# 🏭 Smart Factory Monitoring System
### Team TechForge | IoT + ML | Industrial Automation

## 📁 Project Structure

smart_factory/
├── app.py                  ← Flask backend + ML model
├── simulate_sensor.py      ← Fake sensor data sender (no hardware needed)
├── requirements.txt        ← Python libraries
├── factory.db              ← Auto-created SQLite database
└── templates/
    └── index.html          ← Dashboard UI (Chart.js)

## ⚡ Run Karne Ke Steps (Step by Step)

### Step 1 — Libraries Install Karo

pip install flask scikit-learn numpy requests

### Step 2 — Server Start Karo
python app.py
Terminal mein dikhega:

Smart Factory Monitoring System
Open browser: http://localhost:5000

### Step 3 — Browser Mein Kholo
http://localhost:5000


### Step 4 — Sensor Data Bhejo

**Option A: Dashboard se (Easiest)**
- Dashboard pe "Send One Reading" button click karo
- Ya "Auto-Send (5s)" click karo — automatically data bhejta rahega

**Option B: Separate terminal se simulator**

python simulate_sensor.py


## 🔌 Arduino Integration (Actual Hardware)

Agar Arduino/ESP32 hai toh yeh code Arduino IDE mein upload karo:

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

const char* ssid     = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverURL = "http://YOUR_PC_IP:5000/send";

DHT dht(4, DHT11);  // DHT11 on pin 4

void setup() {
  Serial.begin(115200);
  dht.begin();
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  Serial.println("WiFi Connected!");
}

void loop() {
  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();

  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/json");

  String payload = "{\"temperature\":" + String(temp) +
                   ",\"vibration\":5.2,\"pressure\":101.3}";

  int code = http.POST(payload);
  Serial.println("Response: " + String(code));
  http.end();
  delay(5000);  // send every 5 seconds
}

## 🧠 How ML Works

1. **Training:** At startup, 800 normal sensor readings are generated
2. **Model:** Isolation Forest (contamination=5%)
3. **Scoring:** Each new reading → predict() → +1 Normal / -1 Anomaly
4. **Alert:** If anomaly, red highlight on dashboard + alert log entry

## 📊 API Endpoints

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Dashboard |
| `/send` | POST | Receive sensor data |
| `/data` | GET | Last 20 readings (JSON) |
| `/stats` | GET | Summary statistics |
| `/simulate` | GET | Generate fake reading |
