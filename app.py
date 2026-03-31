from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from google import genai
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from models import User

from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

db = SQLAlchemy()
sess = Session()

app = Flask(__name__)

app.config["SECRET_KEY"] = "dev-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Genflix.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_SQLALCHEMY"] = db


@app.route('/', methods=['GET'])
def home():
    return render_template("base.html")


@app.route('/test-home', methods=['GET'])
def test_home():
    return render_template("home.html")


@app.route('/test-recommendations', methods=['GET'])
def test_recommendations():
    return render_template("recommendations.html")


@app.route('/api/recommendations/gemini', methods=['POST'])
def gemini_recommendations():
    data = request.get_json()
    last_series = data.get("last_series", [])

    if not last_series:
        return jsonify({"error": "Aucune série fournie."}), 400

    try:
        client = genai.Client()

        prompt = f"""
Tu es un assistant de recommandation de séries pour GenFlix.
À partir de cette liste de 10 dernières séries regardées :
{", ".join(last_series)}

Propose 5 séries à regarder ensuite.
Réponds en français.
Format attendu :
1. Nom de la série - courte explication
2. Nom de la série - courte explication
3. Nom de la série - courte explication
4. Nom de la série - courte explication
5. Nom de la série - courte explication
"""

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
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