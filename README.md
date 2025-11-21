# Health Monitoring System with AI & IoT

## 📌 Project Overview
The **Health Monitoring System** is a comprehensive hybrid application designed to monitor vital health parameters in real-time using IoT sensors and provide intelligent disease prediction using Machine Learning. The system consists of a **Desktop Dashboard** (built with CustomTkinter) for live monitoring and a **Web Portal** (Flask) for patient data management and remote access.

The system integrates an **ESP32** microcontroller to collect data from multiple sensors (Heart Rate, SpO2, Temperature, GSR, Air Quality) and transmits it wirelessly to the application. An ensemble Machine Learning model analyzes this data to predict potential health risks and provides actionable advice.

## 🚀 Features
- **Real-Time Vitals Monitoring**: Live tracking of Heart Rate (BPM), SpO2 (%), Body Temperature (°C), and Galvanic Skin Response (GSR).
- **Environmental Monitoring**: Air Quality Index (AQI) monitoring using MQ-7 and DHT11 sensors.
- **AI-Powered Disease Prediction**: Advanced ML ensemble model predicts potential diseases based on sensor data and patient history.
- **Hybrid Interface**:
  - **Desktop App**: High-performance, dark-themed dashboard for continuous monitoring.
  - **Web Portal**: Accessible interface for doctors/patients to view records and submit queries.
- **Automated Alerts**: Critical health alerts sent via **WhatsApp** (Twilio API) to emergency contacts.
- **Secure Data Handling**: Patient data is encrypted and securely stored/transmitted.
- **Interactive Visualizations**: Real-time graphs for heart rate and other metrics.

## 📂 Folder Structure
```
Health_moni/
├── pakkawalafinal.py       # 🖥️ Main Desktop Application (Entry Point)
├── server.py               # 🌐 Flask Web Server & API
├── pakkwalafinlesp/        # 🔌 ESP32 Arduino Code
│   └── pakkwalafinlesp.ino #    Source code for microcontroller
├── datasets/               # 🧠 ML Models & Datasets
│   ├── health_ai_final...pkl  # Trained Ensemble Model
│   ├── scaler_poly_final.pkl  # Data Scaler
│   └── ...
├── templates/              # 🎨 Web Interface Templates (HTML)
│   ├── index.html          #    Home Page
│   ├── contact.html        #    Contact/Query Page
│   └── ...
├── static/                 # 🖼️ CSS & Static Assets (if applicable)
├── requirements.txt        # 📦 Python Dependencies
├── setup.txt               # 🛠️ Hardware Wiring Guide
└── README.md               # 📄 Project Documentation
```

## 🛠️ Setup & Installation

### 1. Hardware Requirements & Wiring
**Microcontroller**: ESP32
**Sensors**: MAX30102 (Pulse/Oximeter), DHT11 (Temp/Humidity), MQ-7 (Air Quality), GSR Sensor.

**Wiring Configuration** (as per `setup.txt`):
- **ESP32 Power**: 3V3 -> VCC, GND -> GND
- **GSR Sensor**: SIG -> D2, VCC -> VCC, GND -> GND
- **DHT11**: DATA -> D15, VCC -> VCC, GND -> GND
- **MQ-7**: A0 -> D4, VCC -> VCC, GND -> GND
- **MAX30102**: SCL -> D18, SDA -> [Check Code/Pinout], VCC -> VCC, GND -> GND

### 2. Software Installation
1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd Health_moni
    ```

2.  **Install Dependencies**:
    Ensure you have Python 3.8+ installed.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Upload Firmware**:
    - Open `pakkwalafinlesp/pakkwalafinlesp.ino` in Arduino IDE.
    - Select your ESP32 board and COM port.
    - Upload the code to the ESP32.

4.  **Configure Credentials**:
    - Update `config.json` (if available) or environment variables with your Twilio credentials for SMS/WhatsApp alerts.

## 💻 Usage

### Running the Web Portal
Start the Flask server to enable the web interface and API endpoints.
```bash
python server.py
```
- Access the web interface at: `http://127.0.0.1:5000`

### Running the Desktop Dashboard
Launch the main monitoring application.
```bash
python pakkawalafinal.py
```
- The dashboard will open, connect to the sensors (via Serial/Bluetooth), and start displaying real-time data.

## 🏗️ Technologies Used
- **Programming Language**: Python 3.x, C++ (Arduino)
- **GUI Framework**: CustomTkinter, PyQtGraph, Tkinter
- **Web Framework**: Flask (HTML/CSS/JS)
- **Machine Learning**: Scikit-learn, Joblib, Pandas, NumPy
- **Hardware**: ESP32, MAX30102, DHT11, MQ-7
- **APIs**: Twilio (WhatsApp/SMS), Firebase (Optional)
