from flask import Blueprint, Flask, render_template, session, redirect,url_for, request ,jsonify, g

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from models import User , Serie , db, ApiKey


auth = Blueprint('auth', __name__)  # Blueprint = groupe de routes

api = Blueprint("api", __name__)

def login_required(f):
    """
        session uniquement

        grace à la variable g.user, on peut accéder à l'utilisateur connecté 
        dans les fonctions de route protégées par ce décorateur
    """
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return {"error": "non autorisé"}, 401

        user = User.get_by_username(session["user"])
        if user is None:
            session.clear()
            return {"error": "non autorisé"}, 401

        g.user = user
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


def auth_required(f):
    """
        session ou clé API
        
        grace à la variable g.user, on peut accéder à l'utilisateur connecté 
        dans les fonctions de route protégées par ce décorateur
    """

    def wrapper(*args, **kwargs):
        user = None

        if "user" in session:
            user = User.get_by_username(session["user"])

        if user is None:
            api_key_header = request.headers.get("X-API-Key")
            if api_key_header is not None:
                api_key = ApiKey.get_by_key(api_key_header)
                if api_key is not None:
                    user = api_key.user

        if user is None:
            return {"error": "non autorisé"}, 401

        g.user = user
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


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
            session['user'] = user.Pseudo  # ← 'user' au lieu de 'pseudo'
            session['user_id'] = user.id
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
@auth_required
def ADDSerie():
    data = request.get_json()
    print(data['id'])
    serie = Serie(idtvmaze=data['id'],name = 'test')
    db.session.add(serie)
    db.session.commit()
    # Ici tu pourras ajouter la logique pour enregistrer en BDD
    return jsonify({"status": "success", "received": data}), 200



@api.route("/api/RemoveSerie/<int:key_id>", methods=["DELETE"])
@auth_required
def Remove(key_id):
    SerieR = Serie.query.filter_by(user_id=session['user_id'],idtvmaze=key_id).first()
    db.session.delete(SerieR)
    db.session.commit()
    if SerieR:
        db.session.delete(SerieR)
        db.session.commit()
        return jsonify({"status": "success", "message": "Série supprimée"}), 200
    else:
        return jsonify({"status": "error", "message": "Série non trouvée"}), 404
    

@api.route("/api/GetSerieUser", methods=["GET"])
@auth_required
def GetAllUser():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    Liste_Serie= Serie.get_All_Serie(user_id=user_id)
    liste_finale = []
    for s in Liste_Serie:
        liste_finale.append(s.to_dict())
    return jsonify(liste_finale)
