document.addEventListener('DOMContentLoaded', function () {

  const authForm = document.getElementById('form_login');
  const btnLogin = document.getElementById('btnLogin');

  authForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    btnLogin.disabled = true;
    btnLogin.textContent = 'Connexion en cours…';

    // FormData récupère automatiquement tous les champs du formulaire
    const formData = new FormData(authForm);

    try {
      const response = await fetch('/login', {
        method: 'POST',
        body: formData,  // envoi en form data, pas JSON
      });

      const result = await response.json();

      if (result.success) {
        window.location.href = '/';
      } else {
        alert(result.message);
      }

    } catch (err) {
      alert('Erreur : ' + err.message);
    } finally {
      btnLogin.disabled = false;
      btnLogin.textContent = 'Se connecter';
    }
  });

});

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