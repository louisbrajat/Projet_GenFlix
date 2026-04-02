from flask import Blueprint, Flask, render_template, session, redirect, url_for, request, jsonify, g

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from models import User, Serie, db

from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

import json
import os
import requests
from google import genai
from google.genai import types


auth = Blueprint('auth', __name__)
api = Blueprint("api", __name__)


def login_required(f):
    """
        session uniquement

        grace à la variable g.user, on peut accéder à l'utilisateur connecté
        dans les fonctions de route protégées par ce décorateur
    """
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return render_template("login.html")

        user = User.get_by_username(session["user"])
        if user is None:
            session.clear()
            return render_template("login.html")

        g.user = user
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json(force=True, silent=True)
        print("DATA REÇUE :", data)

        if data is None:
            return jsonify({'success': False, 'message': 'Données manquantes'})

        email = data['email']
        password = data['password']

        user = User.query.filter_by(Email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session['user'] = user.Pseudo
            session['user_id'] = user.id
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'E-mail ou mot de passe incorrect'})

    return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json(force=True, silent=True)
        pseudo = data['pseudo']
        email = data['email']
        password = data['password']

        user_existant = User.query.filter_by(Pseudo=pseudo).first()
        email_existant = User.query.filter_by(Email=email).first()
        print("USER EXISTANT :", user_existant)
        print("EMAIL EXISTANT :", email_existant)

        if user_existant:
            return jsonify({'success': False, 'message': 'Ce pseudo est déjà pris'})
        if email_existant:
            return jsonify({'success': False, 'message': 'Cet email est déjà utilisé'})

        password_hash = generate_password_hash(password)
        nouvel_utilisateur = User(
            Pseudo=pseudo,
            Email=email,
            password_hash=password_hash
        )
        db.session.add(nouvel_utilisateur)
        db.session.commit()

        session['user'] = pseudo
        session['user_id'] = nouvel_utilisateur.id

        return jsonify({'success': True})

    return render_template('register.html')


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))



@api.route("/api/AjouterSerie", methods=["POST"])
def ADDSerie():
    data = request.get_json()
    idS = int(data['id'])
    nameS = data['name']
    imgurl = data['img']
    serie = Serie(idtvmaze=idS, name=nameS, img=imgurl, user_id=session['user_id'])
    db.session.add(serie)
    db.session.commit()
    return jsonify({"status": "success", "received": data}), 200


@api.route("/api/RemoveSerie/<int:key_id>", methods=["DELETE"])
def Remove(key_id):
    SerieR = Serie.query.filter_by(user_id=session['user_id'], idtvmaze=key_id).first()
    if SerieR:
        db.session.delete(SerieR)
        db.session.commit()
        return jsonify({"status": "success", "message": "Série supprimée"}), 200
    else:
        return jsonify({"status": "error", "message": "Série non trouvée"}), 404


@api.route("/api/GetSerieUser", methods=["GET"])
def GetAllUser():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    Liste_Serie = Serie.get_All_Serie(user_id=user_id)
    liste_finale = []
    for s in Liste_Serie:
        liste_finale.append(s.to_dict())
    return jsonify(liste_finale)


@api.route("/api/Note", methods=["POST"])
def AddMajNote():
    data = request.get_json()
    user_id = session.get('user_id')
    noteS = data['note']
    idS = data['ids']
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    SerieNote = Serie.query.filter_by(user_id=session['user_id'], idtvmaze=idS).first()
    SerieNote.note = noteS
    db.session.commit()

    return jsonify({"status": "success", "received": data}), 200


def get_tvmaze_image(show_name):
    try:
        response = requests.get(
            "https://api.tvmaze.com/search/shows",
            params={"q": show_name},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()

        if not data:
            return ""

        first_show = data[0].get("show", {})
        image = first_show.get("image")

        if image:
            return image.get("original") or image.get("medium") or ""

        return ""
    except Exception as e:
        print("ERREUR IMAGE TVMAZE :", e)
        return ""


def enrich_with_images(recommendations):
    enriched = []
    for reco in recommendations:
        reco_copy = dict(reco)
        reco_copy["image"] = get_tvmaze_image(reco_copy.get("nom_de_serie", ""))
        enriched.append(reco_copy)
    return enriched


def local_fallback_recommendations(genres, moods, paces, styles, popularity, formats, extra):
    genre_map = {
        "thriller": [
            ("Mindhunter", "Thriller", "Très bon choix si tu veux une tension psychologique constante.", "Deux agents du FBI étudient les tueurs en série pour comprendre leur fonctionnement."),
            ("Severance", "Thriller", "Ambiance étrange, élégante et très prenante.", "Des employés subissent une séparation radicale entre vie pro et vie perso."),
            ("Dark", "Thriller", "Parfait si tu aimes les mystères complexes et l’ambiance sombre.", "Des disparitions révèlent un secret énorme lié au temps.")
        ],
        "drame": [
            ("The Crown", "Drame", "Idéal pour un drame soigné, intense et prestigieux.", "Une plongée dans la monarchie britannique et ses tensions internes."),
            ("This Is Us", "Drame", "Très bon si tu cherches quelque chose d’émouvant et humain.", "L’histoire croisée d’une famille sur plusieurs périodes."),
            ("Maid", "Drame", "Mini-série forte, adulte et touchante.", "Une jeune mère tente de reconstruire sa vie après une relation toxique.")
        ],
        "comédie": [
            ("The Good Place", "Comédie", "Parfait pour quelque chose de léger, malin et addictif.", "Une femme se retrouve dans l’au-delà et tente de devenir meilleure."),
            ("Brooklyn Nine-Nine", "Comédie", "Très efficace si tu veux une série drôle et facile à binge-watcher.", "Le quotidien décalé d’un commissariat new-yorkais."),
            ("Ted Lasso", "Comédie", "Une recommandation chaleureuse et feel-good.", "Un coach américain débarque dans le football anglais.")
        ],
        "romance": [
            ("Normal People", "Romance", "Très bon choix pour une romance intense et adulte.", "Une relation complexe se construit entre deux jeunes sur plusieurs années."),
            ("Bridgerton", "Romance", "Parfait si tu veux une romance élégante et populaire.", "Amours, scandales et jeux sociaux dans l’aristocratie londonienne."),
            ("One Day", "Romance", "Émouvant et marquant, avec une vraie sensibilité.", "Deux destins restent liés pendant des années.")
        ],
        "science-fiction": [
            ("Black Mirror", "Science-fiction", "Idéal si tu veux une sci-fi adulte, moderne et marquante.", "Chaque épisode explore une dérive possible liée à la technologie."),
            ("Silo", "Science-fiction", "Très bon si tu cherches un univers immersif et mystérieux.", "Une société entière vit enfermée dans un immense silo."),
            ("The Expanse", "Science-fiction", "Excellente option pour un univers riche et ambitieux.", "Une intrigue politique et spatiale à grande échelle.")
        ],
        "fantasy": [
            ("House of the Dragon", "Fantasy", "Très fort si tu veux du pouvoir, des tensions et un grand univers.", "Une guerre de succession secoue une dynastie de dragons."),
            ("Shadow and Bone", "Fantasy", "Accessible, visuel et immersif.", "Une jeune femme découvre un pouvoir rare dans un monde divisé."),
            ("The Witcher", "Fantasy", "Bon choix pour une fantasy sombre et populaire.", "Un chasseur de monstres évolue dans un monde brutal.")
        ],
        "mystère": [
            ("Sharp Objects", "Mystère", "Très bon si tu veux une ambiance sombre et troublante.", "Une journaliste retourne dans sa ville pour couvrir des meurtres."),
            ("Mare of Easttown", "Mystère", "Parfait pour une enquête humaine et prenante.", "Une inspectrice enquête dans une petite ville rongée par les secrets."),
            ("The Sinner", "Mystère", "Bonne option si tu aimes les affaires psychologiques.", "Chaque saison explore un crime sous un angle inhabituel.")
        ],
        "crime": [
            ("Narcos", "Crime", "Très efficace si tu veux du rythme, de la tension et de la violence.", "L’ascension et la chute des grands cartels de drogue."),
            ("Ozark", "Crime", "Très bon choix pour un crime sombre et addictif.", "Un conseiller financier plonge sa famille dans le blanchiment d’argent."),
            ("Top Boy", "Crime", "Plus brut, plus urbain et très prenant.", "Des rivalités s’installent dans les quartiers de Londres.")
        ],
        "action": [
            ("Reacher", "Action", "Parfait pour quelque chose de direct, efficace et tendu.", "Un ancien militaire redoutable se retrouve au cœur d’un complot."),
            ("24", "Action", "Très bon si tu veux du rythme rapide et de la tension.", "Chaque saison suit une journée contre une menace majeure."),
            ("The Night Agent", "Action", "Populaire, nerveux et facile à binge-watcher.", "Un agent se retrouve mêlé à une conspiration gouvernementale.")
        ],
        "psychologique": [
            ("You", "Psychologique", "Très bon si tu veux quelque chose d’obsessionnel et troublant.", "Un homme dangereux rationalise ses obsessions amoureuses."),
            ("Mr. Robot", "Psychologique", "Parfait pour une série adulte, sombre et cérébrale.", "Un hacker instable veut faire tomber un système géant."),
            ("Behind Her Eyes", "Psychologique", "Courte, addictive et surprenante.", "Une relation étrange glisse vers quelque chose de dérangeant.")
        ],
        "historique": [
            ("Chernobyl", "Historique", "Mini-série puissante, tendue et marquante.", "Le récit de la catastrophe nucléaire et de ses conséquences."),
            ("Peaky Blinders", "Historique", "Très bon pour un style fort et une ambiance sombre.", "Un gang familial monte en puissance dans l’Angleterre d’après-guerre."),
            ("Vikings", "Historique", "Bon choix pour l’aventure, le conflit et l’ampleur.", "L’ascension d’un guerrier devenu légendaire.")
        ],
        "aventure": [
            ("Lost", "Aventure", "Très bon si tu veux du mystère et un grand sens de l’exploration.", "Des survivants tentent de comprendre leur île étrange."),
            ("Outer Banks", "Aventure", "Plus léger et dynamique, parfait pour binge-watcher.", "Un groupe d’amis se lance dans une chasse au trésor."),
            ("The Last Kingdom", "Aventure", "Bonne recommandation pour l’action et les grands conflits.", "Un guerrier partagé entre deux mondes choisit son destin.")
        ]
    }

    default_recos = [
        ("Breaking Bad", "Drame", "Une valeur sûre si tu veux une série marquante et maîtrisée.", "Un professeur bascule dans le crime après un choc personnel."),
        ("Stranger Things", "Science-fiction", "Très bonne option populaire avec mystère et aventure.", "Des événements surnaturels frappent une petite ville."),
        ("The Bear", "Drame", "Très efficace pour quelque chose d’intense et moderne.", "Un chef tente de sauver le restaurant familial sous pression.")
    ]

    selected_key = genres[0].lower() if genres else None
    base = genre_map.get(selected_key, default_recos)

    results = []
    match = 97

    for idx, (name, genre, why, resume) in enumerate(base[:3]):
        bonus = []
        if moods:
            bonus.append(f"Ambiance {moods[0]}")
        if paces:
            bonus.append(f"rythme {paces[0]}")
        if styles:
            bonus.append(f"style {styles[0]}")
        if popularity:
            bonus.append(f"profil {popularity[0]}")
        if formats:
            bonus.append(f"format {formats[0]}")
        if extra:
            bonus.append("ta précision personnelle a aussi été prise en compte")

        if bonus:
            why = f"{why} " + ", ".join(bonus) + "."

        results.append({
            "nom_de_serie": name,
            "genre": genre,
            "niveau_match": max(match - idx * 4, 85),
            "pourquoi_ce_choix": why,
            "resume": resume
        })

    return results


@api.route("/api/recommendations/gemini", methods=["POST"])
@login_required
def generate_gemini_recommendations():
    data = request.get_json() or {}

    genres = data.get("genres", [])
    moods = data.get("moods", [])
    paces = data.get("paces", [])
    styles = data.get("styles", [])
    popularity = data.get("popularity", [])
    formats = data.get("formats", [])
    extra = (data.get("extra") or "").strip()

    total_selected = (
        len(genres) +
        len(moods) +
        len(paces) +
        len(styles) +
        len(popularity) +
        len(formats)
    )

    if total_selected == 0 and not extra:
        return jsonify({"error": "Choisis au moins un filtre."}), 400

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        recommendations = local_fallback_recommendations(
            genres, moods, paces, styles, popularity, formats, extra
        )
        recommendations = enrich_with_images(recommendations)
        return jsonify({"recommendations": recommendations}), 200

    response_schema = types.Schema(
        type=types.Type.ARRAY,
        items=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "nom_de_serie": types.Schema(type=types.Type.STRING),
                "genre": types.Schema(type=types.Type.STRING),
                "niveau_match": types.Schema(type=types.Type.INTEGER),
                "pourquoi_ce_choix": types.Schema(type=types.Type.STRING),
                "resume": types.Schema(type=types.Type.STRING),
            },
            required=[
                "nom_de_serie",
                "genre",
                "niveau_match",
                "pourquoi_ce_choix",
                "resume"
            ]
        )
    )

    try:
        client = genai.Client(api_key=api_key)

        full_prompt = f"""
Tu es une IA experte en recommandations de séries TV.

Tu dois recommander 5 séries maximum.
Réponds en français.
Base-toi uniquement sur les filtres donnés.
Un seul filtre peut suffire.
N'utilise pas d'historique de visionnage.
N'utilise pas de notes utilisateur.
Le ton doit être naturel, moderne et convaincant.

Filtres choisis :
Genres : {", ".join(genres) if genres else "non précisé"}
Ambiance : {", ".join(moods) if moods else "non précisé"}
Rythme : {", ".join(paces) if paces else "non précisé"}
Style : {", ".join(styles) if styles else "non précisé"}
Popularité : {", ".join(popularity) if popularity else "non précisé"}
Format : {", ".join(formats) if formats else "non précisé"}
Précision complémentaire : {extra if extra else "aucune"}

Retourne uniquement un JSON strict :
[
  {{
    "nom_de_serie": "...",
    "genre": "...",
    "niveau_match": 95,
    "pourquoi_ce_choix": "...",
    "resume": "..."
  }}
]

Contraintes :
- niveau_match entre 80 et 100
- pourquoi_ce_choix : 35 mots max
- resume : 40 mots max
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.8
            )
        )

        recommendations = json.loads(response.text)
        recommendations = enrich_with_images(recommendations)
        return jsonify({"recommendations": recommendations}), 200

    except Exception as e:
        print("ERREUR GEMINI :", e)
        recommendations = local_fallback_recommendations(
            genres, moods, paces, styles, popularity, formats, extra
        )
        recommendations = enrich_with_images(recommendations)
        return jsonify({"recommendations": recommendations}), 200
