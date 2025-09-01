from flask import Flask
import requests
import customtkinter as ctk
from tkinter import messagebox
import webbrowser
import os
import threading
import subprocess
import platform  
import re   


# ---------------- Security (Encoding / Decoding) ---------------- #


def hex_encode(text: str) -> str:
    """Encode normal text into hex"""
    return text.encode().hex()

def hex_decode(hex_text: str) -> str:
    """Decode hex string safely"""
    hex_text = hex_text.strip()
    
    if len(hex_text) % 2 != 0:  # must be even length
        print("❌ Invalid hex string length:", len(hex_text))
        return ""

    try:
        return bytes.fromhex(hex_text).decode()
    except Exception as e:
        print("❌ Hex decode error:", e, " | Input:", hex_text)
        return ""

# ---------------- Built-in Encoded Credentials ---------------- #

try:
    res = requests.get("http://127.0.0.1:5000/s")
    s = res.text.strip()  
    
    # Slice the string
    sec = s[0:10]
    sec1 = s[10:20]
    sec2 = s[20:55]
    
    # Decode
    stored_user_enc = hex_decode(sec)
    stored_pass_enc = hex_decode(sec1)
    DEVICE_MAC = hex_decode(sec2) 
  
    

except requests.exceptions.RequestException as e:
    print("Error:", e)
except ValueError as e:
    print("Hex decode error:", e)



# -------------- MAC check -------------- #

    """
    Check if a device with the given MAC address is connected (Linux or Windows)
"""
DEVICE_MAC = DEVICE_MAC.lower()
os_name = platform.system().lower()

try:
    if os_name == "windows":

        cmd = 'powershell "Get-PnpDevice -Class Bluetooth | Select-Object -Property Name,InstanceId"'
        result=subprocess.run(cmd, capture_output=True, text=True, shell=True)
    
        output = result.stdout
    else:  # Linux or others
        output = subprocess.check_output("ip neigh", shell=True, text=True)
except subprocess.CalledProcessError:
    messagebox.showerror("Error", "Failed to fetch network devices.")
    False

# Extract all MAC addresses
matches = re.findall(r'DEV_([0-9A-F]{12})', output, re.IGNORECASE)
mac_list = [m.lower() for m in matches]

#target_mac in mac_list

# ---------------- Submit Function ---------------- #
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
            root.withdraw()
            open_dashboard()
        else:
            messagebox.showerror(
                "Device Not Connected",
                "Your device is not connected. Please connect the device and try again."
            )
    else:
        messagebox.showerror("Failed", "Invalid Username or Password")

# ---------------- Session Handling ---------------- #
SESSION_FILE = "session.txt"

def save_session():
    with open(SESSION_FILE, "w") as f:
        f.write("logged_in")

def check_session():
    return os.path.exists(SESSION_FILE)

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)



# ---------------- Dashboard ---------------- #
def open_dashboard():
    dash = ctk.CTkToplevel()
    dash.title("Dashboard")
    dash.geometry("400x300")
    ctk.CTkLabel(dash, text="Welcome to Dashboard!",
                 font=ctk.CTkFont(size=20, weight="bold")).pack(pady=40)

    logout_btn = ctk.CTkButton(dash, text="Logout", fg_color="red",
                               command=lambda:[clear_session(), dash.destroy(), show_login()])
    logout_btn.pack(pady=20)




# ---------------- Open Link ---------------- #
def open_link(event=None):
    webbrowser.open("http://127.0.0.1:5000/query")

# ---------------- GUI Login ---------------- #
def show_login():
    global root, entry_user, entry_pass

    root = ctk.CTk()
    root.title("Login Page")
    root.geometry("500x550")
    root.resizable(False, False)

    frame = ctk.CTkFrame(root, corner_radius=20, width=500, height=450)
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

    policy = ctk.CTkLabel(frame,
                          text="Don't know your credentials? Click here",
                          font=ctk.CTkFont(size=12, underline=True),
                          text_color="#1E90FF", cursor="hand2")
    policy.pack(pady=10)
    policy.bind("<Button-1>", open_link)

    root.mainloop()

# ---------------- Start ---------------- #
if __name__ == '__main__':
    # Start Flask in a background thread
    #threading.Thread(target=lambda: app.run(debug=True, use_reloader=False)).start()

    # If session exists → skip login
    if check_session():
        temp_root = ctk.CTk()
        temp_root.withdraw()
        open_dashboard()
        temp_root.mainloop()
    else:
        show_login()
