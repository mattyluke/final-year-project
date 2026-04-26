document.getElementById("register-form").addEventListener("submit", async function(e) {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    
    const response = await fetch('/register', {
        method: 'POST',
        headers: {'Content-type': 'application/json'},
        body: JSON.stringify({username, password})
    });

    const data = await response.json();

    if (data.success) {
        window.location.href = '/login';
    } else {
        document.getElementById('error-msg').textContent = "Account is already created.";
    }
});