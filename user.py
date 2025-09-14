from flask import Blueprint, render_template, current_app, request, redirect, url_for, session, flash
import psycopg2
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import mail
from flask_mail import Message

user_bp = Blueprint('users', __name__)

# 🔹 Serializer pour les tokens
def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

# 🔧 Connexion à la base de données
def get_db():
    return psycopg2.connect(
        dbname="Station-Environnemental",
        user="postgres",
        password="fedi",
        host="localhost"
    )

# ------------------- Routes -------------------

# 🔹 Inscription
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = generate_password_hash(request.form['password'])

        conn = get_db()
        cur = conn.cursor()

        # Vérifier si email déjà utilisé
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            flash("Cet email est déjà utilisé.", "danger")
            cur.close()
            conn.close()
            return redirect(url_for('users.register'))

        # Ajouter utilisateur avec active=False
        cur.execute(
            "INSERT INTO users (username, password, email, active) VALUES (%s, %s, %s, FALSE)",
            (username, password, email)
        )
        conn.commit()
        cur.close()
        conn.close()

        # Envoyer mail de confirmation
        send_confirmation_email(email)

        flash("✅ Compte créé. Vérifiez vos emails pour confirmer.", "success")
        return redirect(url_for('users.login'))

    return render_template('register.html')


# 🔹 Connexion
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, username, password, active FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            user_id, username, hashed_password, active = user
            if not active:
                flash("❌ Vous devez confirmer votre email avant de vous connecter.", "danger")
                return redirect(url_for('users.login'))

            if check_password_hash(hashed_password, password):
                session['user_id'] = user_id
                session['username'] = username
                flash("Connexion réussie !", "success")
                return redirect(url_for('devices.list_devices'))  # 🔧 ton endpoint réel
            else:
                flash("Email ou mot de passe incorrect.", "danger")
        else:
            flash("Email ou mot de passe incorrect.", "danger")

    return render_template('login.html')


# 🔹 Déconnexion
@user_bp.route('/logout')
def logout():
    session.clear()
    flash("Déconnecté.")
    return redirect(url_for('users.login'))


# 🔹 Changement de mot de passe
@user_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('users.login'))

    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = generate_password_hash(request.form['new_password'])

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE id = %s", (session['user_id'],))
        current = cur.fetchone()

        if current and check_password_hash(current[0], old_password):
            cur.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, session['user_id']))
            conn.commit()
            flash("Mot de passe changé.", "success")
            cur.close()
            conn.close()
            return redirect(url_for('users.profile'))  # 🔧 Crée la route profile si nécessaire
        else:
            flash("Ancien mot de passe incorrect.", "danger")

        cur.close()
        conn.close()

    return render_template('change_password.html')


# ------------------- Email de confirmation -------------------

def send_confirmation_email(user_email):
    s = get_serializer()
    token = s.dumps(user_email, salt="email-confirm")
    confirm_url = url_for("users.confirm_email", token=token, _external=True)

    # Mail HTML cliquable
    html_body = f"""
    <p>Cliquez sur ce lien pour confirmer votre compte :</p>
    <p><a href="{confirm_url}">{confirm_url}</a></p>
    """

    msg = Message("Confirmez votre compte", recipients=[user_email])
    msg.html = html_body
    mail.send(msg)


# 🔹 Confirmation de l’email
@user_bp.route('/confirm/<token>')
def confirm_email(token):
    s = get_serializer()
    try:
        email = s.loads(token, salt="email-confirm", max_age=3600)  # lien valide 1h
    except Exception:
        flash("❌ Lien invalide ou expiré", "danger")
        return redirect(url_for("users.login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET active=TRUE WHERE email=%s", (email,))
    conn.commit()
    cur.close()
    conn.close()

    flash("✅ Email confirmé avec succès !", "success")
    return redirect(url_for("users.login"))
