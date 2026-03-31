from flask import Blueprint, Flask, render_template, session, redirect,url_for, request ,jsonify

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from models import User , Serie , db

from flask_sqlalchemy import SQLAlchemy
from flask_session import Session


auth = Blueprint('auth', __name__)  # Blueprint = groupe de routes

api = Blueprint("api", __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json(force=True, silent=True)
        print("DATA REÇUE :", data)  # ← regarde ce qui s'affiche

        if data is None:
            return jsonify({'success': False, 'message': 'Données manquantes'})

        email    = data['email']
        password = data['password']

        user = User.query.filter_by(Email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['pseudo']  = user.Pseudo
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'E-mail ou mot de passe incorrect'})

    return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data     = request.get_json(force=True, silent=True)
        print("DATA REÇUE :", data)  # ← ajoute ça
        pseudo   = data['pseudo']
        email    = data['email']
        password = data['password']

        user_existant  = User.query.filter_by(Pseudo=pseudo).first()
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

        return jsonify({'success': True})

    return render_template('register.html')


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@api.route("/api/AjouterSerie", methods=["POST"])
def ADDSerie():
    data = request.get_json()
    idS = int( data['id'])
    nameS = data['name']
    print(idS)
    print(nameS)
    
    serie = Serie(idtvmaze=idS,name=nameS )
    db.session.add(serie)
    db.session.commit()
    # Ici tu pourras ajouter la logique pour enregistrer en BDD
    return jsonify({"status": "success", "received": data}), 200
