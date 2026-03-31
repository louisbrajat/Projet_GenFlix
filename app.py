from flask import Flask, render_template, session, redirect, url_for, request

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from models import User
from routes import auth,api

from flask_session import Session
from models import db

sess = Session()

app = Flask(__name__)

app.config["SECRET_KEY"] = "dev-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Genflix.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SESSION_TYPE"] = "sqlalchemy"
app.config["SESSION_SQLALCHEMY"] = db

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
def mes_Series():
    return render_template("Mes-Series.html")

db.init_app(app)
sess.init_app(app)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)