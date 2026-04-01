import json
import os

from flask import Flask, render_template, session, redirect, url_for, request, jsonify, g
from google import genai
from google.genai import types
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from models import User
from routes import auth, api, login_required

from flask_session import Session
from models import db

os.environ["GEMINI_API_KEY"] = "AIzaSyCWfUAniqSpOkXlqrI4AUDA5uFeX_9HbT0"

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
    return render_template('home.html')


@app.route('/test-home', methods=['GET'])
def test_home():
    return render_template("home.html")


@app.route('/Mes-Series', methods=['GET'])
@login_required
def mes_Series():
    return render_template("Mes-Series.html", user=g.user)


@app.route('/recommendations', methods=['GET'])
@login_required
def recommendations_page():
    return render_template("recommendations.html", user=g.user)


@app.route('/test-recommendations', methods=['GET'])
@login_required
def test_recommendations():
    pseudo = session.get('user')
    reco = gemini_recommendations()
    print(reco)
    return render_template(
        "recommendations.html",
        user=User.get_by_username(pseudo),
        recommendations=reco
    )


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
                "nom_de_serie": types.Schema(type=types.Type.STRING),
                "explication": types.Schema(type=types.Type.STRING),
                "resume": types.Schema(type=types.Type.STRING),
            },
            required=["nom_de_serie", "explication", "resume"]
        )
    )

    try:
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        series_list_str = "\n".join(formatted_list)

        full_prompt = f"""
Tu es une IA experte en analyse cinématographique. Génère 10 recommandations basées sur ces données :
{series_list_str}

### MÉTHODOLOGIE :
Analyse les succès (4-5/5) pour trouver des points communs techniques et évite les thématiques des échecs (0-2/5).

### CONTRAINTES DE RÉDACTION :
- "explication" : MAXIMUM 50 mots. Analyse pourquoi cette série plaira techniquement.
- "resume" : MAXIMUM 50 mots. Pitch percutant pour donner envie.

### FORMAT JSON :
Utilise exactement ces clés : "nom_de_serie", "explication", "resume".
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
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