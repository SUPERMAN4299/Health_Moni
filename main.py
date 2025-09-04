from flask import Flask
import requests
import customtkinter as ctk
from tkinter import messagebox
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
    """Encode normal text into hex"""
    return text.encode().hex()

def hex_decode(hex_text: str) -> str:
    """Decode hex string safely"""
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
    sec2 = s[20:55]

    stored_user_enc = hex_decode(sec)
    stored_pass_enc = hex_decode(sec1)
    DEVICE_MAC = hex_decode(sec2)

except Exception as e:
    print("Error loading credentials:", e)
    stored_user_enc = stored_pass_enc = DEVICE_MAC = ""

# -------------- MAC check -------------- #
DEVICE_MAC = DEVICE_MAC.lower()
os_name = platform.system().lower()

mac_list = []
try:
    if os_name == "windows":
        cmd = 'powershell "Get-PnpDevice -Class Bluetooth | Select-Object -Property Name,InstanceId"'
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        output = result.stdout
    else:
        output = subprocess.check_output("ip neigh", shell=True, text=True)

    matches = re.findall(r'DEV_([0-9A-F]{12})', output, re.IGNORECASE)
    mac_list = [m.lower() for m in matches]
except Exception as e:
    print("Bluetooth check failed:", e)

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
    if "Age" in data:
        try:
            age = int(data["Age"])
            if age < 0 or age > 120:
                messagebox.showerror("Input Error", "Age must be a reasonable number.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Age must be a number.")
            return

    if "Date of Birth (DD-MM-YYYY)" in data:
        try:
            datetime.strptime(data["Date of Birth (DD-MM-YYYY)"], "%d-%m-%Y")
        except ValueError:
            messagebox.showerror("Input Error", "Date of Birth must be in DD-MM-YYYY format.")
            return

    # Run upload in background
    threading.Thread(target=upload_data, args=(master, data), daemon=True).start()

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

def clear_patient_form():
    for widget in fields.values():
        if isinstance(widget, ctk.CTkEntry):
            widget.delete(0, "end")
        elif isinstance(widget, ctk.CTkTextbox):
            widget.delete("1.0", "end")

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

def fetch_patient_data():
    """Check if patient data exists (server or local file)"""
    try:
        # 1. Check local file
        if os.path.exists(PATIENT_FILE):
            with open(PATIENT_FILE, "r") as f:
                data = json.load(f)
                if data:
                    return data

        # 2. Check server
        url = SERVER_URL.replace("/patient-data1", "/get-patient-data1")  # adjust route
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data:
                return data

        return None
    except Exception as e:
        print("Error fetching patient data:", e)
        return None



def logout(master):
    clear_session()

    for widget in master.winfo_children():
        widget.destroy()

    show_login_widgets(master)


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


# ---------------- GUI Windows ---------------- #
def main_dash(master):
    for widget in master.winfo_children():
        master.after(100, lambda: widget.destroy())

    master.title("Dashboard")
    master.geometry("500x500")
    master.configure(bg="black")

    main_frame = ctk.CTkFrame(master, fg_color="#1c1c1c", corner_radius=15)
    main_frame.grid(row=0, column=0, padx=30, pady=20, sticky="nsew")

    master.grid_columnconfigure(0, weight=1)
    master.grid_rowconfigure(0, weight=1)

    ctk.CTkLabel(main_frame, text="✅ Main Dashboard",
                 font=ctk.CTkFont(size=20, weight="bold"),
                 text_color="cyan").grid(row=0, column=0, pady=40, sticky="nsew")

    logout_button = ctk.CTkButton(main_frame, text="Logout",
                                  command=lambda: logout(master),
                                  fg_color="red", hover_color="#cc0000")
    logout_button.grid(row=1, column=0, pady=20)


    #logout_button.grid(row=10, column=0, columnspan=2, pady=20, sticky="se")
    #logout_button.pack(pady=20)

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

    logout_button = ctk.CTkButton(master, text="Logout",
                                  command=lambda: logout(master),
                                  fg_color="red", hover_color="#cc0000")
    logout_button.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

# ---------------- Login ---------------- #
def submit():
    username = entry_user.get()
    password = entry_pass.get()

    if not username or not password:
        messagebox.showerror("Error", "Please enter username and password")
        return

    if username == stored_user_enc and password == stored_pass_enc:
        if DEVICE_MAC in mac_list:
            save_session()
            messagebox.showinfo("Success", "Login Successful and Device Connected!")

            # ✅ Check server for patient data
            patient_data = fetch_patient_data()
            if patient_data:
                main_dash(root)   # go directly to dashboard if data exists
            else:
                open_dashboard(root)  # else, show patient info form
        else:
            messagebox.showerror("Device Not Connected", "Your device is not connected.")
    else:
        messagebox.showerror("Failed", "Invalid Username or Password")


def open_link(event=None):
    webbrowser.open("http://127.0.0.1:5000/query")

def show_login_widgets(master_window):
    global entry_user, entry_pass
    master_window.title("Login Page")
    master_window.geometry("500x500")
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
