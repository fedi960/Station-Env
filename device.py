from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

devices_bp = Blueprint('devices', __name__)

def get_db():
    return psycopg2.connect(dbname="Station-Environnemental",
                            user="postgres",
                            password="fedi",
                            host="localhost")

@devices_bp.route('/devices', methods=['GET', 'POST'])
def list_devices():
    if 'user_id' not in session:
        return redirect(url_for('users.login'))
    user_id = session['user_id']
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute('SELECT name , location FROM devices WHERE user_id = %s', (user_id,))
    devices = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('list_device.html', devices=devices)