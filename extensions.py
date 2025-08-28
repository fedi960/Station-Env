from flask_socketio import SocketIO

# Une seule instance globale
socketio = SocketIO(cors_allowed_origins="*")
