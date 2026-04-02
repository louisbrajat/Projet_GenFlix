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

    const btnMesSeries = document.getElementById('btnMesSeries');
  if (btnMesSeries) {
    btnMesSeries.addEventListener('click', function () {
      window.location.href = '/Mes-Series';
    });
  }


  const btnRecommendations = document.getElementById('btnRecommendations');
  if (btnRecommendations) {
    btnRecommendations.addEventListener('click', function () {
      window.location.href = '/recommendations';
    });
  }

 

});