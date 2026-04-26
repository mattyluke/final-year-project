async function getUser() {
    const res = await fetch('/user');
    const data = await res.json();
    document.getElementById('username').textContent = "Hello, " + data.username;
};

getUser();