const titles = [
    "Bienvenue",
    "Bienvenido",
    "مرحبًا",
    "Welcome"
];

let index = 0;
const title = document.querySelector(".welcome-text h1");

setInterval(() => {
    index = (index + 1) % titles.length;
    title.textContent = titles[index];
}, 2500);