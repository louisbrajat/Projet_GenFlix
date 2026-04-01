document.addEventListener('DOMContentLoaded', function () {

  const btnConnexion = document.getElementById('btnConnexion');
  if (btnConnexion) {
    btnConnexion.addEventListener('click', function () {
      window.location.href = '/login';
    });
  }

  const btnDeconnexion = document.getElementById('btnDeconnexion');
  if (btnDeconnexion) {
    btnDeconnexion.addEventListener('click', function () {
      window.location.href = '/logout';
    });
  }

});