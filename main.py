import tkinter as tk
from tkinter import messagebox

def submit():
    username = entry_user.get()
    password = entry_pass.get()
    if username == "admin" and password == "123":
        messagebox.showinfo("Success", "Login successful!")
    else:
        messagebox.showerror("Error", "Invalid username or password")

# Main window
root = tk.Tk()
root.title("Login Page")
root.geometry("400x400")
root.config(bg="#0A014F")  # Dark navy background

# Privacy & Policy link
policy = tk.Label(root, text="Privacy & Policy", fg="white", bg="#0A014F", font=("Poppins", 10))
policy.place(x=20, y=20)

# Login box frame
frame = tk.Frame(root, bg="#27E4F2", bd=0, relief="flat")
frame.place(relx=0.5, rely=0.5, anchor="center", width=300, height=280)

title = tk.Label(frame, text="Login", fg="#0A014F", bg="#27E4F2", font=("Poppins", 16, "bold"))
title.pack(pady=(15, 5))

subtitle = tk.Label(frame, text="Please enter your username and password.", fg="#0A014F", bg="#27E4F2", font=("Poppins", 10), wraplength=250, justify="center")
subtitle.pack(pady=(0, 15))

# Username input
entry_user = tk.Entry(frame, font=("Poppins", 12), bg="#BFF8FC", bd=0, relief="flat")
entry_user.pack(pady=8, ipady=6, ipadx=5, fill="x", padx=30)

# Password input
entry_pass = tk.Entry(frame, show="*", font=("Poppins", 12), bg="#BFF8FC", bd=0, relief="flat")
entry_pass.pack(pady=8, ipady=6, ipadx=5, fill="x", padx=30)

# Submit button
btn = tk.Button(frame, text="SUBMIT", command=submit, bg="#0A014F", fg="white", font=("Poppins", 12, "bold"), relief="flat")
btn.pack(pady=15, ipadx=5, ipady=5, fill="x", padx=30)

root.mainloop()
