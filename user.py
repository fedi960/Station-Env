from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

user_bp = Blueprint('users', __name__)

def get_db():
    return psycopg2.connect(dbname="Station-Environnemental", user="postgres", password="fedi", host="localhost")

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        email = request.form['email']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''insert into users (username, password, email) values (%s, %s, %s)''', (username, password, email))
        conn.commit()
        cursor.close()

        return redirect('/login')
    return render_template('register.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, password FROM users WHERE email = %s', (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result and check_password_hash(result[1], password):
            session['user_id'] = result[0]
            return render_template('list_device.html')
        else:
            flash("Email or mot de passe incorrect")
    return render_template('login.html')


@user_bp.route('/logout')
def logout():
    session.clear()
    flash("Déconnecté.")
    return redirect('/login')

@user_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        old = request.form['old_password']
        new = generate_password_hash(request.form['new_password'])

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE id = %s", (session['user_id'],))
        current = cur.fetchone()

        if current and check_password_hash(current[0], old):
            cur.execute("UPDATE users SET password = %s WHERE id = %s", (new, session['user_id']))
            conn.commit()
            flash("Mot de passe changé.")
            return redirect('/profile')
        else:
            flash("Ancien mot de passe incorrect.")
        cur.close()
        conn.close()
    return render_template('change_password.html')