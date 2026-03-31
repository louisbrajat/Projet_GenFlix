const titles = ["Bienvenue", "Bienvenido", "Welcome", "ようこそ"];
let index = 0;

const title = document.getElementById("welcome");
const welcomeBox = document.getElementById("welcome-box");

window.addEventListener("load", () => {
    welcomeBox.classList.add("show");
});

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