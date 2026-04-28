export const socket = io();
let gameId = null;


socket.on("connect", () => {
    fetch('/user').then(res => res.json()).then(data => {socket.emit("set_username", data.username);});
    console.log("Connected:",socket.id);
});

socket.on("waiting", (data) => {
    console.log(data.message);
});

socket.on("game_started", (data) => {
    gameId = data.gameId;
});

socket.on("opponent_disconnect", ({ message }) => {
    alert(message);

    window.location.href = "/";
})

export function startPvP() {
    return fetch('/user').then(res => res.json()).then(data => {socket.emit("start_game", {username: data.username});});
}

export function startAI() {
    return fetch('/user').then(res => res.json()).then(data => {socket.emit("start_ai_game", {username: data.username});});
}

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