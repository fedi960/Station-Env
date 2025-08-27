from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
import psycopg2

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
    cursor.execute('SELECT id, name , location FROM devices WHERE user_id = %s', (user_id,))
    devices = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('list_device.html', devices=devices)

@devices_bp.route("/devices/new", methods=["GET", "POST"])
def new_device():
    if request.method == "POST":
        name = request.form["name"]
        location = request.form["location"]

        new_api_key = str(uuid4())
        list_mesures = request.form.getlist("values")
        sketch_io= generate_esp32_sketch(list_mesures)


        if 'user_id' not in session:
            return redirect(url_for('auth.login'))

        user_id = session['user_id']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO devices (name, location, list_mesures,api_key,user_id, sketch_io) VALUES (%s,%s,%s,%s,%s,%s)",
            (name, location, list_mesures, new_api_key, user_id, sketch_io)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Device ajouté avec succès (non activé)", "success")
        return redirect(url_for("devices.list_devices"))

    return render_template("newdevice.html")


"""***************************** GENERATE CODE ESP  ***********************************"""


def generate_esp32_sketch( measurements):

    # Déclarations des librairies selon les capteurs choisis
    includes = [
        '#include <WiFi.h>',
        '#include <HTTPClient.h>'
    ]
    setup_code = []
    loop_code = []

    if "temperature" in measurements or "humidity" in measurements:
        includes.append('#include "DHT.h"')
        setup_code.append('DHT dht(4, DHT22);')  # GPIO4, capteur DHT22
        loop_code.append('float temperature = dht.readTemperature();')
        loop_code.append('float humidity = dht.readHumidity();')

    if "ph" in measurements:
        loop_code.append('int phValue = analogRead(34);  // GPIO34 pour capteur pH')
        loop_code.append('float ph = (phValue * 14.0) / 4095.0;')

    # Construction du JSON à envoyer
    json_parts = []
    if "temperature" in measurements:
        json_parts.append('"temperature": temperature')
    if "humidity" in measurements:
        json_parts.append('"humidity": humidity')
    if "ph" in measurements:
        json_parts.append('"ph": ph')

    json_string = "{" + ",".join(json_parts) + "}"

    # Code complet
    code = f"""
{chr(10).join(includes)}

const char* ssid = "wifi_ssid";
const char* password = "wifi_password";
String serverName = "server_url";
String apiKey = "api_key";

void setup() {{
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi..");
  while (WiFi.status() != WL_CONNECTED) {{
    delay(1000);
    Serial.print(".");
  }}
  Serial.println("Connected to WiFi");
  {"dht.begin();" if "temperature" in measurements or "humidity" in measurements else ""}
}}

void loop() {{
  if (WiFi.status() == WL_CONNECTED) {{
    HTTPClient http;
    http.begin(serverName + "/api/measurements");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-API-KEY", apiKey);

    {chr(10).join(loop_code)}

    String json = String("{json_string}");
    int httpResponseCode = http.POST(json);

    Serial.print("Response: ");
    Serial.println(httpResponseCode);

    http.end();
  }} else {{
    Serial.println("WiFi Disconnected");
  }}
  delay(10000); // envoie toutes les 10 secondes
}}
"""
    return code



@devices_bp.route("/api/delete_device/<int:device_id>", methods=["DELETE"])
def delete_device(device_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM devices WHERE id = %s", (device_id,))
        rows_deleted = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        if rows_deleted == 0:
            return jsonify({"error": "Aucun device trouvé avec cet ID."}), 404

        return jsonify({"message": f"✅ Device {device_id} supprimé avec succès."}), 200
    except Exception as e:
        return jsonify({"error": f"❌ Erreur lors de la suppression : {str(e)}"}), 500
