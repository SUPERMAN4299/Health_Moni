from flask import Flask
import customtkinter as ctk
from tkinter import messagebox
import webbrowser
import os
import threading
import subprocess
import platform  
import re   

# ---------------- Flask Server ---------------- #
app = Flask(__name__)

# ---------------- Security (Encoding / Decoding) ---------------- #
def hex_encode(text: str) -> str:
    return text.encode().hex()

def hex_decode(hex_text: str) -> str:
    return bytes.fromhex(hex_text).decode()

# ---------------- Built-in Encoded Credentials ---------------- #
stored_user_enc = hex_encode("admin")   # username
stored_pass_enc = hex_encode("admin")   # password

stored_user = hex_decode(stored_user_enc)
stored_pass = hex_decode(stored_pass_enc)

add_user_enc = hex_encode("admin1") 
add_pass_enc = hex_encode("admin1") 

stored_user1 = hex_decode(add_user_enc)
stored_pass1 = hex_decode(add_pass_enc)

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
@app.route('/security')
def get_string():
	return f"Stored Username: {stored_user_enc}, Stored Password: {stored_pass_enc} "f"Username: {add_user_enc},Password: {add_pass_enc}"
    
@app.route("/query")
def query():
    return """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Health_Moni Project Login Guide</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f4f8;
            color: #333;
            margin: 0;
            padding: 0;
        }
        header {
            background-color: #4CAF50;
            color: white;
            padding: 30px 20px;
            text-align: center;
        }
        main {
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            margin-bottom: 15px;
        }
        h1 {
            color: #2c3e50;
        }
        h2 {
            color: #34495e;
        }
        h3 {
            color: #7f8c8d;
        }
        ol {
            padding-left: 20px;
        }
        a {
            color: #1abc9c;
            text-decoration: none;
            font-weight: bold;
        }
        a:hover {
            text-decoration: underline;
        }
        .note {
            background-color: #eafaf1;
            padding: 10px;
            border-left: 5px solid #4CAF50;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>

<header>
    <h1>Welcome to the Health_Moni Project</h1>
</header>

<main>
    <section>
        <h2>How to Login</h2>
        <div class="note">
            You will receive a card in your product box containing your Username and Password. Enter them exactly as shown in the app to access our service.
        </div>
        <h3>If you're unsure how to proceed, follow these steps carefully:</h3>
        <ol>
            <li>Open the box where you received this product.</li>
            <li>On your desktop, download the software from our website: <a href="http://127.0.0.1:5000/download" target="_blank">Download Here</a></li>
            <li>Install the software on your PC as usual. Make sure Python is installed: <a href="https://www.python.org" target="_blank">Download Python</a></li>
            <li>Before opening the app, turn on Bluetooth on your device.</li>
            <li>Open the software and enter the Username and Password provided in your card.</li>
            <li>Connect the device associated with our service.</li>
            <li>Allow the software to access the device.</li>
            <li>Once connected, you will be redirected to the monitoring dashboard with real-time graphs.</li>
        </ol>
    </section>
</main>

</body>
</html>
    """

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

    if (username == stored_user or username == stored_user1) and \
       (password == stored_pass or password == stored_pass1):
        if is_device_connected(DEVICE_MAC):
            save_session()
            messagebox.showinfo("Success", "Login Successful and Device Connected!")
            root.withdraw()
            open_dashboard()
        else:
            messagebox.showerror("Device Not Connected",
                                 "Your device is not connected. Please connect the device and try again.")
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
    threading.Thread(target=lambda: app.run(debug=True, use_reloader=False)).start()

    # If session exists → skip login
    if check_session():
        temp_root = ctk.CTk()
        temp_root.withdraw()
        open_dashboard()
        temp_root.mainloop()
    else:
        show_login()
