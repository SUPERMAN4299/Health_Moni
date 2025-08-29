import tkinter as tk
from tkinter import messagebox
import webbrowser

# ---------------- Placeholder Entry Class ---------------- #
class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()

# ---------------- Gradient Background ---------------- #
class GradientFrame(tk.Canvas):
    def __init__(self, master, color1, color2, **kwargs):
        super().__init__(master, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind("<Configure>", self._draw_gradient)

    def _draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        limit = height
        (r1, g1, b1) = self.winfo_rgb(self.color1)
        (r2, g2, b2) = self.winfo_rgb(self.color2)
        r_ratio = float(r2 - r1) / limit
        g_ratio = float(g2 - g1) / limit
        b_ratio = float(b2 - b1) / limit

        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = "#%04x%04x%04x" % (nr, ng, nb)
            self.create_line(0, i, width, i, tags=("gradient",), fill=color)
        self.lower("gradient")

# ---------------- Submit Function ---------------- #
def submit():
    username = entry_user.get()
    password = entry_pass.get()
    if username == entry_user.placeholder or password == entry_pass.placeholder:
        messagebox.showerror("Error", "Please enter username and password")
        return
    if username == "admin" and password == "123":
        messagebox.showinfo("Success", "Login successful!")
    else:
        messagebox.showerror("Error", "Invalid username or password")

# ---------------- Hover Effects for Button ---------------- #
def on_enter(e):
    btn['bg'] = "#1A2E6F"   # Hover color

def on_leave(e):
    btn['bg'] = "#0A014F"   # Default color

# ---------------- Password Field Fix ---------------- #
def on_pass_focus_in(event):
    if entry_pass.get() == entry_pass.placeholder:
        entry_pass.delete(0, tk.END)
        entry_pass.config(show="*")
        entry_pass['fg'] = 'black'

def on_pass_focus_out(event):
    if not entry_pass.get():
        entry_pass.config(show="")
        entry_pass.put_placeholder()

# ---------------- Open Link ---------------- #
def open_link(event=None):
    webbrowser.open("https://www.google.com")  # LOcalHost

# ---------------- Main Window ---------------- #
root = tk.Tk()
root.title("Login Page")
root.geometry("500x500")
root.resizable(False, False)

# Gradient background
gradient = GradientFrame(root, "#0A014F", "#27E4F2")
gradient.pack(fill="both", expand=True)

# ---------------- Frame (Glass Effect) ---------------- #
frame = tk.Frame(gradient, bg="#27E4F2", bd=3, relief="ridge", 
                 highlightbackground="white", highlightthickness=2)
frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=380)

title = tk.Label(frame, text="Login", fg="#0A014F", bg="#27E4F2", font=("Poppins", 22, "bold"))
title.pack(pady=(20, 10))

subtitle = tk.Label(frame, text="Please enter your username and password", fg="#0A014F", bg="#27E4F2", 
                    font=("Poppins", 12), wraplength=350, justify="center")
subtitle.pack(pady=(0, 15))

# ---------------- Input Fields ---------------- #
entry_user = PlaceholderEntry(frame, placeholder="Username", font=("Poppins", 14), 
                              bg="#BFF8FC", bd=0, relief="flat", fg="black")
entry_user.pack(pady=10, ipady=10, ipadx=10, fill="x", padx=40)

entry_pass = PlaceholderEntry(frame, placeholder="Password", font=("Poppins", 14), 
                              bg="#BFF8FC", bd=0, relief="flat", fg="black", show="")
entry_pass.pack(pady=10, ipady=10, ipadx=10, fill="x", padx=40)

entry_pass.bind("<FocusIn>", on_pass_focus_in)
entry_pass.bind("<FocusOut>", on_pass_focus_out)

# ---------------- Submit Button ---------------- #
btn = tk.Button(frame, text="SUBMIT", command=submit, 
                bg="#0A014F", fg="white", activebackground="#1A2E6F", activeforeground="white",
                font=("Poppins", 14, "bold"), relief="flat", cursor="hand2")
btn.pack(pady=30, fill="x", padx=40)

btn.bind("<Enter>", on_enter)
btn.bind("<Leave>", on_leave)

# ---------------- Click Me Link ---------------- #

policy = tk.Label(gradient, text="If you don't know click me",
                  fg="blue", bg="#27E4F2",   # lighter background
                  font=("Poppins", 12, "underline"),
                  cursor="hand2")
policy.pack(side="bottom", pady=15)
policy.bind("<Button-1>", open_link)


root.mainloop()
