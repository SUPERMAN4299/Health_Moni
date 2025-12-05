from flask import Flask
import asyncio
import csv
import sys
import random
import logging
import re
from twilio.rest import Client
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
import requests
import string
import multiprocessing
import pyautogui
from threading import Lock
if sys.platform.startswith("win"):
    multiprocessing.set_start_method("spawn", force=True)
import socket
import random
import os
from datetime import datetime
os.environ["USE_TF"] = "0"
from twilio.rest import Client
os.environ["TRANSFORMERS_NO_TF_WARNING"] = "1"
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import time
import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
import serial
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
import threading
import webbrowser
import os
import subprocess
import platform
import re
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import json
import atexit

serial_port = None


def init_serial_port(port="COM6", baudrate=115200):
    global serial_port
    try:
        serial_port = serial.Serial(port, baudrate, timeout=1)
        print(f"[Serial] Connected to {port}")
    except Exception as e:
        print(f"[Serial Error] {e}")

def read_serial_loop():
    global serial_port
    print("[Serial] Read thread started")
    while True:
        try:
            if serial_port and serial_port.in_waiting:
                data = serial_port.readline().decode(errors="ignore").strip()
                if data:
                    print("[Sensor]", data)
        except Exception as e:
            print("[Serial Read Error]", e)
        time.sleep(0.05)

def close_serial():
    global serial_port
    try:
        if serial_port:
            serial_port.close()
            serial_port = None
            print("[Serial] Port closed")

    except Exception as e:
        print(f"[Serial] Close error: {e}")


def read_serial_portial_loop():
    global serial_port
    print("[Main] serial_portial read thread started")
    while True:
        try:
            if serial_port and serial_port.in_waiting:
                data = serial_port.readline().decode(errors="ignore").strip()
                if data:
                    print("[Sensor]", data)
        except Exception as e:
            print("[serial_portialLoopError]", e)
        time.sleep(0.05)


def start_serial_portial_thread():
    t = threading.Thread(target=read_serial_portial_loop, daemon=True)
    t.start()



# ---------------- Logging Setup ---------------- #
logger = logging.getLogger('HealthMonitor')
logging.basicConfig(
    filename=f'health_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ---------------- Exception Handling ---------------- #
def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            return None
    return wrapper

# ---------------- Security ---------------- #
@handle_exceptions
def hex_encode(text: str) -> str:
    return text.encode().hex()

@handle_exceptions
def hex_decode(hex_text: str) -> str:
    hex_text = (hex_text or "").strip()
    if not hex_text:
        return ""
    if len(hex_text) % 2 != 0:
        return ""
    try:
        return bytes.fromhex(hex_text).decode()
    except Exception as e:
        logger.error(f"Hex decode error: {e}")
        return ""

# --------- Destroying files --------- #
def clear_patient_form():
    for widget in fields.values():
        if isinstance(widget, ctk.CTkEntry):
            widget.delete(0, "end")
        elif isinstance(widget, ctk.CTkTextbox):
            widget.delete("1.0", "end")

# ---------------- Configurations ---------------- #
SESSION_FILE = "session.txt"
PATIENT_FILE = "patient_data1.json"
serial_portVER_URL = "http://127.0.0.1:5000/patient-data1"


# ---------------- Load Credentials ---------------- #
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"
stored_userial_port_enc = DEFAULT_USERNAME
stored_pass_enc = DEFAULT_PASSWORD
stored_mac_enc = ""
def load_serial_portver_credentials():
    global stored_userial_port_enc, stored_pass_enc, stored_mac_enc
    stored_userial_port_enc = DEFAULT_USERNAME
    stored_pass_enc = DEFAULT_PASSWORD
    stored_mac_enc = ""
    try:
        res = requests.get("http://127.0.0.1:5000/s1", timeout=5)
        s = res.text.strip()
        sec = s[0:10] if len(s) >= 10 else ""
        sec1 = s[10:20] if len(s) >= 20 else ""
        fetched_user = hex_decode(sec)
        fetched_pass = hex_decode(sec1)
        if fetched_user:
            stored_userial_port_enc = fetched_user
        if fetched_pass:
            stored_pass_enc = fetched_pass
        stored_mac_enc = "80:f3:da:5d:5d:fa"
    except Exception as e:
        print("[Init] Error loading credentials:", e)


os_name = os.name

# ---------------- Session Handling ---------------- #
def save_session():
    try:
        with open(SESSION_FILE, "w") as f:
            f.write("logged_in")
    except Exception:
        pass

def check_session():
    return os.path.exists(SESSION_FILE)

def clear_session():
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except Exception:
            pass

# ---------------- Globals for UI fields ---------------- #
fields = {}

# ---------------- Utility: safe local IP ---------------- #
'''
def get_local_ip(fallback="127.0.0.1"):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return fallback

local_ip = get_local_ip()
print(local_ip)
'''

# ---------------- Firebase (out) ---------------- #
'''
cred = credentials.Certificate("health-2025b-firebase-adminsdk-fbsvc-c147f969ca.json")
firebase_admin.initialize_app(cred)


def firedb_ai(out):
    """Stores an AI output string in Firebase Realtime Database"""
    ref = db.reference("/ai_outputs")  # 'ai_outputs' is your chosen path
    data = {
        "output": out,
        "timestamp": datetime.now().isoformat()
    }
    ref.push(data)  # Push creates a unique key for each entry
'''
# ---------------- Sensor file and state ---------------- #
filename = "sensor_data.json"
MAX_ENTRIES = 84600
REFRESH_INTERVAL = 2  # seconds (used by GUI scheduling & poller)
last_entry = None
last_count = 0
device_connected = False

# shared data protected by lock
HEART_DATA = 0
AIR_QUA_DATA = 0
GSR_DATA = 0
TEMP_DATA = 0.0
SPO2 = 0

# ---------------- BT scanning ---------------- #

# ---------------- SMS ---------------- #
# --------------- Configuration and Patient No. --------------- #
logger = logging.getLogger(__name__)


# Global variables

with open("config.json", "r") as f:
    cfg = json.load(f)

    account_sid = cfg["account_sid"]
    auth_token = cfg["auth_token"]

with open(PATIENT_FILE, "r") as f:
    pdata = json.load(f)
    Contact_No = pdata[0].get("Contact_No", "") if pdata else ""
    Emergency_No = pdata[0].get("Emergency_No", "") if pdata else ""



def send_whatsapp(body):
    
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=body,
        from_="+15677042248",
        to=Contact_No,
    )

    print(message.body)


# ---------------- Read sensor data ---------------- #


@handle_exceptions
def clean_sensor_line(line):
    """Clean and parse sensor data line"""
    if not line:
        return None
    
    # Remove any non-printable characters
    clean = re.sub(r'[^\x20-\x7E]', '', line)
    
    try:
        return json.loads(clean)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error after cleaning: {e}")
        return None

@handle_exceptions
def read_sensor_data():
    """Read and validate sensor data from serial port in a clean, safe manner"""
    global HEART_DATA, AIR_QUA_DATA, GSR_DATA, TEMP_DATA, SPO2

    if serial_port is None:
        logger.warning("Serial not initialized")
        return None

    try:
        # Check if new data available
        if serial_port.in_waiting > 0:
            raw = serial_port.readline()

            if not raw:
                return None

            try:
                line = raw.decode("utf-8", errors="replace").strip()
                data = clean_sensor_line(line)

            except Exception as e:
                logger.error(f"Sensor decode/parse error: {e}")
                return None
        current_data = {
            "HEART_DATA": HEART_DATA,
            "AIR_QUA_DATA": AIR_QUA_DATA,
            "GSR_DATA": GSR_DATA,
            "TEMP_DATA": TEMP_DATA,
            "SPO2": SPO2
        }

        heart_path = "BPM_data.txt"
        heart_file = current_data["HEART_DATA"]

        if heart_file is not None:
            # Count lines efficiently without loading the full file into memory
            try:
                with open(heart_path, 'r') as f:
                    line_count = sum(1 for _ in f)
            except FileNotFoundError:
                line_count = 0  # File doesn’t exist yet

            # Reset file after reaching 86,400 lines
            if line_count >= 86400:
                with open(heart_path, 'w') as f:
                    f.write("")  # Clear file content

            # Append new data
            with open(heart_path, 'a') as f:
                f.write(f"{heart_file}\n")

        #return current_data

    except serial.SerialException as e:
        logger.error(f"Serial port error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected sensor read error: {e}")
        return None

# ---------------- Patient Upload ---------------- #
def upload_data(master, data):
    try:
        if not os.path.exists(PATIENT_FILE):
            with open(PATIENT_FILE, "w") as f:
                json.dump([data], f, indent=4)

        with open(PATIENT_FILE, "rb") as f:
            files = {"file": f}
            try:
                response = requests.post(serial_portVER_URL, files=files, timeout=10)
            except Exception as e:
                master.after(0, lambda: messagebox.showerror("Error", f"Failed to contact serial_portver:\n{e}"))
                return

        if response.status_code == 200:
            master.after(0, lambda: messagebox.showinfo("Success", "Patient data saved & sent successfully!"))
            master.after(0, lambda: (save_session(), main_dash(master)))
        else:
            master.after(0, lambda: messagebox.showerror("Error", f"serial_portver error: {response.text}"))
    except Exception as e:
        master.after(0, lambda: messagebox.showerror("Error", f"Failed to save/send data:\n{e}"))


# ---------------- Validation + Submit (bound to UI) ---------------- #
def validate_and_submit(master):
    data = {}
    for name, widget in fields.items():
        if isinstance(widget, ctk.CTkEntry):
            data[name] = widget.get().strip()
        elif isinstance(widget, ctk.CTkTextbox):
            data[name] = widget.get("1.0", "end-1c").strip()
        elif isinstance(widget, ctk.CTkOptionMenu):
            data[name] = widget.get().strip()
        else:
            data[name] = getattr(widget, "get", lambda: "")().strip()

    if "Age" in data:
        try:
            age = int(data["Age"])
            if not 0 <= age <= 120:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Age must be 0-120.")
            return

    for ph_field in ("Contact_No", "Emergency_No"):
        if ph_field in data and data[ph_field]:
            phone = data[ph_field]
            if not phone.isdigit() or len(phone) != 10:
                messagebox.showerror("Input Error", f"{ph_field} must be 10 digits.")
                return

    if "Date of Birth (DD-MM-YYYY)" in data and data["Date of Birth (DD-MM-YYYY)"]:
        try:
            datetime.strptime(data["Date of Birth (DD-MM-YYYY)"], "%d-%m-%Y")
        except ValueError:
            messagebox.showerror("Input Error", "DOB must be DD-MM-YYYY.")
            return

    threading.Thread(target=upload_data, args=(master, data), daemon=True).start()

# ---------------- Fetch patient data (local -> serial_portver) ---------------- #
def fetch_patient_data():
    try:
        if os.path.exists(PATIENT_FILE):
            with open(PATIENT_FILE, "r", encoding="utf-8") as f:
                raw = f.read().strip()
                if raw:
                    try:
                        data = json.loads(raw)
                        if data:
                            return data
                    except json.JSONDecodeError as decode_err:
                        logger.warning("Corrupt local patient file, ignoring: %s", decode_err)
                else:
                    logger.info("Local patient file empty, skipping.")
        res = requests.get(serial_portVER_URL, timeout=5)
        if res.status_code == 200:
            try:
                data = res.json()
                if data:
                    return data
            except ValueError as decode_err:
                logger.warning("Remote patient JSON invalid: %s", decode_err)
        return None
    except Exception as e:
        print("Error fetching patient data:", e)
        messagebox.showerror("Error", f"Failed to fetch patient data:\n{e}")
        return None

# ---------------- Conditions and UI constants ---------------- #
PRIMARY_DARK_COLOR = "#101010"
SECONDARY_DARK_COLOR = "#2b2b2b"
TEXT_COLOR_PRIMARY = "white"
TEXT_COLOR_SECONDARY = "#999999"
TEXT_COLOR_TERTIARY = "#cccccc"
SUCCESS_COLOR = "#00cc66"
WARNING_COLOR = "#ffaa00"
CRITICAL_COLOR = "#ff4444"
BUTTON_BLUE_DARK = "#1976D2"
BUTTON_BLUE_HOVER_DARK = "#1565C0"
STAT_CARD_BG = "#252525"
PANEL_BG = "#202020"
ICON_COLOR = "#00aaff"
GRADIENT_START = "#007bff"
GRADIENT_END = "#00c6ff"

BPM_PATH = "file.txt"
BPM_DATA = []
max_points = 200  # store last 200 points for smooth scrolling graph

FONT_SIZE_LARGE = 36
FONT_SIZE_MEDIUM = 16
FONT_SIZE_SMALL = 11
FONT_SIZE_XSMALL = 10
FONT_SIZE_XXSMALL = 8

CORNER_RADIUS_LARGE = 20
CORNER_RADIUS_MEDIUM = 15
CORNER_RADIUS_SMALL = 10
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40
ICON_BUTTON_SIZE = 30
STATUS_LABEL_WIDTH = 45
STATUS_LABEL_HEIGHT = 20

PADDING_X = 20
PADDING_Y = 20
CARD_INNER_PADDING = 20
CARD_SPACING = 20

STATUS_GOOD = "GOOD"
STATUS_WARNING = "WARNING"
STATUS_CRITICAL = "CRITICAL"

ICON_HEART = "❤️"
ICON_AIR_QUALITY = "💨"
ICON_GSR = "⚡"
ICON_TEMP = "🌡️"
ICON_TRENDS = "📈"

UNIT_BPM = "BPM"
UNIT_AQI = "AQI"
UNIT_MICROS = "µS"
UNIT_CELSIUS = "°C"

DEFAULT_WINDOW_SIZE = "900x600"

# ---------------- Health logic helpers ---------------- #
def condition_heart_rate(hr):
    try:
        hr = int(hr)
    except Exception:
        return STATUS_CRITICAL
    if 60 <= hr <= 100:
        return STATUS_GOOD
    elif 50 <= hr < 60 or 101 <= hr <= 120:
        return STATUS_WARNING
    else:
        #send_whatsapp_alert("Critical Heart Rate detected!")
        return STATUS_CRITICAL

def condition_aqi(aqi):
    try:
        aqi = int(aqi)
    except Exception:
        return STATUS_CRITICAL
    if 0 <= aqi <= 100:
        return STATUS_GOOD
    elif 101 <= aqi <= 250:
        return STATUS_WARNING
    else:
        #send_whatsapp_alert("Poor Air Quality detected!")
        return STATUS_CRITICAL

def condition_gsr(gsr):
    try:
        gsr = float(gsr)
    except Exception:
        return STATUS_CRITICAL
    if 0 <= gsr <= 100:
        return STATUS_GOOD
    elif 101 <= gsr <= 250:
        return STATUS_WARNING
    else:
        #send_whatsapp_alert("Abnormal GSR detected!")
        return STATUS_CRITICAL

def condition_temp(temp):
    try:
        temp = float(temp)
    except Exception:
        return STATUS_CRITICAL
    if 36 <= temp <= 37.5:
        return STATUS_GOOD
    elif 35 <= temp < 36 or 37.6 <= temp <= 38.5:
        return STATUS_WARNING
    else:
        #send_whatsapp_alert("Abnormal Temperature detected!")
        return STATUS_CRITICAL

def status_to_color(status):
    if status == STATUS_GOOD:
        return SUCCESS_COLOR
    elif status == STATUS_WARNING:
        return WARNING_COLOR
    else:
        return CRITICAL_COLOR
# ---------------- Graph Window (pyqtgraph) ---------------- #
def launch_graph():
    """Launch the graph window in a separate process to avoid GUI toolkit conflicts"""
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "heartbsgload.py")
        if os.path.exists(script_path):
            subprocess.Popen(
                [sys.executable, script_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )
        else:
            messagebox.showerror("Error", f"Graph script not found: {script_path}")
    except Exception as e:
        logger.error(f"Failed to launch graph: {e}")
        messagebox.showerror("Error", f"Failed to launch graph window:\n{e}")

def read_sensor_data_dummy():
    global HEART_DATA, AIR_QUA_DATA, GSR_DATA, TEMP_DATA, SPO2
    with sensor_lock:
        HEART_DATA = np.random.randint(60, 100)
        AIR_QUA_DATA = np.random.randint(0, 150)
        GSR_DATA = np.random.randint(20, 80)
        TEMP_DATA = round(np.random.uniform(36, 38), 1)
        SPO2 = np.random.randint(90, 100)
    return {"HEART_DATA": HEART_DATA, "AIR_QUA_DATA": AIR_QUA_DATA,
            "GSR_DATA": GSR_DATA, "TEMP_DATA": TEMP_DATA, "SPO2": SPO2}

sensor_poll_stop = threading.Event()

# ---------------- Sensor poller ---------------- #
def sensor_poller():
    global HEART_DATA, AIR_QUA_DATA, GSR_DATA, TEMP_DATA, SPO2
    while not sensor_poll_stop.is_set():
        data = read_sensor_data()
        if data:
            with sensor_lock:
                HEART_DATA = data.get('HEART_DATA', HEART_DATA)
                AIR_QUA_DATA = data.get('AIR_QUA_DATA', AIR_QUA_DATA)
                GSR_DATA = data.get('GSR_DATA', GSR_DATA)
                TEMP_DATA = data.get('TEMP_DATA', TEMP_DATA)
                SPO2 = data.get('SPO2', SPO2)
        time.sleep(REFRESH_INTERVAL)


def get_clean_sensor_values():
    """Safely converts live sensor data into pure numeric values."""
    with sensor_lock:
        try: hr = int(HEART_DATA)
        except: hr = 0

        try: gsr = float(GSR_DATA)
        except: gsr = 0.0

        try: temperature = float(TEMP_DATA)
        except: temperature = 0.0

        try: spo2 = int(SPO2)
        except: spo2 = 0

    return hr, gsr, temperature, spo2


# start sensor poller right away in background
threading.Thread(target=sensor_poller, daemon=True).start()


# ---------------- BPM logger (write heart rate to data.txt) ---------------- #
file_lock = threading.Lock()

# ---------------- AI loop (background) ---------------- #
# --- Locks ---
prescription_lock = threading.Lock()
sensor_lock = threading.Lock()

# --- Global Variables ---
out = "AI not ready..."

model = joblib.load(r"F:\Health_moni\datasets\health_ai_final_ultra_best_ensemble.pkl")
label_disease = joblib.load(r"F:\Health_moni\datasets\label_disease.pkl")
label_past = joblib.load(r"F:\Health_moni\datasets\label_past.pkl")
scaler = joblib.load(r"F:\Health_moni\datasets\scaler_poly_final.pkl")

# Fit PolynomialFeatures using dummy feature row (11 base features)
poly = PolynomialFeatures(degree=2, include_bias=False)
poly.fit(np.zeros((1, 11)))   # 11 = number of base features


base_features = [
    "HeartRate", "GSR", "Temperature", "SpO2", "Age",
    "HR_Temp_Ratio", "Oxygen_Stress_Index", "Temp_Spo2_Interaction",
    "HRV_Index", "Thermal_Stress_Index", "Stress_Ratio"
]



def get_clean_patient_data(p):

    try:
        age = int(p.get("Age", 0))
    except:
        age = 0

    try:
        past_encoded = int(label_past.transform([p.get('Previous Disease', 'Other')])[0])
    except:
        past_encoded = 0

    return age, past_encoded


# --- Locks and dummy sensor variables (replace with your real ones) ---
prescription_lock = Lock()
sensor_lock = Lock()


def compute_features(hr, gsr, temperature, spo2, age, past_encoded):
    """Builds the complete feature vector for ML model."""

    # Hand-crafted features
    hr_temp_ratio = hr / (temperature + 1e-5)
    oxygen_stress_index = (100 - spo2) + (gsr / 1000)
    temp_spo2_interaction = temperature * (100 - spo2)
    hrv_index = 0.0  # HRV cannot be computed with single reading
    thermal_stress_index = (temperature - 36.5) * (gsr / 800)
    stress_ratio = (hr / 100) + (gsr / 800) - (spo2 / 95)

    base_vector = np.array([[
        hr, gsr, temperature, spo2, age,
        hr_temp_ratio, oxygen_stress_index,
        temp_spo2_interaction, hrv_index,
        thermal_stress_index, stress_ratio
    ]], dtype=float)

    poly_features = poly.transform(base_vector)

    final_vec = np.concatenate([poly_features, np.array([[past_encoded]])], axis=1)

    final_scaled = scaler.transform(final_vec)

    return final_scaled


def predict_disease_ml(hr, gsr, temperature, spo2, age, past_encoded):
    X_scaled = compute_features(hr, gsr, temperature, spo2, age, past_encoded)
    pred = model.predict(X_scaled)[0]
    disease = label_disease.inverse_transform([pred])[0]
    return disease

def get_disease_advice(disease):
    try:
        data = pd.read_csv(r"F:\Health_moni\datasets\logical_health_dataset.csv")
        if "PredictedDisease" in data.columns and "ShortAdvice" in data.columns:
            advice_map = data.groupby("PredictedDisease")["ShortAdvice"].first().to_dict()
            return advice_map.get(disease, "No advice available.")
    except:
        return "No advice available."

    return "No advice available."


def ai_loop():
    """Background AI loop — generates ML predictions + advice every cycle."""
    global out, model

    print("[AI] Background AI loop started.")

    while True:
        try:
      
            p = {}
            if os.path.exists(PATIENT_FILE):
                try:
                    with open(PATIENT_FILE, "r") as f:
                        pdata = json.load(f)
                        if pdata and isinstance(pdata, list):
                            p = pdata[0]
                except:
                    p = {}

            hr, gsr, temperature, spo2 = get_clean_sensor_values()

            age, past_encoded = get_clean_patient_data(p)

            try:
                disease = predict_disease_ml(hr, gsr, temperature, spo2, age, past_encoded)
            except Exception as e:
                print("[AI] ML prediction error:", e)
                disease = "Unknown"

            advice = get_disease_advice(disease)

            response = f"The predicted disease is {disease}. It is advised to {advice}."
           
            if not response.strip():
                response = "AI produced an empty response."

            with prescription_lock:
                out = response

            print("[AI] Updated advice:", response[:100], "...")

        except Exception as e:
            with prescription_lock:
                out = f"AI loop error: {str(e)}"
            print("[AI Loop Error]", e)

        time.sleep(120)

def calling_sleep30():
    last_30 = time.time()
    last_180 = time.time()
    while True:
        now = time.time()

        # Call every 30 seconds
        if now - last_30 >= 30:
            print("30s call:", out)
            last_30 = now

        # Call every 180 seconds
        if now - last_180 >= 50:
            print("180s call:", out)
            last_180 = now

        time.sleep(0.2)   

def logout(master):
    clear_session()

    for widget in master.winfo_children():
        widget.destroy()

# ---------------- Main Dashboard UI ---------------- #
def create_metric(parent, col, icon, title, value, unit, status, color, width=STATUS_LABEL_WIDTH):
    frame = ctk.CTkFrame(parent, fg_color=STAT_CARD_BG, corner_radius=CORNER_RADIUS_MEDIUM)
    frame.grid(row=0, column=col, padx=CARD_SPACING, pady=CARD_SPACING, sticky="nsew")
    frame.grid_columnconfigure(0, weight=1)

    # Icon + Title
    icon_title_frame = ctk.CTkFrame(frame, fg_color="transparent")
    icon_title_frame.pack(pady=(CARD_INNER_PADDING, 0))
    ctk.CTkLabel(icon_title_frame, text=icon,
                 font=ctk.CTkFont(size=FONT_SIZE_MEDIUM),
                 text_color=ICON_COLOR).pack(side="left", padx=(0, 5))
    ctk.CTkLabel(icon_title_frame, text=title,
                 font=ctk.CTkFont(size=FONT_SIZE_SMALL, weight="bold"),
                 text_color=TEXT_COLOR_SECONDARY).pack(side="left")

    # Value
    value_label = ctk.CTkLabel(frame, text=value,
                               font=ctk.CTkFont(size=FONT_SIZE_LARGE, weight="bold"),
                               text_color=TEXT_COLOR_PRIMARY)
    value_label.pack(pady=(0, 5))
    unit_label = ctk.CTkLabel(frame, text=unit,
                              font=ctk.CTkFont(size=FONT_SIZE_XSMALL),
                              text_color=TEXT_COLOR_SECONDARY)
    unit_label.pack()

    # Status badge
    badge = ctk.CTkFrame(frame, fg_color=color,
                         corner_radius=CORNER_RADIUS_SMALL,
                         width=width, height=STATUS_LABEL_HEIGHT)
    badge.pack(pady=(CARD_INNER_PADDING // 2, CARD_INNER_PADDING))
    status_label = ctk.CTkLabel(badge, text=status,
                                font=ctk.CTkFont(size=FONT_SIZE_XXSMALL, weight="bold"),
                                text_color=TEXT_COLOR_PRIMARY)
    status_label.pack(padx=5, pady=2)

    return {"value": value_label, "status": status_label, "badge": badge}

def main_dash(master):
    # --- Configure theme ---
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    master.title("Health Dashboard")
    master.geometry(DEFAULT_WINDOW_SIZE)
    master.configure(fg_color=PRIMARY_DARK_COLOR)
    master.grid_columnconfigure(0, weight=1)
    master.grid_rowconfigure(0, weight=1)

    # --- Main Frame ---
    main_frame = ctk.CTkFrame(master, fg_color=PRIMARY_DARK_COLOR)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=PADDING_X, pady=PADDING_Y)
    main_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
    main_frame.grid_rowconfigure((0, 1), weight=1)

    # --- Get initial values safely ---
    with sensor_lock:
        hr_val = HEART_DATA if HEART_DATA != 0 else "-"
        aqi_val = AIR_QUA_DATA if AIR_QUA_DATA != 0 else "-"
        gsr_val = GSR_DATA if GSR_DATA != 0 else "-"
        temp_val = TEMP_DATA if TEMP_DATA != 0 else "-"
        spo2_val = SPO2 if SPO2 != 0 else "-"

    # --- Calculate statuses ---
    hr_status = condition_heart_rate(hr_val)
    aqi_status = condition_aqi(aqi_val)
    gsr_status = condition_gsr(gsr_val)
    temp_status = condition_temp(temp_val)

    # --- Metrics dictionary (will store label refs) ---
    metrics_refs = {}

    # --- Metric cards ---
    metrics_refs["Heart Rate"] = create_metric(
        main_frame, 0, ICON_HEART, "Heart Rate", hr_val, UNIT_BPM,
        hr_status, status_to_color(hr_status)
    )
    metrics_refs["Air Quality Index"] = create_metric(
        main_frame, 1, ICON_AIR_QUALITY, "Air Quality Index", aqi_val,
        UNIT_AQI, aqi_status, status_to_color(aqi_status)
    )
    metrics_refs["GSR"] = create_metric(
        main_frame, 2, ICON_GSR, "GSR", gsr_val, UNIT_MICROS,
        gsr_status, status_to_color(gsr_status), width=70
    )
    metrics_refs["Temperature"] = create_metric(
        main_frame, 3, ICON_TEMP, "Temperature", temp_val, UNIT_CELSIUS,
        temp_status, status_to_color(temp_status), width=60
    )

    # --- Prescription (AI Output) Frame ---
    prescription_frame = ctk.CTkFrame(main_frame, fg_color=PANEL_BG, corner_radius=CORNER_RADIUS_MEDIUM)
    prescription_frame.grid(row=1, column=0, columnspan=2, padx=CARD_SPACING, pady=CARD_SPACING, sticky="nsew")
    prescription_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        prescription_frame, text="Prescription",
        font=ctk.CTkFont(size=FONT_SIZE_MEDIUM, weight="bold"),
        text_color=TEXT_COLOR_PRIMARY
    ).pack(anchor="w", padx=CARD_INNER_PADDING, pady=(10, 5))

    content_label = ctk.CTkLabel(
        prescription_frame, text=out, wraplength=420,
        font=ctk.CTkFont(size=FONT_SIZE_SMALL),
        text_color=TEXT_COLOR_TERTIARY, justify="left"
    )
    content_label.pack(anchor="w", padx=CARD_INNER_PADDING, pady=(5, CARD_INNER_PADDING))

    def update_prescription_label():
        with prescription_lock:
            txt = out
        content_label.configure(text=txt)
        master.after(2000, update_prescription_label)

    update_prescription_label()

    # --- Trends Frame ---
    trends_frame = ctk.CTkFrame(main_frame, fg_color=PANEL_BG, corner_radius=CORNER_RADIUS_MEDIUM)
    trends_frame.grid(row=1, column=2, columnspan=2, padx=CARD_SPACING, pady=CARD_SPACING, sticky="nsew")

    ctk.CTkLabel(
        trends_frame, text="Health Trends", font=ctk.CTkFont(size=FONT_SIZE_MEDIUM, weight="bold"),
        text_color=TEXT_COLOR_PRIMARY
    ).pack(pady=10)

    ctk.CTkButton(
        trends_frame, text="Launch Graph", command=launch_graph,
        font=ctk.CTkFont(size=13, weight="bold"),
        fg_color=(GRADIENT_START, GRADIENT_END), hover_color=(BUTTON_BLUE_HOVER_DARK, BUTTON_BLUE_DARK),
        width=BUTTON_WIDTH, height=BUTTON_HEIGHT, corner_radius=CORNER_RADIUS_LARGE,
        text_color=TEXT_COLOR_PRIMARY
    ).pack(pady=(0, 20))

    # --- Logout Button ---
    logout_button = ctk.CTkButton(
        master, text="Logout", command=lambda: logout(master),
        fg_color="red", hover_color="#cc0000", text_color=TEXT_COLOR_PRIMARY
    )
    logout_button.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

    # --- Live Metric Updater ---
    def update_live_metrics():
        with sensor_lock:
            hr = HEART_DATA
            aqi = AIR_QUA_DATA
            gsr = GSR_DATA
            temp = TEMP_DATA

        # Update visuals
        metrics_refs["Heart Rate"]["value"].configure(text=str(hr))
        metrics_refs["Air Quality Index"]["value"].configure(text=str(aqi))
        metrics_refs["GSR"]["value"].configure(text=str(gsr))
        metrics_refs["Temperature"]["value"].configure(text=str(temp))

        # Recalculate color/status
        metrics_refs["Heart Rate"]["badge"].configure(fg_color=status_to_color(condition_heart_rate(hr)))
        metrics_refs["Air Quality Index"]["badge"].configure(fg_color=status_to_color(condition_aqi(aqi)))
        metrics_refs["GSR"]["badge"].configure(fg_color=status_to_color(condition_gsr(gsr)))
        metrics_refs["Temperature"]["badge"].configure(fg_color=status_to_color(condition_temp(temp)))

        master.after(1000, update_live_metrics)  # Refresh every 1 second

    update_live_metrics()

# ---------------- Patient Information Form ---------------- #
def open_dashboard(master):
    for widget in master.winfo_children():
        widget.destroy()

    master.title("Patient Information Form")
    master.geometry("500x550")
    master.configure(bg="black")

    main_frame = ctk.CTkFrame(master, fg_color="#1c1c1c", corner_radius=15)
    main_frame.grid(row=0, column=0, padx=30, pady=20, sticky="nsew")

    master.grid_columnconfigure(0, weight=1)
    master.grid_rowconfigure(0, weight=1)

    heading_label = ctk.CTkLabel(main_frame, text="Filled by doctor or elder only.",
                                 font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                                 text_color="cyan")
    heading_label.grid(row=0, column=0, columnspan=2, pady=20, sticky="nsew")

    field_names = [
        ("Previous Disease", "🤒"),
        ("Safe Environment for Patient", "🏠"),
        ("Age", "🎂"),
        ("Contact_No", "📱"),
        ("Emergency_No", "🚨"),
        ("Date of Birth (DD-MM-YYYY)", "📅")
    ]

    # Clear `fields` then populate4
    fields.clear()

    for i, (name, icon) in enumerate(field_names):
        label = ctk.CTkLabel(
            main_frame,
            text=f"{icon} {name}:",
            anchor="w",
            text_color="white",
            font=("Segoe UI", 11, "bold")
        )
        label.grid(row=i + 1, column=0, padx=10, pady=10, sticky="w")

        if name == "Previous Disease":
            widget = ctk.CTkOptionMenu(
                main_frame,
                values=[
                    "Anemia",
                    "Asthma",
                    "Heart Disease",
                    "Hypertension",
                    "Other"
                ],
                fg_color="#222",
                button_color="#444",
                text_color="white",
                dropdown_hover_color="#0094ff",
                width=300,
                corner_radius=10
            )
            widget.set("Select past disease")
        elif name == "Safe Environment for Patient":
            widget = ctk.CTkOptionMenu(
                main_frame,
                values=[
                    "0 - 50 (Good)",
                    "51 - 100 (Moderate)",
                    "101 - 200 (Unhealthy for Sensitive Groups)",
                    "201 - 300 (Unhealthy)",
                    "301+ (Hazardous)"
                ],
                fg_color="#222",
                button_color="#444",
                text_color="white",
                dropdown_hover_color="#0094ff",
                width=300,
                corner_radius=10
            )
            widget.set("Select AQI range")
        else:
            widget = ctk.CTkEntry(
                main_frame,
                width=300,
                corner_radius=10,
                border_width=1,
                border_color="cyan"
            )

        widget.grid(row=i + 1, column=1, padx=10, pady=10, sticky="ew")
        fields[name] = widget

    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.grid(row=len(field_names) + 1, column=0, columnspan=2, pady=20)

    submit_button = ctk.CTkButton(button_frame, text="Submit",
                                  command=lambda: validate_and_submit(master),
                                  fg_color="#007bff", hover_color="#0094ff")
    submit_button.pack(side="left", padx=10)

    clear_button = ctk.CTkButton(button_frame, text="Clear",
                                 command=clear_patient_form,
                                 fg_color="#ff4444", hover_color="#ff6666")
    clear_button.pack(side="left", padx=10)

# ---------------- Login UI ---------------- #
entry_userial_port = "admin"
entry_pass = "admin"

def open_link(event=None):
    webbrowser.open("http://127.0.0.1:5000/query")

def submit():
    global entry_userial_port, entry_pass
    global stored_userial_port_enc, stored_pass_enc

    # Resolve current entry values whether widgets are rendered or we are running headless
    username = entry_userial_port.get().strip() if hasattr(entry_userial_port, "get") else str(entry_userial_port or "").strip()
    password = entry_pass.get().strip() if hasattr(entry_pass, "get") else str(entry_pass or "").strip()

    # Ensure latest credentials are loaded before validating
    if not stored_userial_port_enc or not stored_pass_enc:
        load_serial_portver_credentials()

    if not username or not password:
        messagebox.showerror("Error", "Please enter userial_portname and password")
        return

    # Compare with stored decoded credentials
    if username == stored_userial_port_enc and password == stored_pass_enc:
        # Check local IP matches expected device IP
        try:
            save_session()
            messagebox.showinfo("Success", "Login Successful! Device is Connected")
            patient_data = fetch_patient_data()
            if patient_data:
                main_dash(root)
            else:
                open_dashboard(root)
            
        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong: {e}")
    else:
        messagebox.showerror("Error", "Incorrect userial_portname or password")

def show_login_widgets(master_window):
    global entry_userial_port, entry_pass
    global stored_userial_port_enc, stored_pass_enc

    # Always make sure we have the latest credential cache before drawing the UI
    if not stored_userial_port_enc or not stored_pass_enc:
        load_serial_portver_credentials()

    for widget in master_window.winfo_children():
        widget.destroy()

    master_window.title("Login Page")
    master_window.geometry("600x550")
    master_window.resizable(False, False)
    master_window.configure(bg="black")

    frame = ctk.CTkFrame(master_window, corner_radius=20, width=500, height=450)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    title = ctk.CTkLabel(frame, text="Welcome Back!",
                         font=ctk.CTkFont(size=24, weight="bold"),
                         text_color="#00FFFF")
    title.pack(pady=(30, 10))

    subtitle = ctk.CTkLabel(frame, text="Please login to continue",
                            font=ctk.CTkFont(size=14), text_color="#FFFFFF")
    subtitle.pack(pady=(0, 20))

    entry_userial_port = ctk.CTkEntry(frame, placeholder_text="Userial_portname", width=400, height=40,
                              corner_radius=10, fg_color="#1C1C1C",
                              border_color="#00FFFF", border_width=2, text_color="white")
    entry_userial_port.pack(pady=15)
    if stored_userial_port_enc:
        entry_userial_port.insert(0, stored_userial_port_enc)

    entry_pass = ctk.CTkEntry(frame, placeholder_text="Password", width=400, height=40,
                              corner_radius=10, fg_color="#1C1C1C",
                              border_color="#00FFFF", border_width=2,
                              show="*", text_color="white")
    entry_pass.pack(pady=15)

    btn = ctk.CTkButton(frame, text="Login", width=400, height=45, corner_radius=10,
                        fg_color="#00FFFF", hover_color="#1E90FF",
                        text_color="black",
                        font=ctk.CTkFont(size=16, weight="bold"),
                        command=submit)
    btn.pack(pady=30)

    policy = ctk.CTkLabel(frame, text="Don't know your credentials? Click here",
                          font=ctk.CTkFont(size=12, underline=True),
                          text_color="#1E90FF", cursor="hand2")
    policy.pack(pady=10)
    policy.bind("<Button-1>", open_link)

# ---------------- Application start/entry ---------------- #
def show_login():
    global root
    root = ctk.CTk()
    # if session exists, try to open dashboard or patient form
    if check_session():
        patient_data = fetch_patient_data()
        if patient_data:
            main_dash(root)
        else:
            open_dashboard(root)
    else:
        show_login_widgets(root)
    root.mainloop()

def serial_portial_read_loop():
    global HEART_DATA, AIR_QUA_DATA, GSR_DATA, TEMP_DATA, SPO2
    
    init_serial_port()

    last_data_time = time.time()
    while True:
        try:
            raw = None

            if serial_port and serial_port.in_waiting:
                raw = serial_port.readline().decode(errors="ignore").strip()
                if raw:
                    data = clean_sensor_line(raw)
                    if data:
                        with sensor_lock:
                            HEART_DATA = data.get("HEART_DATA", HEART_DATA)
                            TEMP_DATA = data.get("TEMP_DATA", TEMP_DATA)
                            GSR_DATA = data.get("GSR_DATA", GSR_DATA)
                            AIR_QUA_DATA = data.get("AIR_QUA_DATA", AIR_QUA_DATA)
                            SPO2 = data.get("SPO2", SPO2)
                        #print("[LIVE SENSOR]", data)
                        last_data_time = time.time()

            # Detect if no data for 5 seconds
            if time.time() - last_data_time > 5:
                print("[Warning] No data received from ESP32 for 5+ seconds.")
                last_data_time = time.time()

        except serial.SerialException as e:
            print(f"[Serial Error] {e}. Attempting reconnect...")
            time.sleep(1)
            init_serial_port()

        except Exception as e:
            print("[serial_portialLoopError]", e)

        time.sleep(0.05)





# ---------------- Clean exit handling ---------------- #
def shutdown():
    # stop background poller (daemon threads will exit on process end anyway)
    sensor_poll_stop.set()

# ---------------- Run ---------------- #
if __name__ == "__main__":
    try:
        # 1) Init serial_portial safely
        # 2) Start background AI thread
        ai_thread = threading.Thread(target=ai_loop, daemon=True, name="AIThread")
        ai_thread.start()
        calling_sleep30_thread = threading.Thread(target=calling_sleep30, daemon=True)
        calling_sleep30_thread.start()
        
        print("[Main] AI thread started in background.")
        

        # 3) Start serial_portial read loop thread
        threading.Thread(target=serial_portial_read_loop, daemon=True).start()
        print("[Main] serial_portial read thread started")

        # 4) Tkinter UI (must run in main thread)
        show_login()

    except KeyboardInterrupt:
        print("\n[Main] KeyboardInterrupt, shutting down...")

    except Exception as e:
        print("[Main] Unexpected error:", e)

    finally:
        print("[Main] Cleaning up...")
        close_serial()
        atexit.register(sensor_poll_stop.set)
        shutdown()
        print("[Main] Shutdown complete ✅")
        pyautogui.hotkey('ctrl', 'v') 


