from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import psycopg2
from datetime import datetime
from extensions import socketio
mesures_bp = Blueprint('mesures', __name__)

def get_db():
    return psycopg2.connect(dbname="Station-Environnemental",
                            user="postgres",
                            password="fedi",
                            host="localhost")


@mesures_bp.route("/api/mesures", methods=["POST"])
def insert_mesures():
    # 1️⃣ Get API key from headers
    api_key = request.headers.get("X-API-KEY")
    if not api_key:
        return jsonify({"error": "Missing API key"}), 403

    # 2️⃣ Get JSON data from request
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    conn = get_db()
    cur = conn.cursor()

    # 3️⃣ Verify device by API key
    cur.execute("SELECT id FROM devices WHERE api_key = %s", (api_key,))
    device_row = cur.fetchone()
    if not device_row:
        cur.close()
        conn.close()
        return jsonify({"error": "Invalid API key"}), 403
    device_id = device_row[0]

    # 4️⃣ Insert a new mesure row
    cur.execute("INSERT INTO mesure (id_device) VALUES (%s) RETURNING id", (device_id,))
    id_mesure = cur.fetchone()[0]

    # 5️⃣ Insert each capability value
    now = datetime.utcnow()
    for capability, value in data.items():
        cur.execute("""
            INSERT INTO mesurevalues (valeur, time, id_capability, id_mesure)
            VALUES (%s, %s, (SELECT id FROM capability WHERE typecapability = %s LIMIT 1), %s)
        """, (value, now, capability, id_mesure))

        socketio.emit('new_measurement', {
            "device_id": device_id,
            "capability": capability.lower(),
            "value": value,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
        })

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Data saved successfully"})
@mesures_bp.route("/dev_details/<int:device_id>", methods=["GET"])
def device_detail(device_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, location FROM devices WHERE id = %s", (device_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        flash("❌ Appareil introuvable", "danger")
        return redirect(url_for("devices.list_devices"))

    device = {
        "id": row[0],
        "name": row[1],
        "location": row[2]
    }
    return render_template("device_detail.html", device=device)

@mesures_bp.route("/realtime/<int:device_id>", methods=["GET"])
def realtime(device_id):
    conn = get_db()
    cur = conn.cursor()

    # Récupérer les 20 dernières mesures de ce device
    cur.execute("""
        SELECT c.typecapability, mv.valeur, mv.time
        FROM mesurevalues mv
        JOIN mesure m ON mv.id_mesure = m.id
        JOIN capability c ON mv.id_capability = c.id
        WHERE m.id_device = %s
        ORDER BY mv.time DESC
        LIMIT 20
    """, (device_id,))
    rows = cur.fetchall()

    # Infos du device
    cur.execute("SELECT id, name, location, api_key FROM devices WHERE id = %s", (device_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        flash("Appareil introuvable", "danger")
        return redirect(url_for("devices.list_devices"))

    device = {"id": row[0], "name": row[1], "location": row[2], "api_key": row[3]}

    cur.close()
    conn.close()

    # Organiser les mesures
    data = {}
    for name, value, ts in rows:
        if name not in data:
            data[name] = []
        data[name].append({"value": value, "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S")})

    return render_template("realtime.html", device=device, data=data)


@mesures_bp.route("/history/<int:device_id>", methods=["GET"])
def history(device_id):
    conn = get_db()
    cur = conn.cursor()

    # Récupérer toutes les mesures du device
    cur.execute("""
        SELECT c.typecapability, mv.valeur, mv.time
        FROM mesurevalues mv
        JOIN mesure m ON mv.id_mesure = m.id
        JOIN capability c ON mv.id_capability = c.id
        WHERE m.id_device = %s
        ORDER BY mv.time ASC
    """, (device_id,))
    rows = cur.fetchall()

    # Infos du device
    cur.execute("SELECT id, name, location, api_key FROM devices WHERE id = %s", (device_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        flash("Appareil introuvable", "danger")
        return redirect(url_for("devices.list_devices"))

    device = {"id": row[0], "name": row[1], "location": row[2], "api_key": row[3]}

    cur.close()
    conn.close()

    # Organiser les données par type de capability
    data = {}
    for name, value, ts in rows:
        if name not in data:
            data[name] = []
        data[name].append({"value": value, "timestamp": ts})

    return render_template("history.html", device=device, data=data)


@mesures_bp.route("/esp_code/<int:device_id>", methods=["GET"])
def esp_code(device_id):
    conn = get_db()
    cur = conn.cursor()

    # Récupérer le sketch et infos du device
    cur.execute("SELECT id, name, location, api_key, sketch_io FROM devices WHERE id = %s", (device_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return "Device not found", 404

    device = {"id": row[0], "name": row[1], "location": row[2], "api_key": row[3]}
    sketch_code = row[4]

    cur.close()
    conn.close()

    return render_template("esp_code.html", device=device, sketch_code=sketch_code)
