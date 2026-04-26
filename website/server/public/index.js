async function getData() {
    const res = await fetch('/user');
    const data = await res.json();
    document.getElementById('username').textContent = "Hello, " + data.username;
    document.getElementById('wins').textContent = `Wins: ${data.wins}`;
    document.getElementById('games').textContent = `Total Games: ${data.games}`;
    document.getElementById('win-rate').textContent = `Win rate: ${data.games == 0 ? 0 : data.wins/data.games}`;
};

getData();