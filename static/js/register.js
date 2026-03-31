document.addEventListener('DOMContentLoaded', function () {

  const registerForm = document.getElementById('registerForm');
  const btnRegister  = document.getElementById('btnRegister');

  // Récupère les valeurs des champs du formulaire
  function getFormData() {
    return {
      pseudo  : document.getElementById('pseudo').value,
      email   : document.getElementById('email').value,
      password: document.getElementById('password').value,
    };
  }

  registerForm.addEventListener('submit', async function (e) {
    e.preventDefault(); // empêche le rechargement de la page

    btnRegister.disabled = true;
    btnRegister.textContent = 'Inscription en cours…';

    const payload = getFormData();

    try {
      const response = await fetch('/register', {
        method : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body   : JSON.stringify(payload),
      });

      const result = await response.json();

      if (result.success) {
        window.location.href = '/'; // redirige vers la page d'accueil après inscription réussie
      } else {
        alert(result.message);           // affiche le message d'erreur
      }

    } catch (err) {
      alert('Erreur : ' + err.message);
    } finally {
      btnRegister.disabled = false;
      btnRegister.textContent = 'Créer un compte';
    }
  });

});