from flask import Blueprint, Flask, render_template, session, redirect,url_for, request ,jsonify, g

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from models import User , Serie , db


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

        # ← connecte directement l'utilisateur après inscription
        session['user']    = pseudo
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
    idS = int( data['id'])
    nameS = data['name']
    imgurl = data['img']
    serie = Serie(idtvmaze=idS,name=nameS,img=imgurl,user_id=session['user_id'] )
    db.session.add(serie)
    db.session.commit()
    return jsonify({"status": "success", "received": data}), 200



@api.route("/api/RemoveSerie/<int:key_id>", methods=["DELETE"])

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

def GetAllUser():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    Liste_Serie= Serie.get_All_Serie(user_id=user_id)
    liste_finale = []
    for s in Liste_Serie:
        liste_finale.append(s.to_dict())
    return jsonify(liste_finale)

