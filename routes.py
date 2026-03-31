from flask import Blueprint, Flask, render_template, session, redirect,url_for, request

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from models import User

from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

db = SQLAlchemy()
sess = Session()    

auth = Blueprint('auth', __name__)  # Blueprint = groupe de routes

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Chercher l'utilisateur en BDD par son email
        user = User.query.filter_by(Email=email).first()

        # Vérifier que l'utilisateur existe ET que le mot de passe est correct
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['pseudo'] = user.Pseudo
            return redirect(url_for('home'))  # redirige vers ta page principale
        else:
            return render_template('login.html', error="E-mail ou mot de passe incorrect")

    return redirect(url_for('home'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 1. Récupérer les données du formulaire
        pseudo = request.form['pseudo']
        email = request.form['email']
        password = request.form['password']

        # 2. Hasher le mot de passe (ne jamais stocker en clair)
        password_hash = generate_password_hash(password)

        # 3. Créer l'objet utilisateur
        nouvel_utilisateur = User(
            Pseudo=pseudo,
            Email=email,
            password_hash=password_hash
        )

        # 4. Ajouter en BDD
        db.session.add(nouvel_utilisateur)
        db.session.commit()

        return redirect(url_for('login'))  # Rediriger vers une page de succès ou de connexion

    return render_template('register.html')
