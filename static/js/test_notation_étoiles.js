const card      = document.getElementById('card');
const mainBtn   = document.getElementById('mainBtn');
const stars     = document.querySelectorAll('.star');
const noteLabel = document.getElementById('noteLabel');
const resetBtn  = document.getElementById('resetBtn');
const status    = document.getElementById('status');

let noteActuelle = 0;

// Clic bouton -> retournement
mainBtn.addEventListener('click', () => {
  card.classList.add('flipped');
});

// Retour
resetBtn.addEventListener('click', () => {
  card.classList.remove('flipped');
});

// Hover sur les étoiles
stars.forEach(star => {
  star.addEventListener('mouseenter', () => {
    const val = parseInt(star.dataset.value);
    stars.forEach(s => {
      s.classList.toggle('hovered', parseInt(s.dataset.value) <= val);
    });
  });

  star.addEventListener('mouseleave', () => {
    stars.forEach(s => s.classList.remove('hovered'));
  });

  // Clic : enregistre la note
  star.addEventListener('click', () => {
    noteActuelle = parseInt(star.dataset.value);

    stars.forEach(s => {
      s.classList.toggle('selected', parseInt(s.dataset.value) <= noteActuelle);
    });

    noteLabel.textContent = noteActuelle + ' / 5';
    status.textContent    = 'Note enregistrée : ' + noteActuelle + ' étoile' + (noteActuelle > 1 ? 's' : '');

    envoyerNote(noteActuelle);

    // Retournement automatique après 700ms
    setTimeout(() => card.classList.remove('flipped'), 700);
  });
});

function envoyerNote(note) {
  console.log('Note envoyée :', note);
  // fetch('/note/serie_id', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify({ note: note })
  // }).then(r => r.json()).then(data => console.log(data));
}