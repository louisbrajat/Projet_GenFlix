const SeriesConteneur = document.getElementById("Resulat-Series");

 SeriesConteneur.addEventListener('click', (event) => {
    if (event.target.classList.contains('butAjout')) {
      const idSerie = event.target.dataset.idKey;
      const nameS = event.target.dataset.title;
      const imgS = event.target.dataset.img;
      AddSerie(idSerie,nameS,imgS)
      event.target.closest('.film').style.display = 'none';
     
    }
}) 

function AddSerie(idSerie,nameS,imgS) {
    console.log('hey')
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
                if (film) {
                    film.remove(); 
                }
            }).catch(error => console.error("Error", error));
})
}

const form2 = document.querySelector('#retour')    
form2.addEventListener('submit', function (event) {
    window.location.href ="/Mes-Series";
})

const form = document.querySelector('#ChercherForm')    
form.addEventListener('submit', function (event) {
    event.preventDefault();
    const text = Object.fromEntries(new FormData(form))
    RechercherSeries(text['Chercher'])
})


function RechercherSeries(text) {
    if (text === 'LENVRS') {
        window.location.href = "https://vinkyn.github.io/D17/";
    }
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

                    } else {
                        listSerie.push(d);
                    }
                });
                console.log(listSerie)
                showShows(listSerie,text)
                document.getElementById('MS').style.display = 'block';
            })
            console.log("Mes séries en DB :", mesSeries);
        })    
}

function showShows(show,text) {
    const MesSeries = document.getElementById("MesSeries");
    MesSeries.style.display="none"
    const conteneur = document.getElementById("Resulat-Series");
    conteneur.innerHTML = `<h3>Résultats de Recherche : ${text} </h3>
                            <div class="ligneverte"></div>
                           <div class="listeSerie" id="listeResultats"></div>
                           `;
    
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


const cards = document.querySelectorAll('.notation');

cards.forEach(card => {

  const starsContainer = card.querySelector('.stars');
  const serieId = starsContainer.dataset.star;


  const stars = card.querySelectorAll('.star');
  

  const initialNote = parseInt(starsContainer.dataset.note);

  if (initialNote > 0) {
    updateStars(stars, initialNote, 'selected');
  }

  let currentRating = initialNote;

  stars.forEach(star => {
    star.addEventListener('mouseenter', () => {
      const val = parseInt(star.dataset.value);
      updateStars(stars, val, 'hovered');
    });

    star.addEventListener('click', () => {
      currentRating = parseInt(star.dataset.value);
      updateStars(stars, currentRating, 'selected');
      MajAjoutNote(currentRating,serieId)
    });
  });
});


function MajAjoutNote(currentRating,serieId) {
    const jsonfilm = {'note':currentRating,'ids':serieId}
    fetch(`/api/Note`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jsonfilm)
    }).then(response => response.json()).then(data => {
            return data
    })
}

function updateStars(stars, limit, className) {
  stars.forEach(s => {
    const starValue = parseInt(s.dataset.value);

    if(starValue <= limit){
        s.classList.add(className);
    }else{
        s.classList.remove(className);
    }
  });
}

