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
    return text.encode().hex()

def hex_decode(hex_text: str) -> str:
    try:
        return bytes.fromhex(hex_text).decode()
    except Exception as e:
        print("Hex decode error:", e)
        return ""

# ---------------- Built-in Encoded Credentials ---------------- #
#stored_user_enc = hex_encode("admin")   # username
#stored_pass_enc = hex_encode("admin")   # password

#stored_user = hex_decode(stored_user_enc)
#stored_pass = hex_decode(stored_pass_enc)

#add_user_enc = hex_encode("admin1") 
#add_pass_enc = hex_encode("admin1") 

#stored_user1 = hex_decode(add_user_enc)
#stored_pass1 = hex_decode(add_pass_enc)

try:
    res = requests.get("http://127.0.0.1:5000/s")
    s = res.text.strip()  # remove leading/trailing whitespace
    
    # Slice the string
    sec = s[0:10]
    sec1 = s[10:20]
    
    # Decode
    stored_user_enc = hex_decode(sec)
    stored_pass_enc = hex_decode(sec1)
    
    #print("User:", stored_user_enc)
    #print("Pass:", stored_pass_enc)
except requests.exceptions.RequestException as e:
    print("Error:", e)
except ValueError as e:
    print("Hex decode error:", e)

DEVICE_MAC = "00:1a:2b:3c:4d:5e" 

# -------------- MAC check -------------- #
def is_device_connected(target_mac):
    """
    Check if a device with the given MAC address is connected (Linux or Windows)
    """
    target_mac = target_mac.lower().replace("-", ":")
    os_name = platform.system().lower()

    try:
        if os_name == "windows":
            output = subprocess.check_output("arp -a", shell=True, text=True)
        else:  # Linux or others
            output = subprocess.check_output("ip neigh", shell=True, text=True)
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Failed to fetch network devices.")
        return False

    # Extract all MAC addresses
    macs = re.findall(r'(([0-9a-f]{2}[:-]){5}[0-9a-f]{2})', output.lower())
    mac_list = [match[0].replace("-", ":") for match in macs]  # normalize for Windows

    return target_mac in mac_list


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

# ---------------- Flask Routes ---------------- #


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

# ---------------- Submit Function ---------------- #
def submit():
    username = entry_user.get()
    password = entry_pass.get()

    if not username or not password:
        messagebox.showerror("Error", "Please enter username and password")
        return

    if username == stored_user_enc and password == stored_pass_enc:
        if is_device_connected(DEVICE_MAC):
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

# ---------------- Open Link ---------------- #
def open_link(event=None):
    webbrowser.open("http://127.0.0.1:5000/query")

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
