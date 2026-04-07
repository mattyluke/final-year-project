const {generateBoardPieces, parseMove, checkWin} = require("./gameEngine.js");
const express = require("express");
const Database = require("better-sqlite3");
const http = require("http");
const { Server } = require("socket.io");
const bcrypt = require('bcrypt');
const path = require('path');

const app = express();
const db = new Database('./nonaga.db')
const server = http.createServer(app);
const io = new Server(server);

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

db.exec('CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, password TEXT, wins INT, games INT)');

const PORT = 3000;

const waitingPlayers = [];

const games = {};

io.on("connection", (socket) => {
    console.log("A player connected:",socket.id);

    socket.on("start_game", () => {
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
                currentPlayer: Math.random() < 0.5 ? player1.id : player2.id,
                currentTurn: "r",
                turnCount: 1,
                win: "N"
            };

            const player1Color = player1.id === games[gameId].currentPlayer ? "r" : "b";
            const player2Color = player2.id === games[gameId].currentPlayer ? "r" : "b";

            player1.emit("game_started", { gameId , game: games[gameId] , color : player1Color });
            player2.emit("game_started", { gameId , game: games[gameId] , color : player2Color});
        } else {
            socket.emit("waiting", { message: "Waiting for another player..." });
        }
    })

    socket.on("make_move", ({ gameId, move }) => {
        const game = games[gameId];

        if (socket.id !== game.currentPlayer) return;

        game.board = parseMove(game.board, move);
        game.win = "N"
        game.currentPlayer = game.players.find(id => id !== socket.id);
        if (game.currentTurn === "b") game.turnCount++;
        game.currentTurn = game.currentTurn === "r" ? "b" : "r";
        
        io.to(gameId).emit("game_updated", {game: games[gameId]});
    });

    socket.on("disconnect", () => {
        console.log("Player disconnected:", socket.id);
    });

    socket.on("send_win", ({gameId, move, occupation}) => {
        const game = games[gameId];
        game.win = occupation;
        game.board = parseMove(game.board, move);
        io.to(gameId).emit("game_over", {winner: occupation});

        game.players.forEach(playerId => {
            const playerSocket = io.sockets.sockets.get(playerId);
            if (playerSocket) playerSocket.disconnect();
        });
    })
});

server.listen(PORT, () => {
    console.log("Server running on http://localhost:" + PORT);
});

// Get Routes

app.get('/login', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

app.get('/register', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'register.html'));
});

// Post Req

app.post('/register', async (req, res) => {
    const {username, password} = req.body;

    const existing = db.prepare('SELECT id FROM users WHERE id = ?').get(username);
    if (existing) return res.status(400).json({error: "Username already taken"});

    const hash = await bcrypt.hash(password, 12);
    db.prepare('INSERT INTO users (id, password) VALUES (?, ?)').run(username, hash);

    res.json({success: true});
});

app.post('/login', async (req, res) => {
    const {username, password} = req.body;

    const existing = db.prepare('SELECT id, password FROM users WHERE id = ?').get(username);
    if(!existing) return res.status(400).json({error: "Username or password does not match"});

    const match = await bcrypt.compare(password, existing.password);
    if (!match) return res.status(400).json({error: "Username or password does not match"});

    res.json({success: true});
});