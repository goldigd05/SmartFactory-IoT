from flask import Flask, request, jsonify, render_template
from sklearn.ensemble import IsolationForest
import sqlite3, json, random, math
from datetime import datetime
import numpy as np

app = Flask(__name__)
DB = "factory.db"

# ─── DATABASE SETUP ───
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        temperature REAL,
        vibration REAL,
        pressure REAL,
        anomaly INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

# ─── TRAIN MODEL ON STARTUP ───
def train_model():
    """Generate synthetic normal data and train Isolation Forest."""
    np.random.seed(42)
    n = 800
    normal_data = np.column_stack([
        np.random.normal(65, 5, n),    # temp: 55–75°C normal
        np.random.normal(5, 1, n),     # vibration: 3–7 m/s² normal
        np.random.normal(101, 1, n),   # pressure: 99–103 kPa normal
    ])
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(normal_data)
    return model

model = train_model()

def is_anomaly(temp, vibration, pressure):
    features = np.array([[temp, vibration, pressure]])
    result = model.predict(features)
    return int(result[0] == -1)

# ─── ROUTES ───

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def receive_data():
    """Receive sensor data from Arduino/simulator."""
    data = request.get_json()
    temp      = float(data.get('temperature', 65))
    vibration = float(data.get('vibration', 5))
    pressure  = float(data.get('pressure', 101))
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    anomaly   = is_anomaly(temp, vibration, pressure)

    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT INTO readings (timestamp, temperature, vibration, pressure, anomaly) VALUES (?,?,?,?,?)",
        (timestamp, temp, vibration, pressure, anomaly)
    )
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok', 'anomaly': bool(anomaly)})

@app.route('/data')
def get_data():
    """Send last 20 readings to dashboard."""
    conn = sqlite3.connect(DB)
    rows = conn.execute(
        "SELECT timestamp, temperature, vibration, pressure, anomaly FROM readings ORDER BY id DESC LIMIT 20"
    ).fetchall()
    conn.close()
    rows = list(reversed(rows))
    return jsonify([{
        'time':        r[0][-8:],   # HH:MM:SS only
        'temperature': round(r[1], 1),
        'vibration':   round(r[2], 2),
        'pressure':    round(r[3], 1),
        'anomaly':     r[4]
    } for r in rows])

@app.route('/stats')
def stats():
    """Summary stats for KPI cards."""
    conn = sqlite3.connect(DB)
    row = conn.execute(
        "SELECT COUNT(*), SUM(anomaly), AVG(temperature), AVG(vibration), AVG(pressure) FROM readings"
    ).fetchone()
    conn.close()
    total, anomalies, avg_t, avg_v, avg_p = row
    return jsonify({
        'total':      total or 0,
        'anomalies':  int(anomalies or 0),
        'avg_temp':   round(avg_t or 0, 1),
        'avg_vib':    round(avg_v or 0, 2),
        'avg_pres':   round(avg_p or 0, 1),
    })

@app.route('/simulate')
def simulate():
    """Generate one random sensor reading (for demo without hardware)."""
    t = datetime.now().second
    # Occasionally inject spikes
    spike = random.random() < 0.08
    temp      = round(random.gauss(65, 4) + (20 if spike else 0), 1)
    vibration = round(random.gauss(5, 0.8) + (6 if spike else 0), 2)
    pressure  = round(random.gauss(101, 0.8) - (8 if spike else 0), 1)
    return jsonify({'temperature': temp, 'vibration': vibration, 'pressure': pressure})

if __name__ == '__main__':
    init_db()
    print("\n  Smart Factory Monitoring System")
    print("  Open browser: http://localhost:5000\n")
    app.run(debug=True, port=5000)
