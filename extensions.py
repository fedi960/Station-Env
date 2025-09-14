from flask_socketio import SocketIO
from flask_mail import Mail

# Une seule instance globale
socketio = SocketIO(cors_allowed_origins="*")
mail = Mail()