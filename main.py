from flask import Flask
import asyncio
import csv
from collections import deque
import openai
from bleak import BleakScanner, BleakClient
import requests
import socket
import time
import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
import multiprocessing
import numpy as np
from PyQt5 import QtWidgets
import pyqtgraph as pg
import sys
import webbrowser
import os
import subprocess
import platform
import re
from datetime import datetime
import json
import threading 

# ---------------- Security ---------------- #
def hex_encode(text: str) -> str:
    return text.encode().hex()

def hex_decode(hex_text: str) -> str:
    hex_text = hex_text.strip()
    if len(hex_text) % 2 != 0:
        return ""
    try:
        return bytes.fromhex(hex_text).decode()
    except Exception:
        return ""


# ---------------- Configurations ---------------- #
SESSION_FILE = "session.txt"
PATIENT_FILE = "patient_data1.json"
SERVER_URL = "http://127.0.0.1:5000/patient-data1"

# ---------------- Load Credentials ---------------- #
try:
    res = requests.get("http://127.0.0.1:5000/s1", timeout=5)
    s = res.text.strip()
    sec = s[0:10]
    sec1 = s[10:20]
    sec2 = s[20:124]
    sec3 = s[124:159]

    stored_user_enc = hex_decode(sec)
    stored_pass_enc = hex_decode(sec1)
    #stored_ip_enc = str(hex_decode(sec2).replace(":", "").replace("-", ""))   
    stored_ip_enc = str(hex_decode(sec2))

except Exception as e:
    print("Error loading credentials:", e)
    stored_user_enc = stored_pass_enc = stored_ip_enc = ""


os_name = os.name


# ---------------- Session Handling ---------------- #
def save_session():
    with open(SESSION_FILE, "w") as f:
        f.write("logged_in")

def check_session():
    return os.path.exists(SESSION_FILE)

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

# ---------------- Patient Form ---------------- #
fields = {}

def validate_and_submit(master):
    """Collect data and run upload in background"""
    data = {}
    for name, widget in fields.items():
        if isinstance(widget, ctk.CTkEntry):
            data[name] = widget.get()
        elif isinstance(widget, ctk.CTkTextbox):
            data[name] = widget.get("1.0", "end-1c")
        elif isinstance(widget, ctk.CTkOptionMenu):
            data[name] = widget.get()

    # Conditions

    if "Previous Disease" in data:
        
      if  len(data["Previous Disease"]) > 100:
        messagebox.showerror("Input Error", "Disease information is too long. Max 100 characters allowed.")
        return
        
    if "Age" in data:
        try:
            age = int(data["Age"])
            if age < 0 or age > 120:
                messagebox.showerror("Input Error", "Age must be a reasonable number.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Age must be a number.")
            return
        
    if "Contact No. (WhatsApp)" in data:
        try:
            contact = int(data["Contact No. (WhatsApp)"])
            if len(data["Contact No. (WhatsApp)"]) < 10 or len(data["Contact No. (WhatsApp)"])> 10:
                messagebox.showerror("Input Error", "Contact number must be at least 10 digits.")
                return

        except ValueError:
            messagebox.showerror("Intut Error","Please enter the conatact no. or enter the conatact no")            
        
    if "Emergency No. (WhatsApp)" in data:
        try:
            emergen_contact = int(data["Emergency No. (WhatsApp)"])
            if len(data["Emergency No. (WhatsApp)"]) < 10 or len(data["Emergency No. (WhatsApp)"]) > 10:
                messagebox.showerror("Input Error", "Emergency Contact number must be at least 10 digits.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Please enter the emergency conatact no. or enter the conatact no")
            return  
            


    if "Date of Birth (DD-MM-YYYY)" in data:
        try:
            datetime.strptime(data["Date of Birth (DD-MM-YYYY)"], "%d-%m-%Y")
        except ValueError:
            messagebox.showerror("Input Error", "Date of Birth must be in DD-MM-YYYY format.")
            return

    # Run upload in background
    threading.Thread(target=upload_data, args=(master, data), daemon=True).start()


# ---------- Sending P-info on the server --------- #
def upload_data(master, data):
    """Save JSON and send to server (background thread)"""
    try:
        # If file already exists → block further writes
        if os.path.exists(PATIENT_FILE):
            messagebox.showwarning("Save Blocked", "Patient data already exists and cannot be modified!")
            return

        with open(PATIENT_FILE, "w") as f:
            json.dump([data], f, indent=4)

        with open(PATIENT_FILE, "rb") as f:
            files = {"file": f}
            response = requests.post(SERVER_URL, files=files, timeout=10)

        if response.status_code == 200:
            messagebox.showinfo("Success", "Patient data saved & sent successfully!")
            save_session()
            main_dash(master)
        else:
            messagebox.showerror("Error", f"Server error: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save/send data:\n{e}")

# --------- Destroying files --------- #
def clear_patient_form():
    for widget in fields.values():
        if isinstance(widget, ctk.CTkEntry):
            widget.delete(0, "end")
        elif isinstance(widget, ctk.CTkTextbox):
            widget.delete("1.0", "end")


# --------- Data upload on the server --------- #
def upload_data(master, data):
    """Save JSON and send to server (background thread)"""
    try:
        # Save locally only if not already saved
        if not os.path.exists(PATIENT_FILE):
            with open(PATIENT_FILE, "w") as f:
                json.dump([data], f, indent=4)

        # Always send to server
        with open(PATIENT_FILE, "rb") as f:
            files = {"file": f}
            response = requests.post(SERVER_URL, files=files, timeout=10)

        if response.status_code == 200:
            messagebox.showinfo("Success", "Patient data saved & sent successfully!")
            save_session()
            main_dash(master)
        else:
            messagebox.showerror("Error", f"Server error: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save/send data:\n{e}")

    return None

# ---------- Taking Data from server -------- #

def fetch_patient_data():
    try:
        # 1. Check local file
        if os.path.exists(PATIENT_FILE):
            with open(PATIENT_FILE, "r") as f:
                data = json.load(f)
                if data:
                    return data

        # 2. Check server
        url = SERVER_URL.replace("/patient-data1", "/get-patient-data1")  # adjesment of routing 
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data:
                return data

        return None
    except Exception as e:
        print("Error fetching patient data:", e)
        return None


# --------- Logout --------- #
def logout(master):
    clear_session()

    for widget in master.winfo_children():
        widget.destroy()

    show_login_widgets(master)




# ------------ Taking sensor data in .json ------------- #

filename = "sensor_data.json"

# --- Max entries (same as ESP32) ---
MAX_ENTRIES = 84600

# --- Refresh interval (seconds) ---
REFRESH_INTERVAL = 2

# --- State memory ---
last_entry = None
last_count = 0

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as ip_local:
    ip_local.connect(("8.8.8.8", 80))
    local_ip = ip_local.getsockname()[0]

def connection():
    if local_ip == stored_ip_enc:
        device_connected = True
        return device_connected
    else:
        device_connected = False
        return device_connected
        

def read_sensor_data():
    if not os.path.exists(filename):
        return None

    try:
        with open(filename, "r") as f:
            data = json.load(f)
        if not data:
            return None
        return data
    except json.JSONDecodeError:
        # Happens if ESP32 is still writing to the file
        return None
# ------------ Artificial Intelegence ------------ #

##################################################################

# ---------------- GUI Windows ---------------- #
# ---------------- Utilites ---------------- #
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

# ---------------- Fonts & Sizes ---------------- #
FONT_SIZE_LARGE = 36
FONT_SIZE_MEDIUM = 16
FONT_SIZE_SMALL = 11
FONT_SIZE_XSMALL = 10
FONT_SIZE_XXSMALL = 8

# ---------------- Dimensions ---------------- #
CORNER_RADIUS_LARGE = 20
CORNER_RADIUS_MEDIUM = 15
CORNER_RADIUS_SMALL = 10
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 40
ICON_BUTTON_SIZE = 30
STATUS_LABEL_WIDTH = 45
STATUS_LABEL_HEIGHT = 20

# ---------------- Spacing ---------------- #
PADDING_X = 20
PADDING_Y = 20
CARD_INNER_PADDING = 20
CARD_SPACING = 20

# ---------------- Status ---------------- #
STATUS_GOOD = "GOOD"
STATUS_WARNING = "WARNING"
STATUS_CRITICAL = "CRITICAL"

# ---------------- Main data (Live) ---------------- #

while True:
    sensor_data = read_sensor_data()

    if sensor_data:
        total_entries = len(sensor_data)
        last = sensor_data[-1]

        # Detect new data (file grew)
        if total_entries > last_count:
            connection()
            last_entry = last
            last_count = total_entries

            HEART_DATA = last['Heart_Rate']
            AIR_QUA_DATA = last['AQI']
            GSR_DATA = last['GSR']
            TEMP_DATA = last['Temperature']
            break

            if total_entries < MAX_ENTRIES:
                print(f"Appended new entry. Total entries: {total_entries}\n")
            else:
                print(f"Overwrote oldest entry. Buffer full ({MAX_ENTRIES} entries)\n")

        else:
            # No new entries since last check
            if last_entry:
                if connection():
                    HEART_DATA = last_entry['Heart_Rate']
                    AIR_QUA_DATA = last_entry['AQI']
                    GSR_DATA = last_entry['GSR']
                    TEMP_DATA = last_entry['Temperature']
                connection()
    else:
        pass
        #main_dash(master)
        #messagebox.showerror("Error","Start Your device")
        #break
    time.sleep(REFRESH_INTERVAL)


        
# ---------------- Icons ---------------- #
ICON_HEART = "❤️"
ICON_AIR_QUALITY = "💨"
ICON_GSR = "⚡"
ICON_TEMP = "🌡️"
ICON_TRENDS = "📈"

# ---------------- Units ---------------- #
UNIT_BPM = "BPM"
UNIT_AQI = "AQI"
UNIT_MICROS = "µS"
UNIT_CELSIUS = "°C"

# ---------------- Window ---------------- #
DEFAULT_WINDOW_SIZE = "800x500"

# -------------- Conditions for Level data -------------- #

def condition_heart_rate(hr):
    if 60 <= hr <= 100:
        return STATUS_GOOD
    elif 101 <= hr <= 120 or 50 <= hr < 60:
        return STATUS_WARNING
    else:
        return STATUS_CRITICAL
    
def condition_aqi(aqi):
    if 0 <= aqi <= 50:
        return STATUS_GOOD
    elif 51 <= aqi <= 100:
        return STATUS_WARNING
    else:
        return STATUS_CRITICAL
    
def condition_gsr(gsr):
    if 0 <= gsr <= 50:
        return STATUS_GOOD
    elif 51 <= gsr <= 100:
        return STATUS_WARNING
    else:
        return STATUS_CRITICAL

def condition_temp(temp):
    if 36 <= temp <= 37.5:
        return STATUS_GOOD
    elif 37.6 <= temp <= 38.5 or 35 <= temp < 36:
        return STATUS_WARNING
    else:
        return STATUS_CRITICAL
    

# ---------------- Graph Window ---------------- #
def run_graph():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    win = pg.plot()
    win.setWindowTitle("Heart Rate")
    data1 = np.zeros(380)
    curve1 = win.plot(data1, pen="w")
    win.setXRange(200, 380)
    last_line = 0

    def update():
        nonlocal data1, last_line
        try:
            with open("data.txt", "r") as f:
                lines = f.readlines()

                # Detect reset
                if len(lines) < last_line:
                    print("File reset detected, continuing...")
                    last_line = 0
                    data1 = np.zeros_like(data1)

                if len(lines) > last_line:
                    new_lines = lines[last_line:]
                    for line in new_lines:
                        try:
                            new_value = int(line.strip())
                        except:
                            continue
                        data1[:-1] = data1[1:]
                        data1[-1] = new_value

                    last_line = len(lines)

                curve1.setData(data1)
        except Exception as e:
            print("Error:", e)

    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(500)

    win.show()
    sys.exit(app.exec_())

def launch_graph():
    """Launch PyQtGraph in a separate process"""
    p = multiprocessing.Process(target=run_graph)
    p.start()



def main_dash(master):
    # ----------------- Global Config ----------------- #
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    master.title("Health Dashboard")
    master.geometry(DEFAULT_WINDOW_SIZE)
    master.configure(fg_color=PRIMARY_DARK_COLOR)

    master.grid_columnconfigure(0, weight=1)
    master.grid_rowconfigure(0, weight=1)

    # ----------------- Main Frame ----------------- #
    main_frame = ctk.CTkFrame(master, fg_color=PRIMARY_DARK_COLOR)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=PADDING_X, pady=PADDING_Y)
    main_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
    main_frame.grid_rowconfigure((0, 1), weight=1)

    # ----------------- Metric Card ----------------- #
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

        # Return references for live update
        return {"value": value_label, "status": status_label, "badge": badge}

    # ----------------- Status to Color ----------------- #
    def status_to_color(status):
        if status == STATUS_GOOD:
            return SUCCESS_COLOR
        elif status == STATUS_WARNING:
            return WARNING_COLOR
        else:
            return CRITICAL_COLOR

    # Initial metric values
    sensor_data = read_sensor_data()
    if sensor_data:
        last = sensor_data[-1]
        HEART_DATA = last['Heart_Rate']
        AIR_QUA_DATA = last['AQI']
        GSR_DATA = last['GSR']
        TEMP_DATA = last['Temperature']
    else:
        HEART_DATA = AIR_QUA_DATA = GSR_DATA = TEMP_DATA = 0

    # Compute initial statuses
    hr_status = condition_heart_rate(HEART_DATA)
    aqi_status = condition_aqi(AIR_QUA_DATA)
    gsr_status = condition_gsr(GSR_DATA)
    temp_status = condition_temp(TEMP_DATA)

    # ----------------- Create Metrics ----------------- #
    metrics_refs = {}
    metrics_refs["Heart Rate"] = create_metric(main_frame, 0, ICON_HEART, "Heart Rate", HEART_DATA, UNIT_BPM,
                                              hr_status, status_to_color(hr_status))
    metrics_refs["Air Quality Index"] = create_metric(main_frame, 1, ICON_AIR_QUALITY, "Air Quality Index",
                                                     AIR_QUA_DATA, UNIT_AQI, aqi_status, status_to_color(aqi_status))
    metrics_refs["GSR"] = create_metric(main_frame, 2, ICON_GSR, "GSR", GSR_DATA, UNIT_MICROS,
                                        gsr_status, status_to_color(gsr_status), width=70)
    metrics_refs["Temperature"] = create_metric(main_frame, 3, ICON_TEMP, "Temperature", TEMP_DATA, UNIT_CELSIUS,
                                                temp_status, status_to_color(temp_status), width=60)

    # ----------------- Bottom Section ----------------- #
    # Prescription (left)
    prescription_frame = ctk.CTkFrame(main_frame, fg_color=PANEL_BG, corner_radius=CORNER_RADIUS_MEDIUM)
    prescription_frame.grid(row=1, column=0, columnspan=2, padx=CARD_SPACING, pady=CARD_SPACING, sticky="nsew")
    prescription_frame.grid_columnconfigure(0, weight=1)

    settings_btn = ctk.CTkButton(prescription_frame, text="⚙", width=ICON_BUTTON_SIZE, height=ICON_BUTTON_SIZE,
                                 fg_color="transparent", text_color=TEXT_COLOR_TERTIARY,
                                 hover_color="#3a3a3a", font=ctk.CTkFont(size=FONT_SIZE_MEDIUM))
    settings_btn.place(x=CARD_INNER_PADDING, y=CARD_INNER_PADDING)

    prescription_header = ctk.CTkFrame(prescription_frame, fg_color="transparent")
    prescription_header.pack(fill="x", padx=CARD_INNER_PADDING, pady=(CARD_INNER_PADDING, 5))

    ctk.CTkLabel(prescription_header, text="Prescription",
                 font=ctk.CTkFont(size=FONT_SIZE_MEDIUM, weight="bold"),
                 text_color=TEXT_COLOR_PRIMARY).pack(anchor="w")

    prescription_text = """Take ECOSPRIN-AV 75/20 Capsule,  
and DRL cardiovascular 100mg
Tablet(white) every 3 hours.
Monitor vitals daily. Consult
physician."""  

    content_label = ctk.CTkLabel(prescription_frame, text=prescription_text,
                                 font=ctk.CTkFont(size=FONT_SIZE_SMALL),
                                 text_color=TEXT_COLOR_TERTIARY,
                                 justify="left")
    content_label.pack(anchor="w", padx=CARD_INNER_PADDING, pady=(5, CARD_INNER_PADDING))

    # Trends (right)
    trends_frame = ctk.CTkFrame(main_frame, fg_color=PANEL_BG, corner_radius=CORNER_RADIUS_MEDIUM)
    trends_frame.grid(row=1, column=2, columnspan=2, padx=CARD_SPACING, pady=CARD_SPACING, sticky="nsew")
    trends_frame.grid_columnconfigure(0, weight=1)
    trends_frame.grid_rowconfigure(0, weight=1)
    trends_frame.configure(border_width=1, border_color="#3a3a3a")

    trends_header_frame = ctk.CTkFrame(trends_frame, fg_color="transparent")
    trends_header_frame.pack(pady=(CARD_INNER_PADDING, CARD_INNER_PADDING // 2))

    ctk.CTkLabel(trends_header_frame, text=ICON_TRENDS,
                 font=ctk.CTkFont(size=FONT_SIZE_MEDIUM),
                 text_color=ICON_COLOR).pack(side="left", padx=(0, 5))
    ctk.CTkLabel(trends_header_frame, text="Health Trends",
                 font=ctk.CTkFont(size=FONT_SIZE_MEDIUM, weight="bold"),
                 text_color=TEXT_COLOR_PRIMARY).pack(side="left")

    launch_btn = ctk.CTkButton(trends_frame, text="Launch Graph",
                               font=ctk.CTkFont(size=13, weight="bold"),
                               fg_color=(GRADIENT_START, GRADIENT_END),
                               hover_color=(BUTTON_BLUE_HOVER_DARK, BUTTON_BLUE_DARK),
                               width=BUTTON_WIDTH, height=BUTTON_HEIGHT, corner_radius=CORNER_RADIUS_LARGE,
                               text_color=TEXT_COLOR_PRIMARY,
                               command=launch_graph)
    launch_btn.pack(pady=(0, CARD_INNER_PADDING))

    refresh_frame = ctk.CTkFrame(trends_frame, fg_color="transparent")
    refresh_frame.pack(side="bottom", pady=(CARD_INNER_PADDING // 2, CARD_INNER_PADDING))

    ctk.CTkLabel(refresh_frame, text="Heart Beat (Live)",
                 font=ctk.CTkFont(size=9), text_color="#666666").pack()

    # Logout button
    logout_button = ctk.CTkButton(master, text="Logout",
                                  command=lambda: logout(master),
                                  fg_color="red", hover_color="#cc0000",
                                  text_color=TEXT_COLOR_PRIMARY)
    logout_button.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

    # ----------------- Live Update Function ----------------- #
    def update_live_data():
        sensor_data = read_sensor_data()
        if sensor_data:
            last = sensor_data[-1]

            # Update Heart Rate
            hr_status = condition_heart_rate(last['Heart_Rate'])
            metrics_refs["Heart Rate"]["value"].configure(text=last['Heart_Rate'])
            metrics_refs["Heart Rate"]["status"].configure(text=hr_status)
            metrics_refs["Heart Rate"]["badge"].configure(fg_color=status_to_color(hr_status))

            # Update AQI
            aqi_status = condition_aqi(last['AQI'])
            metrics_refs["Air Quality Index"]["value"].configure(text=last['AQI'])
            metrics_refs["Air Quality Index"]["status"].configure(text=aqi_status)
            metrics_refs["Air Quality Index"]["badge"].configure(fg_color=status_to_color(aqi_status))

            # Update GSR
            gsr_status = condition_gsr(last['GSR'])
            metrics_refs["GSR"]["value"].configure(text=last['GSR'])
            metrics_refs["GSR"]["status"].configure(text=gsr_status)
            metrics_refs["GSR"]["badge"].configure(fg_color=status_to_color(gsr_status))

            # Update Temperature
            temp_status = condition_temp(last['Temperature'])
            metrics_refs["Temperature"]["value"].configure(text=last['Temperature'])
            metrics_refs["Temperature"]["status"].configure(text=temp_status)
            metrics_refs["Temperature"]["badge"].configure(fg_color=status_to_color(temp_status))

        else:
        # Device not connected 
            messagebox.showerror("Device Status", "Device is not connected!")
            time.sleep(10)
        master.after(REFRESH_INTERVAL * 1000, update_live_data)

    # Start live updates
    update_live_data()


def open_dashboard(master):
    for widget in master.winfo_children():
        master.after(100, lambda:widget.destroy())

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
        ("Contact No. (WhatsApp)", "📱"),
        ("Emergency No. (WhatsApp)", "🚨"),
        ("Date of Birth (DD-MM-YYYY)", "📅")
    ]

    for i, (name, icon) in enumerate(field_names):
        label = ctk.CTkLabel(main_frame, text=f"{icon} {name}:", anchor="w",
                             text_color="white", font=("Segoe UI", 11, "bold"))
        label.grid(row=i + 1, column=0, padx=10, pady=10, sticky="w")

        if name == "Previous Disease":
            entry = ctk.CTkTextbox(main_frame, width=300, height=80,
                                   corner_radius=10, border_width=1, border_color="cyan")
        elif name == "Safe Environment for Patient":
            entry = ctk.CTkOptionMenu(main_frame,
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
                                      corner_radius=10)
            entry.set("Select AQI Range")
        else:
            entry = ctk.CTkEntry(main_frame, width=300, corner_radius=10,
                                 border_width=1, border_color="cyan")

        entry.grid(row=i + 1, column=1, padx=10, pady=10, sticky="ew")
        fields[name] = entry

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


# ---------------- Login ---------------- #
def submit():
    username = entry_user.get()
    password = entry_pass.get()
    ip_local = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    if not username or not password:
        messagebox.showerror("Error", "Please enter username and password")
        return    
    


    if username == stored_user_enc and password == stored_pass_enc:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as ip_local:
                ip_local.connect(("8.8.8.8", 80))
                local_ip = ip_local.getsockname()[0]

            if stored_ip_enc == local_ip:
                save_session()
                messagebox.showinfo("Success", f"Login Successful! Device is Connected")
                patient_data = fetch_patient_data()
                if patient_data:
                    main_dash(root)
                else:
                    open_dashboard(root)
            else:
                messagebox.showerror("Your device is not connected by via network.")
        except Exception as e:
            pass
            messagebox.showerror("Error! Something went wrong.")
    else:
        messagebox.showerror("Error", "Incorrect username or password")        


            
            
def open_link(event=None):
    webbrowser.open("http://127.0.0.1:5000/query")

def show_login_widgets(master_window):
    global entry_user, entry_pass
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

    entry_user = ctk.CTkEntry(frame, placeholder_text="Username", width=400, height=40,
                              corner_radius=10, fg_color="#1C1C1C",
                              border_color="#00FFFF", border_width=2, text_color="white")
    entry_user.pack(pady=15)

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

# ---------------- Start ---------------- #
def show_login():
    global root
    root = ctk.CTk()
    if check_session():
        patient_data = fetch_patient_data()
        if patient_data:
            main_dash(root)
        else:
            open_dashboard(root)
    else:
        show_login_widgets(root)
    root.mainloop()


if __name__ == '__main__':
    show_login()
