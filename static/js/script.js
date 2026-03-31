const messages = [
    "Bienvenue",
    "Welcome",
    "Salut",
    "Salam"
];

let i = 0;

const welcome = document.getElementById("welcome");

setInterval(() => {
    i = (i + 1) % messages.length;
    welcome.textContent = messages[i];
}, 3000);