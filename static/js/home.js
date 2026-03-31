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


document.addEventListener('DOMContentLoaded', function () {

  const btnConnexion = document.getElementById('btnConnexion');

  btnConnexion.addEventListener('click', function () {
    window.location.href = '/login';
  });

});

document.addEventListener('DOMContentLoaded', function () {

  const btnDeconnexion = document.getElementById('btnDeconnexion');

  btnDeconnexion.addEventListener('click', function () {
    window.location.href = '/logout';
  });

});