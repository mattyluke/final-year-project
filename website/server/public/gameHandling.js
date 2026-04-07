const socket = io("http://localhost:3000");
let gameId = null;


socket.on("connect", () => {
    console.log("Connected:",socket.id);
    socket.emit("start_game");
});

socket.on("waiting", (data) => {
    console.log(data.message);
});

socket.on("game_started", (data) => {
    gameId = data.gameId;
});

export function sendMove(move) {
    socket.emit("make_move", {gameId, move});
};

export function onGameStarted( callback ) {
    socket.on("game_started", callback);
};

export function onGameUpdated( callback ) {
    socket.on("game_updated", callback);
};

export function onGameOver(callback) {
    socket.on("game_over", callback);
}

export function sendWin(move, occupation){
    socket.emit("send_win", {gameId, move, occupation})
}