const {generateBoardPieces, parseMove, checkWin} = require("./gameEngine.js");
const express = require("express");
const mysql = require("mysql2/promise");
const http = require("http");
const { Server } = require("socket.io");
const bcrypt = require('bcrypt');
const path = require('path');
const session = require("express-session");
const MySQLStore = require('express-mysql-session')(session)
const net = require('net');

require('dotenv').config();
const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.json());

const pool = mysql.createPool({
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: 'nonaga_db',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

const sessionStore = new MySQLStore({
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: 'nonaga_db',
    createDatabaseTable: true
})

app.use(session({
    store: sessionStore,
    secret: process.env.SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: false,
        httpOnly: true,
        maxAge: 1000 * 60 * 60
    }
}));

async function initDB() {

    const rootPool = mysql.createPool({
        host: process.env.DB_HOST,
        port: process.env.DB_PORT,
        user: process.env.DB_USER,
        password: process.env.DB_PASSWORD
    });

    await rootPool.execute('CREATE DATABASE IF NOT EXISTS nonaga_db');
    await rootPool.end();
    await pool.execute(`
        CREATE TABLE IF NOT EXISTS users (
        id VARCHAR(255) PRIMARY KEY,
        password TEXT,
        wins INT DEFAULT 0,
        games INT DEFAULT 0
        )
    `)

    await pool.execute(`
        CREATE TABLE IF NOT EXISTS sessions (
        session_id VARCHAR(128) NOT NULL PRIMARY KEY,
        expires INT(11) UNSIGNED NOT NULL,
        data MEDIUMTEXT
        )
    `);
    
    console.log("Database initialised");
}

initDB().catch(err => {
    console.error("Failed to init DB:", err);
    process.exit(1);
});


const PORT = 3000;

const waitingPlayers = [];

const games = {};

io.on("connection", (socket) => {
    console.log("A player connected:",socket.id);

    socket.on("start_game", ({ username }) => {
        socket.username = username;
        waitingPlayers.push(socket);

        if(waitingPlayers.length >= 2) {
            const player1 = waitingPlayers.shift();
            const player2 = waitingPlayers.shift();

            const gameId = `game_${player1.id}_${player2.id}`;

            player1.join(gameId);
            player2.join(gameId);

            games[gameId] = {
                board: generateBoardPieces(),
                players: [player1.id, player2.id],
                isAI: {
                    [player1.id]: false,
                    [player2.id]: false
                },
                currentPlayer: Math.random() < 0.5 ? player1.id : player2.id,
                currentTurn: "r",
                turnCount: 1,
                win: "N"
            };

            const game = games[gameId];

            const player1Color = player1.id === games[gameId].currentPlayer ? "r" : "b";
            const player2Color = player2.id === games[gameId].currentPlayer ? "r" : "b";

            player1.emit("game_started", { gameId , game: games[gameId] , color : player1Color, myUsername : player1.username, opponentUsername : player2.username});
            player2.emit("game_started", { gameId , game: games[gameId] , color : player2Color, myUsername : player2.username, opponentUsername : player1.username});

            if (game.isAI?.[game.currentPlayer]) {
                handleAITurn(gameId);
            }
        } else {
            socket.emit("waiting", { message: "Waiting for another player..." });
        }
    })

    socket.on("start_ai_game", ({ username }) => {
        socket.username = username;
        const aiId = `AI_${socket.id}`;
        const gameId = `game_${socket.id}_AI`;

        socket.join(gameId);

        games[gameId] = {
            board: generateBoardPieces(),
            players: [socket.id, aiId],
            isAI: {
                [socket.id]: false,
                [aiId]: true
            },
            currentPlayer: Math.random() < 0.5 ? socket.id: aiId,
            currentTurn: "r",
            turnCount: 1,
            win: "N"
        };

        const game = games[gameId];

        const playerColor = game.currentPlayer === socket.id ? "r" : "b";
        const aiColor = playerColor === "r" ? "b" : "r";

        socket.emit("game_started", {
            gameId,
            game,
            color: playerColor,
            myUsername: socket.username,
            opponentUsername: "AI"
        });

        if (game.isAI[game.currentPlayer]) {
            handleAITurn(gameId);
        }
    });

    socket.on("make_move", async ({ gameId, move }) => {
        const game = games[gameId];

        if (socket.id !== game.currentPlayer) return;
        if (game.win !== 'N') return;

        game.board = parseMove(game.board, move);
        game.win = checkWin(game.board, game.currentTurn);
        winner = game.win;

        if (game.win !== "N") {
            const winnerSocketId = game.players.find(id => {
                const playerSocket = io.sockets.sockets.get(id);
                return playerSocket && (game.win === 'r' ? playerSocket.id === game.currentPlayer : playerSocket.id !== game.currentPlayer);
            });

            const winnerSocket = io.sockets.sockets.get(winnerSocketId);
            if (winnerSocket && winnerSocket.username){
                await pool.execute('UPDATE users SET wins = wins + 1 WHERE id = ?', [winnerSocket.username]);
            }

            for (const playerId of game.players) {
                const playerSocket = io.sockets.sockets.get(playerId);
                if (playerSocket && playerSocket.username) {
                    await pool.execute('UPDATE users SET games = games + 1 WHERE id = ?', [playerSocket.username]);
                }
            }
            
            io.to(gameId).emit("game_over", {winner});
            delete games[gameId];
            return;
        }


        game.currentPlayer = game.players.find(id => id !== socket.id);
        if (game.currentTurn === "b") game.turnCount++;
        game.currentTurn = game.currentTurn === "r" ? "b" : "r";
        
        io.to(gameId).emit("game_updated", {game: games[gameId]});

        if (game.isAI?.[game.currentPlayer]) {
            handleAITurn(gameId);
        }
    });

    socket.on("disconnect", () => {
        console.log("Player disconnected:", socket.id);

        const waitingIndex = waitingPlayers.findIndex(s => s.id === socket.id);
        if (waitingIndex !== -1) {
            waitingPlayers.splice(waitingIndex, 1);
        }

        for (const gameId in games) {
            const game = games[gameId];

            if (game.players.includes(socket.id)){
                const otherPlayerId = game.players.find(id => id !== socket.id);

                io.to(otherPlayerId).emit("opponent_disconnect", {
                    message: "Your opponent has disconnected. Game ended."
                });

                io.sockets.sockets.get(otherPlayerId)?.leave(gameId);

                delete games[gameId];

                console.log(`Game ${gameId} destroyed due to disconnect`);
                break;
            }
        }
    });
});

// Handling an AI opponent

let aiClient = null;

function getAIMove(boardData) {
    return new Promise((resolve, reject) => {
        const client = new net.Socket();
        let buffer = "";
        let settled = false;

        aiClient = client;

        client.connect(5000, '127.0.0.1', () => {
            client.write(JSON.stringify(boardData) + "\n");
        });

        client.on("data", (data) => {
            buffer += data.toString();
            if (buffer.includes("\n")) {
                const fullMessage = buffer.split("\n")[0].trim();
                settled = true;
                aiClient = null;
                resolve(fullMessage);
                client.destroy();
            }
        });

        client.on("error", (err) => {
            if (!settled) {
                settled = true;
                aiClient = null;
                reject(err);
            }
        });

        client.on("close", () => {
            if (!settled) {
                settled = true;
                aiClient = null;
                reject(new Error("AI connection closed before responding"));
                }
            });
        });
    }

function extractBoardState(game) {
    const coords = [];
    const red_coords = [];
    const black_coords = [];
    let last_moved = null;

    for (const key in game.board) {
        const [x,y,z] = key.split(",").map(Number);

        const q = x;
        const r = y;

        coords.push([q, r]);

        if (game.board[key].just_moved) {
            last_moved = [q, r]
        }

        if (game.board[key].occupation === "r") {
            red_coords.push([q, r]);
        } else if (game.board[key].occupation === 'b') {
            black_coords.push([q, r]);
        }
    }

    console.log({
        coords,
        red_coords,
        black_coords,
        last_moved,
        colour: game.currentTurn === "r" ? "r" : "b"
    });

    return {
        coords,
        red_coords,
        black_coords,
        last_moved,
        colour: game.currentTurn === "r" ? "r" : "b"
    };
}

async function handleAITurn(gameId) {
    const game = games[gameId];
    if (!game) return;

    const data = extractBoardState(game);

    try {
        const move = await getAIMove(data);
        console.log(move);

        game.board = parseMove(game.board, move);
        game.win = checkWin(game.board, game.currentTurn);

        if (game.win !== "N") {
            io.to(gameId).emit("game_over", { winner: game.win });
            delete games[gameId];
            return;
        }

        game.currentPlayer = game.players.find(id => id !== game.currentPlayer);
        if (game.currentTurn === 'b') game.turnCount++;
        game.currentTurn = game.currentTurn === 'r' ? 'b' : 'r';

        io.to(gameId).emit("game_updated", {game});
    } catch (err) {
        console.error("AI Error:", err);
    }
}

// Server listening

server.listen(PORT, () => {
    console.log("Server running on http://localhost:" + PORT);
});

// Get Routes

app.get('/', (req, res) => {
    if (!req.session.user) {
        return res.redirect('/login');
    }
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
})


app.get('/game_pvp', (req, res) => {
    if (!req.session.user) {
        return res.redirect('/login');
    }
    res.sendFile(path.join(__dirname, 'public', 'game_pvp.html'));
})

app.get('/game_AI', (req, res) => {
    if (!req.session.user) {
        return res.redirect('/login');
    }
    res.sendFile(path.join(__dirname, 'public', 'game_ai.html'));
})

app.get('/login', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

app.get('/register', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'register.html'));
});

app.get('/user', async (req, res) => {
    if (!req.session.user) {
        return res.status(401).json({error: "Unauthorised"
        });
    }
    const [rows] = await pool.execute('SELECT id, wins, games FROM users where id = ?', [req.session.user.username]);
    res.json({username: rows[0].id, wins: rows[0].wins, games: rows[0].games})
});

// Post Req

app.post('/register', async (req, res) => {
    const {username, password} = req.body;

    const [rows] = await pool.execute('SELECT id FROM users WHERE id = ?', [username]);

    if (rows[0]) return res.status(400).json({error: "Username already taken"});

    const hash = await bcrypt.hash(password, 12);
    await pool.execute('INSERT INTO users (id, password) VALUES (?, ?)', [username, hash])

    res.json({success: true});
});

app.post('/login', async (req, res) => {
    const {username, password} = req.body;

    const [rows] = await pool.execute('SELECT id, password FROM users WHERE id = ?', [username]);
    const existing = rows[0]

    if (!existing) return res.status(400).json({error: "Username or password does not match"})

        const match = await bcrypt.compare(password, existing.password);
        if (!match) return res.status(400).json({error: "Username or password does not match"})

    req.session.user = {username};
    res.json({success: true});
});

app.post('/logout', async (req, res) => {
    req.session.destroy(err => {
        if (err) return res.status(500).json({error: "Logout failed"});
        res.clearCookie('connect.sid');
        res.redirect('/login');
    });
});

app.use(express.static(path.join(__dirname, 'public')));