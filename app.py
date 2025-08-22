from flask import Flask, redirect, url_for
from flask_socketio import SocketIO

from user import user_bp

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete'
socketio = SocketIO(app, cors_allowed_origins="*")

app.register_blueprint(user_bp)

def get_db():
    return psycopg2.connect(
        dbname="StationEnv",
        user="postgres",
        password="fedi",
        host="localhost"
    )

@app.route('/')
def index():
    return redirect(url_for('users.login'))

if __name__ == '__main__':
    socketio.run(app,host="0.0.0.0",port=5000, debug=True)
