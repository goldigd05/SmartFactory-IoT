"""
simulate_sensor.py
──────────────────
Agar tere paas actual Arduino/ESP32 nahi hai,
yeh script fake sensor data bhejti hai Flask server ko.

Usage:
  python simulate_sensor.py          (sends 1 reading every 5 seconds)
  python simulate_sensor.py --spike  (force anomaly spike every 5th reading)
"""

import requests, time, random, sys, math

URL = "http://localhost:5000/send"

def make_reading(force_spike=False):
    spike = force_spike or (random.random() < 0.08)
    return {
        "temperature": round(random.gauss(65, 4) + (22 if spike else 0), 1),
        "vibration":   round(random.gauss(5.0, 0.8) + (7 if spike else 0), 2),
        "pressure":    round(random.gauss(101, 0.7) - (9 if spike else 0), 1),
    }

def run():
    spike_mode = "--spike" in sys.argv
    count = 0
    print("  Sensor Simulator Started")
    print(f"  Sending to: {URL}")
    print("  Press Ctrl+C to stop\n")

    while True:
        count += 1
        force = spike_mode and (count % 5 == 0)
        data = make_reading(force_spike=force)

        try:
            r = requests.post(URL, json=data, timeout=3)
            resp = r.json()
            tag = "🔴 ANOMALY" if resp.get("anomaly") else "🟢 Normal"
            print(f"  [{count:03d}] T={data['temperature']}°C  V={data['vibration']}  P={data['pressure']}kPa  → {tag}")
        except Exception as e:
            print(f"  [!] Could not connect to server: {e}")

        time.sleep(5)

if __name__ == "__main__":
    run()
