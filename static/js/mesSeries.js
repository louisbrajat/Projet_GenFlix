const SeriesConteneur = document.getElementById("Resulat-Series");

 SeriesConteneur.addEventListener('click', (event) => {
    if (event.target.classList.contains('butAjout')) {
      const idSerie = event.target.dataset.idKey;
      const nameS = event.target.dataset.title;
      const imgS = event.target.dataset.img;
      console.log(idSerie,nameS,imgS)
      AddSerie(idSerie,nameS,imgS)
      event.target.style.display = 'none';
     
    }
}) 

function AddSerie(idSerie,nameS,imgS) {
    const jsonfilm = {'id':idSerie,'name':nameS,'img':imgS}
    fetch(`/api/AjouterSerie`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jsonfilm)
    }).then(response => response.json()).then(data => {
            return data
    })
}

//const boutonsSupprimer = document.querySelectorAll('.butSupprimer');

for (const btn of document.querySelectorAll('.butSupprimer')) {
 btn.addEventListener('click', async () => {
 const keyId = btn.dataset.idKey;

 const film = btn.closest('.film');
 fetch(`/api/RemoveSerie/${keyId}`, {method:"DELETE"})
    .then(response=> {
        if (response.ok) {
                    return response.json();
                }
                throw new Error('Erreur lors de la suppression');
    }).then(data => {
                console.log("Réponse du serveur:", data);
                // Si le serveur confirme le succès, on retire la carte du HTML
                if (film) {
                    film.remove(); 
                }
            }).catch(error => console.error("Error", error));
})
}

const form = document.querySelector('#ChercherForm')    
form.addEventListener('submit', function (event) {
    event.preventDefault();
    const text = Object.fromEntries(new FormData(form))
    RechercherSeries(text['Chercher'])
})


function RechercherSeries(text) {
    fetch(`/api/GetSerieUser`)
        .then(response => response.json())
        .then(mesSeries => {
            fetch(`https://api.tvmaze.com/search/shows?q=${text}`)
            .then(response => response.json())
            .then(data => {
                const serieBDID = mesSeries.map(s => s.serie_idtvmaze);
                let listSerie = []
                data.forEach(d => {
                    if (serieBDID.includes(d.show.id)) {
                        console.log("On ignore le doublon :", d.show.name);
                    } else {
                        listSerie.push(d);
                    }
                });
                console.log(listSerie)
                showShows(listSerie,text)
            })
            console.log("Mes séries en DB :", mesSeries);
        })


    
}

function showShows(show,text) {
    const MesSeries = document.getElementById("MesSeries");
    MesSeries.style.display="none"
    const conteneur = document.getElementById("Resulat-Series");
    conteneur.innerHTML = `<h3>Résultats de recherche : ${text} </h3>
                           <div class="listeSerie" id="listeResultats"></div>`;
    
    const conteneur2 = document.getElementById("listeResultats");
    let template = ""
    show.forEach(s => {
        serie = s['show']
        if (serie.image && serie.image.medium) {
            img= serie.image.medium
        }else{
             img = "https://www.pngegg.com/fr/png-bmmcf"
        }
        template += `
           <div class="film">
                <div class="contenant">
                    <div class="affiche">   
                        <img class="img_film" src="${img}">
                    </div>
                    <div class="titreFilm">
                        <p>${serie.name}</p>
                    </div>
                    <div class="bottomFilm">
                        <button class="butAjout" data-img="${img}" data-title="${serie.name}" data-id-key="${serie.id}">Ajouter</button>
                    </div>
                </div>
            </div>`;
        conteneur2.innerHTML = template;
    })
}



