from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

user_bp = Blueprint('users', __name__)

def get_db():
    return psycopg2.connect(
        dbname="Station-Environnemental",
        user="postgres",
        password="fedi",
        host="localhost"
    )

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
            flash("Cet email est déjà utilisé.")
            cur.close()
            conn.close()
            return redirect(url_for('users.register'))

        cur.execute(
            "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
            (username, password, email)
        )
        conn.commit()
        cur.close()
        conn.close()

        flash("Inscription réussie, vous pouvez vous connecter.")
        return redirect(url_for('users.login'))

    return render_template('register.html')


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, username, password FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash("Connexion réussie !")
            return redirect(url_for('devices.list_devices'))  # 🔧 à remplacer par ton vrai endpoint
        else:
            flash("Email ou mot de passe incorrect.")

    return render_template('login.html')


@user_bp.route('/logout')
def logout():
    session.clear()
    flash("Déconnecté.")
    return redirect(url_for('users.login'))


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
            flash("Mot de passe changé.")
            cur.close()
            conn.close()
            return redirect(url_for('users.profile'))  # 🔧 tu peux créer une route profile
        else:
            flash("Ancien mot de passe incorrect.")

        cur.close()
        conn.close()

    return render_template('change_password.html')
