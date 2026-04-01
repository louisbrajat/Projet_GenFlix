/*function envoyerNote(serieId, note, starsDiv) {
    // Colorie les étoiles
    starsDiv.querySelectorAll('.star').forEach(s => {
        s.style.color = s.dataset.value <= note ? 'gold' : 'grey';
    });

    fetch(`/note/${serieId}`, {
        method : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body   : JSON.stringify({ note: note }),
    })
    .then(response => response.json())
    .then(data => console.log(data));
}

const SeriesConteneur = document.getElementById("Resulat-Series");

SeriesConteneur.addEventListener('click', (event) => {
    if (event.target.classList.contains('butAjout')) {
        const idSerie = event.target.dataset.idKey;
        AddSerie(idSerie, event.target);  // ← ajoute event.target en paramètre
    }

    // ← ajoute ce bloc
    if (event.target.classList.contains('star')) {
        const note    = event.target.dataset.value;
        const serieId = event.target.closest('.stars').dataset.serie;
        envoyerNote(serieId, note, event.target.closest('.stars'));
    }
});

function AddSerie(idSerie, bouton) {
    const jsonfilm = { 'id': idSerie };
    fetch(`/api/AjouterSerie`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jsonfilm)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.success) {
            bouton.closest('.bottomFilm').innerHTML = `
                <div class="stars" data-serie="${idSerie}">
                    <span class="star" data-value="1">★</span>
                    <span class="star" data-value="2">★</span>
                    <span class="star" data-value="3">★</span>
                    <span class="star" data-value="4">★</span>
                    <span class="star" data-value="5">★</span>
                </div>
            `;
        }
    });
}*/