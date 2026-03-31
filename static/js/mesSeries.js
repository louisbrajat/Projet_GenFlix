const SeriesConteneur = document.getElementById("Resulat-Series");

 SeriesConteneur.addEventListener('click', (event) => {
    if (event.target.classList.contains('butAjout')) {
      const idSerie = event.target.dataset.idKey;
      const nameS = event.target.dataset.title;
      console.log(idSerie,nameS)
      AddSerie(idSerie,nameS)
      event.target.style.display = 'none';
     
    }
}) 







function AddSerie(idSerie,nameS) {
    const jsonfilm = {'id':idSerie,'name':nameS}
    fetch(`/api/AjouterSerie`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jsonfilm)
    }).then(response => response.json()).then(data => {
            return data
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
                    <button class="butAjout" id='addSerie' data-title='${serie.name}' data-id-key='${serie.id}'>Ajouter la Serie </button>
                </div>
                <button class="butSupprimer" data-id-key='${serie.id}' style="display: none;>
                Enlever la Serie
                </button>
            </div> `
        conteneur.innerHTML += template;
    })
}



