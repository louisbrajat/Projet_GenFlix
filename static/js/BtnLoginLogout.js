
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