document.getElementById("login-form").addEventListener("submit", async function(e) {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    
    const response = await fetch('/login', {
        method: 'POST',
        headers: {'Content-type': 'application/json'},
        body: JSON.stringify({username, password})
    });

    const data = await response.json();

    if (response.ok) {
        window.location.href = '/';
    } else {
        console.error(data.error);
    }
});