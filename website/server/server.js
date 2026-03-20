const {generateBoardPieces, parseMove, checkWin} = require("./gameEngine.js");
const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const cors = require("cors");

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: "http://127.0.0.1:5500",
        methods: ["GET", "POST"]
    }
});

app.use(cors());

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