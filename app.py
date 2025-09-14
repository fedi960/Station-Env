from flask import Flask, redirect, url_for
from extensions import socketio, mail

from device import devices_bp
from user import user_bp
from mesure import mesures_bp
import psycopg2

app = Flask(__name__)

# 🔑 Configuration principale
app.config['SECRET_KEY'] = 'une_cle_secrete'  # clé secrète utilisée par serializer
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'votrmail@gmail.com'
app.config['MAIL_PASSWORD'] = 'ctor kgxn pehr xpsw'
app.config['MAIL_DEFAULT_SENDER'] = 'votre/aplication/mail@gmail.com'

# 🔌 Initialisation des extensions
socketio.init_app(app, cors_allowed_origins="*")
mail.init_app(app)

# 🔹 Enregistrement des blueprints
app.register_blueprint(user_bp)
app.register_blueprint(devices_bp)
app.register_blueprint(mesures_bp)

# 🔧 Connexion à la base de données
def get_db():
    return psycopg2.connect(
        dbname="Station-Environnemental",
        user="postgres",
        password="fedi",
        host="localhost"
    )

@app.route('/')
def index():
    return redirect(url_for('users.login'))

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
