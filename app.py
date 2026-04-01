from flask import Flask, render_template, session, request, jsonify
from google import genai
import os

from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from models import User, db
from routes import auth, api

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
    pseudo = session.get('pseudo')
    return render_template('home.html', pseudo=pseudo)


@app.route('/test-home', methods=['GET'])
def test_home():
    return render_template("home.html")


@app.route('/Mes-Series', methods=['GET'])
def mes_series():
    return render_template("Mes-Series.html")


@app.route('/test-recommendations', methods=['GET'])
def test_recommendations():
    return render_template("recommendations.html")

@app.route('/api/recommendations/gemini', methods=['POST'])
def gemini_recommendations():
    data = request.get_json()
    last_series = data.get("last_series", [])
    user_prompt = data.get("prompt", "")

    if not last_series:
        return jsonify({"error": "Aucune série fournie."}), 400

    try:
        # connexion Gemini avec la clé
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

        # prompt modifiable par utilisateur)
        prompt = f"""
Tu es un expert en recommandations de séries.

Voici les dernières séries regardées par un utilisateur :
{", ".join(last_series)}

{user_prompt}

Propose 5 séries adaptées à ses goûts.

Format :
1. Série - courte explication
2. Série - courte explication
3. Série - courte explication
4. Série - courte explication
5. Série - courte explication
"""

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        return jsonify({"result": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

db.init_app(app)
sess.init_app(app)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)