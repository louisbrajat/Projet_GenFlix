import json
import requests
import os
from dotenv import load_dotenv
from flask import Flask, render_template, session, redirect, url_for, request, jsonify, g
from google import genai
from google.genai import types
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from models import User
from routes import auth, api, login_required

from flask_session import Session
from models import db

load_dotenv()

os.getenv["GEMINI_API_KEY"]

app = Flask(__name__)

app.config["SECRET_KEY"] = "dev-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Genflix.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_SQLALCHEMY"] = db

sess = Session()

app.register_blueprint(auth)
app.register_blueprint(api)


@app.route('/', methods=['GET'])
def home():
    if "user_id" in session:
        return redirect(url_for('mes_series'))
    return render_template('home.html')


@app.route('/Mes-Series', methods=['GET'])
@login_required
def mes_series():
    if "user_id" not in session:
        return redirect(url_for('auth.login'))
    return render_template('Mes-Series.html', user=g.user, page = "mes_series")



@app.route('/recommendations', methods=['GET'])
@login_required
def recommendations():
    if "user_id" not in session:
        return redirect(url_for('auth.login'))
    
    #geminireponse = gemini_recommendations()

    geminireponse = [
    {
        'name': 'The Mandalorian',
        'explication': "Réalisation impeccable, visuels époustouflants et rythme d'action soutenu.",
        'resume': "Un chasseur de primes solitaire protège un mystérieux enfant dans une galaxie lointaine.",
        'repas': ["Macarons bleus", "Bouillon d'os", "Rôti de Krayt"],
        'ref': ["Westerns de Sergio Leone", "Lone Wolf and Cub", "Star Wars original"]
    },
    {
        'name': 'Stranger Things',
        'explication': "Esthétique des années 80 et suspense parfaitement dosé.",
        'resume': "Un groupe d'amis découvre des forces surnaturelles et des secrets gouvernementaux en 1983.",
        'repas': ["Gaufres Eggo", "Pizzas Surfer Boy", "Bonbons Reese's Pieces"],
        'ref': ["Steven Spielberg", "Stephen King", "Donjons & Dragons"]
    },
    {
        'name': 'Ted Lasso',
        'explication': "Rythme comique parfait, dialogues vifs et optimisme contagieux.",
        'resume': "Un entraîneur de football américain dirige une équipe de soccer anglaise.",
        'repas': ["Biscuits Shortbread", "Thé", "Fish and Chips"],
        'ref': ["Culture UK vs USA", "Psychologie positive", "The Office"]
    },
    {
        'name': 'Lupin',
        'explication': "Réalisation stylée et dynamique avec un rythme d'enquête haletant.",
        'resume': "Un gentleman cambrioleur s'inspire d'Arsène Lupin pour venger son père.",
        'repas': "Cupcakes multicolores Barbe à papa Barres de la Horde",
        'ref': "Maurice Leblanc Sherlock Holmes Braquages à la française"
    },
    {
        'name': "The Queen's Gambit",
        'explication': "Cinématographie sophistiquée et tension dramatique autour des échecs.",
        'resume': "Une orpheline prodige des échecs affronte ses démons et les meilleurs joueurs mondiaux.",
        'repas': "Cupcakes multicolores Barbe à papa Barres de la Horde",
        'ref': "Maurice Leblanc Sherlock Holmes Braquages à la française"
    },
    {
        'name': 'Gravity Falls',
        'explication': "Animation expressive, humour et mystères captivants pour tous les âges.",
        'resume': "Deux jumeaux découvrent les secrets paranormaux d'une ville mystérieuse l'été.",
        'repas': "Cupcakes multicolores Barbe à papa Barres de la Horde",
        'ref': "Maurice Leblanc Sherlock Holmes Braquages à la française"
    },
    {
        'name': 'Only Murders in the Building',
        'explication': "Mise en scène créative utilisant l'espace new-yorkais et humour noir.",
        'resume': "Trois voisins passionnés de true crime enquêtent sur un meurtre dans leur immeuble.",
        'repas': "Cupcakes multicolores Barbe à papa Barres de la Horde",
        'ref': "Maurice Leblanc Sherlock Holmes Braquages à la française"
    },
    {
        'name': 'She-Ra and the Princesses of Power',
        'explication': "Animation moderne, colorée et scènes de combat fluides.",
        'resume': "Adora devient la guerrière magique She-Ra pour mener une rébellion.",
        'repas': "Cupcakes multicolores Barbe à papa Barres de la Horde",
        'ref': "Maurice Leblanc Sherlock Holmes Braquages à la française"
    }
]
    series = []
    for serie in geminireponse:
        name = serie['name']
        response = requests.get(f"https://api.tvmaze.com/singlesearch/shows?q={name}")
        if response.status_code == 200:
                data = response.json()
                if (data.get('image', {}) and data.get('image', {}).get('medium')):
                    img= data.get('image', {}).get('medium')
                    imggros = data.get('image', {}).get('original')
                else:
                    img = 'https://www.pngegg.com/fr/png-bmmcf'
                    imggros= 'https://www.pngegg.com/fr/png-bmmcf'

                series.append({'idserimaze':data.get('id'),
                               'name':data.get('name'),
                               'img':img,
                               'imgbig':imggros,
                               'genres':data.get('genres', []),
                               'resume': data.get('summary'),
                               'note': data.get('rating', {}).get('average'),
                               'explication' : serie['explication'],
                               'donnerenvi':serie['resume'],
                               'repas':serie['repas'],
                               'ref':serie['ref']
                               })
    return render_template("recommendations.html", user=g.user,recommendations=series,page = "recommandations")


def gemini_recommendations():
    series_list = g.user.serie
    if not series_list:
        return []

    formatted_list = []
    for s in series_list:
        ligne = f"{s.name}: {s.note}/5"
        formatted_list.append(ligne)

    response_schema = types.Schema(
        type=types.Type.ARRAY,
        items=types.Schema(
            type=types.Type.OBJECT,
            properties={
                    "name": types.Schema(type=types.Type.STRING),
                    "explication": types.Schema(type=types.Type.STRING),
                    "resume": types.Schema(type=types.Type.STRING),
                    "repas": types.Schema(type=types.Type.STRING),
                    "ref": types.Schema(type=types.Type.STRING)
            },
            required=["name", "explication", "resume","repas","ref"]
        )
    )

    try:
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        series_list_str = "\n".join(formatted_list)

        full_prompt = f"""
Rôle : Tu es une IA experte en analyse cinéphile et critique de séries. Ton objectif est de réaliser un profilage "ADN" des goûts de l'utilisateur pour recommander 8 séries parfaites.

Données d'entrée : {series_list_str}

Méthodologie d'analyse :

Analyse des Succès (Note 5/5) : Décompose les piliers : style de réalisation (ex: montage nerveux vs contemplatif), identité sonore, thématiques récurrentes, et types de personnages.

Analyse des Appréciations (Note 3-4/5) : Identifie les genres et acteurs qui plaisent sans être essentiels.

Filtres d'exclusion (Note ≤ 2/5) : Identifie les "Red Flags" techniques ou narratifs à bannir absolument.

Contraintes de rédaction :

Explication (Max 50 mots) : Analyse technique poussée. Pourquoi cette recommandation matche-t-elle avec l'ADN des notes 5/5 (rythme, photographie, écriture) ?

Pitch (Max 50 mots) : Accroche narrative percutante et immersive.

Repas : Suggère un plat ou un encas spécifique qui complète l'ambiance de la série.

Référence : Monte le curseur sur le côté "clin d'œil absurde" et rigolo. L'idée est que l'utilisateur se dise : "Mais pourquoi il me parle de ça ?" au début, et qu'il rigole tout seul devant sa télé quand l'élément apparaît enfin.

"""

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.7,
            )
        )
        return json.loads(response.text)

    except Exception as e:
        print(f"ERREUR GEMINI : {e}")
        return []


db.init_app(app)
sess.init_app(app)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)