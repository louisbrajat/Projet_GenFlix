const SeriesConteneur = document.getElementById("Resulat-Series");

 SeriesConteneur.addEventListener('click', (event) => {
    if (event.target.classList.contains('butAjout')) {
      const idSerie = event.target.dataset.idKey;
      console.log(idSerie)
      AddSerie(idSerie)
    }
}) 





function AddSerie(idSerie) {
    const jsonfilm = {'id':idSerie}
    fetch(`/api/AjouterSerie`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jsonfilm)
    }).then(response => response.json()).then(data => {
            console.log(data)
    })
}




const form = document.querySelector('#ChercherForm')    
form.addEventListener('submit', function (event) {
    event.preventDefault();
    const text = Object.fromEntries(new FormData(form))
    RechercherSeries(text['Chercher'])
})


function RechercherSeries(text) {
    fetch(`https://api.tvmaze.com/search/shows?q=${text}`)
    .then(response => response.json())
    .then(data => {
        showShows(data)
    })
}

function showShows(show) {
    const conteneur = document.getElementById("Resulat-Series");
    conteneur.innerHTML = "";
    show.forEach(s => {
        serie = s['show']
        if (serie.image && serie.image.medium) {
            img= serie.image.medium
        }else{
             img = "https://www.pngegg.com/fr/png-bmmcf"
        }
        titre = serie.name
        const template = `
            <div class="film">
                <div class="affiche">   
                    <img class="img_film" src=" ${img}">
                </div>
                <div class="titreFilm">
                    <p>${serie.name}</p>
                </div>
                <div class="bottomFilm">
                    <button class="butAjout" id='addSerie' data-id-key='${serie.id}'>Ajouter la Serie </button>
                </div>
            </div> `
        conteneur.innerHTML += template;
    })
}



