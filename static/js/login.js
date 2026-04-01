document.addEventListener('DOMContentLoaded', function () {

  const formLogin = document.getElementById('formLogin');
  const btnLogin  = document.getElementById('btnLogin');

  formLogin.addEventListener('submit', async function (e) {
    e.preventDefault();

    btnLogin.disabled = true;
    btnLogin.textContent = 'Connexion en cours…';

    const payload = {
      email   : document.getElementById('email').value,
      password: document.getElementById('password').value,
    };

    try {
      const response = await fetch('/login', {
        method : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body   : JSON.stringify(payload),
      });

      const result = await response.json();

      if (result.success) {
        window.location.href = '/Mes-Series';
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