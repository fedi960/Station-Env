from flask import Flask, redirect, url_for
from flask_socketio import SocketIO

from device import devices_bp
from user import user_bp
from mesure import mesures_bp

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'
socketio = SocketIO(app, cors_allowed_origins="*")

app.register_blueprint(user_bp)
app.register_blueprint(devices_bp)
app.register_blueprint(mesures_bp)

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
    socketio.run(app,host="0.0.0.0",port=5000, debug=True)
