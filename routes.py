from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Serie, db

import json
import os
import requests
from google import genai
from google.genai import types

auth = Blueprint('auth', __name__)
api = Blueprint("api", __name__)

# =========================================================
# AUTH
# =========================================================

def login_required(f):
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

        if User.query.filter_by(Pseudo=pseudo).first():
            return jsonify({'success': False, 'message': 'Pseudo déjà utilisé'})

        if User.query.filter_by(Email=email).first():
            return jsonify({'success': False, 'message': 'Email déjà utilisé'})

        password_hash = generate_password_hash(password)

        user = User(
            Pseudo=pseudo,
            Email=email,
            password_hash=password_hash
        )

        db.session.add(user)
        db.session.commit()

        session['user'] = pseudo
        session['user_id'] = user.id

        return jsonify({'success': True})

    return render_template('register.html')


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# =========================================================
# SERIES
# =========================================================


@api.route("/api/AjouterSerie", methods=["POST"])
def ADDSerie():
    data = request.get_json()

    serie = Serie(
        idtvmaze=int(data['id']),
        name=data['name'],
        img=data['img'],
        user_id=session['user_id']
    )

    db.session.add(serie)
    db.session.commit()

    return jsonify({"status": "success"}), 200


@api.route("/api/RemoveSerie/<int:key_id>", methods=["DELETE"])
def Remove(key_id):
    serie = Serie.query.filter_by(
        user_id=session['user_id'],
        idtvmaze=key_id
    ).first()

    if serie:
        db.session.delete(serie)
        db.session.commit()
        return jsonify({"status": "success"}), 200

    return jsonify({"error": "Not found"}), 404


@api.route("/api/GetSerieUser", methods=["GET"])
def GetAllUser():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    series = Serie.get_All_Serie(user_id=user_id)
    return jsonify([s.to_dict() for s in series])


@api.route("/api/Note", methods=["POST"])
def AddMajNote():
    data = request.get_json()

    serie = Serie.query.filter_by(
        user_id=session['user_id'],
        idtvmaze=data['ids']
    ).first()

    if not serie:
        return jsonify({"error": "Not found"}), 404

    serie.note = data['note']
    db.session.commit()

    return jsonify({"status": "success"}), 200

# =========================================================
# UTILS
# =========================================================

def get_tvmaze_image(show_name):
    try:
        res = requests.get("https://api.tvmaze.com/search/shows", params={"q": show_name})
        data = res.json()

        if not data:
            return ""

        return data[0]["show"]["image"]["original"]

    except:
        return ""


def enrich_with_images(recommendations):
    for r in recommendations:
        r["image"] = get_tvmaze_image(r["nom_de_serie"])
    return recommendations

# =========================================================
# 1️⃣ RECO BASEE SUR SERIES
# =========================================================

@api.route("/api/recommendations/gemini", methods=["POST"])
@login_required
def reco_last_series():
    data = request.get_json() or {}
    last_series = data.get("last_series", [])

    if not last_series:
        return jsonify({"error": "Pas de séries"}), 400

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return jsonify({
            "result": f"Suggestions proches de : {', '.join(last_series)}"
        }), 200

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
Recommande des séries proches de :
{", ".join(last_series)}

Réponse courte et fluide.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return jsonify({"result": response.text}), 200

    except:
        return jsonify({"result": "Erreur Gemini"}), 200

# =========================================================
# 2️⃣ TA RECO FILTRES
# =========================================================

@api.route("/api/recommendations/gemini/filters", methods=["POST"])
@login_required
def reco_filters():
    data = request.get_json() or {}
    genres = data.get("genres", [])
    moods = data.get("moods", [])
    paces = data.get("paces", [])
    styles = data.get("styles", [])
    popularity = data.get("popularity", [])
    formats = data.get("formats", [])
    extra = data.get("extra", "")

    if not any([genres, moods, paces, styles, popularity, formats, extra]):
        return jsonify({"error": "Choisis un filtre"}), 400

    geminireponse = gemini_filtre(genres, moods, paces, styles, popularity, formats, extra)
    series = []
    print(geminireponse)
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

    return jsonify({"recommendations": series}), 200




def gemini_filtre(genres, moods, paces, styles, popularity, formats, extra):

    filtre = {
    'genres': genres,
    'moods': moods,
    'paces': paces,
    'styles': styles,
    'popularity': popularity,
    'formats': formats,
    'extra': extra
    };

    print(filtre)

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
        filtres = json.dumps(filtre, ensure_ascii=False, indent=2)

        full_prompt = f"""
Rôle :
Tu es une IA experte en analyse cinéphile et en recommandation de séries TV. Tu combines une compréhension fine des préférences utilisateurs avec une expertise narrative (réalisation, rythme, écriture, direction artistique).
Objectif :
Proposer 8 séries parfaitement adaptées aux préférences de l’utilisateur, en te basant sur les filtres fournis.
Chaque recommandation doit être argumentée, précise et personnalisée.

Données d'entrée : {filtres}
Méthodologie d’analyse :
Construction du profil utilisateur (ADN cinéphile)
Identifier les combinaisons clés (ex : thriller + sombre + rythme lent = tension psychologique).
Déduire les attentes implicites (ex : “style visuel travaillé” → importance de la mise en scène).
Prioriser les filtres dominants.
Interprétation des filtres :
genres → univers narratif principal
moods → ambiance émotionnelle recherchée
paces → rythme (lent, modéré, rapide)
styles → signature visuelle ou narrative
popularity → mainstream vs pépites
formats → mini-série, long format, anthologie, etc.
extra → contraintes spécifiques (plot twist, romance secondaire, anti-héros, etc.)
Contraintes de recommandation :
Éviter toute série incohérente avec les filtres
Varier légèrement les propositions pour éviter la redondance
Prioriser la qualité narrative et esthétique
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