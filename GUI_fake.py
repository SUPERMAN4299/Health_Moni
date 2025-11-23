import random
import threading
import customtkinter as ctk

# ================================
#           CONSTANTS
# ================================

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
UNIT_SPO2 = "%"
UNIT_MICROS = "µS"
UNIT_CELSIUS = "°C"

DEFAULT_WINDOW_SIZE = "1100x650"

# ================================
#       GLOBAL FAKE DATA
# ================================

sensor_lock = threading.Lock()
prescription_lock = threading.Lock()

HEART_DATA = 0
GSR_DATA = 0
TEMP_DATA = 0.0
SPO2 = 0
out = "Waiting for data..."


# ================================
#       HELPER FUNCTIONS
# ================================

def status_to_color(status: str) -> str:
    if status == STATUS_GOOD:
        return SUCCESS_COLOR
    if status == STATUS_WARNING:
        return WARNING_COLOR
    return CRITICAL_COLOR


def condition_heart_rate(hr):
    """Simple heart rate status logic."""
    try:
        hr = int(hr)
    except (TypeError, ValueError):
        return STATUS_WARNING

    if 60 <= hr <= 100:
        return STATUS_GOOD
    elif 50 <= hr < 60 or 100 < hr <= 120:
        return STATUS_WARNING
    else:
        return STATUS_CRITICAL


def condition_spo2(spo2):
    """SpO2 status logic."""
    try:
        spo2 = int(spo2)
    except (TypeError, ValueError):
        return STATUS_WARNING

    if spo2 >= 95:
        return STATUS_GOOD
    elif 90 <= spo2 < 95:
        return STATUS_WARNING
    else:
        return STATUS_CRITICAL


def condition_gsr(gsr):
    """Dummy GSR status logic (completely fake)."""
    try:
        gsr = float(gsr)
    except (TypeError, ValueError):
        return STATUS_WARNING

    if 10 <= gsr <= 40:
        return STATUS_GOOD
    elif 40 < gsr <= 70:
        return STATUS_WARNING
    else:
        return STATUS_CRITICAL


def condition_temp(temp):
    """Temperature status logic."""
    try:
        temp = float(temp)
    except (TypeError, ValueError):
        return STATUS_WARNING

    if 36.0 <= temp <= 37.5:
        return STATUS_GOOD
    elif 37.5 < temp <= 38.5:
        return STATUS_WARNING
    else:
        return STATUS_CRITICAL


def generate_fake_sensor_data():
    """Generate completely fake but 'realistic-looking' vitals."""
    global HEART_DATA, GSR_DATA, TEMP_DATA, SPO2, out

    with sensor_lock:
        HEART_DATA = random.randint(55, 120)          # BPM
        GSR_DATA = random.randint(10, 90)             # µS (fake scale)
        TEMP_DATA = round(random.uniform(35.5, 39.5), 1)  # °C
        SPO2 = random.randint(88, 100)                # %

    # Build a fake 'AI' prescription based on the statuses
    hr_status = condition_heart_rate(HEART_DATA)
    spo2_status = condition_spo2(SPO2)
    gsr_status = condition_gsr(GSR_DATA)
    temp_status = condition_temp(TEMP_DATA)

    messages = []
    if hr_status != STATUS_GOOD:
        messages.append("Heart rate is outside normal range. Avoid intense activity.")
    if spo2_status != STATUS_GOOD:
        messages.append("SpO₂ is low. Take deep breaths and consult a doctor if this continues.")
    if gsr_status != STATUS_GOOD:
        messages.append("Stress level / GSR is high. Try relaxation or breathing exercises.")
    if temp_status != STATUS_GOOD:
        messages.append("Body temperature looks abnormal. Monitor regularly and stay hydrated.")

    with prescription_lock:
        if not messages:
            out = "All vitals look normal. Maintain a healthy routine and hydration. ✅"
        else:
            out = " | ".join(messages)


def launch_graph():
    """Fake graph launcher – only shows a placeholder window."""
    graph_win = ctk.CTkToplevel()
    graph_win.title("Health Trends (Fake Data)")
    graph_win.geometry("500x300")
    graph_win.configure(fg_color=PANEL_BG)

    ctk.CTkLabel(
        graph_win,
        text="Graph feature not connected to real sensors.\nShowing only simulated data.",
        font=ctk.CTkFont(size=FONT_SIZE_MEDIUM),
        text_color=TEXT_COLOR_PRIMARY,
        justify="center"
    ).pack(expand=True, fill="both", padx=20, pady=20)


def logout(master):
    """Close the app."""
    master.destroy()


# ================================
#       UI COMPONENTS
# ================================

def create_metric(parent, col, icon, title, value, unit, status, color, width=STATUS_LABEL_WIDTH):
    frame = ctk.CTkFrame(parent, fg_color=STAT_CARD_BG, corner_radius=CORNER_RADIUS_MEDIUM)
    frame.grid(row=0, column=col, padx=CARD_SPACING, pady=CARD_SPACING, sticky="nsew")
    frame.grid_columnconfigure(0, weight=1)

    # Icon + Title
    icon_title_frame = ctk.CTkFrame(frame, fg_color="transparent")
    icon_title_frame.pack(pady=(CARD_INNER_PADDING, 0))

    ctk.CTkLabel(
        icon_title_frame,
        text=icon,
        font=ctk.CTkFont(size=FONT_SIZE_MEDIUM),
        text_color=ICON_COLOR
    ).pack(side="left", padx=(0, 5))

    ctk.CTkLabel(
        icon_title_frame,
        text=title,
        font=ctk.CTkFont(size=FONT_SIZE_SMALL, weight="bold"),
        text_color=TEXT_COLOR_SECONDARY
    ).pack(side="left")

    # Value
    value_label = ctk.CTkLabel(
        frame,
        text=value,
        font=ctk.CTkFont(size=FONT_SIZE_LARGE, weight="bold"),
        text_color=TEXT_COLOR_PRIMARY
    )
    value_label.pack(pady=(0, 5))

    unit_label = ctk.CTkLabel(
        frame,
        text=unit,
        font=ctk.CTkFont(size=FONT_SIZE_XSMALL),
        text_color=TEXT_COLOR_SECONDARY
    )
    unit_label.pack()

    # Status badge
    badge = ctk.CTkFrame(
        frame,
        fg_color=color,
        corner_radius=CORNER_RADIUS_SMALL,
        width=width,
        height=STATUS_LABEL_HEIGHT
    )
    badge.pack(pady=(CARD_INNER_PADDING // 2, CARD_INNER_PADDING))

    status_label = ctk.CTkLabel(
        badge,
        text=status,
        font=ctk.CTkFont(size=FONT_SIZE_XXSMALL, weight="bold"),
        text_color=TEXT_COLOR_PRIMARY
    )
    status_label.pack(padx=5, pady=2)

    return {"value": value_label, "status": status_label, "badge": badge}


# ================================
#          MAIN DASHBOARD
# ================================

def main_dash(master):
    global out

    # --- Configure theme ---
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    master.title("Health Dashboard (Fake Data)")
    master.geometry(DEFAULT_WINDOW_SIZE)
    master.configure(fg_color=PRIMARY_DARK_COLOR)
    master.grid_columnconfigure(0, weight=1)
    master.grid_rowconfigure(0, weight=1)

    # --- Main Frame ---
    main_frame = ctk.CTkFrame(master, fg_color=PRIMARY_DARK_COLOR)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=PADDING_X, pady=PADDING_Y)
    main_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
    main_frame.grid_rowconfigure((0, 1), weight=1)

    # Generate initial fake data
    generate_fake_sensor_data()

    # --- Get initial values safely ---
    with sensor_lock:
        hr_val = HEART_DATA
        gsr_val = GSR_DATA
        temp_val = TEMP_DATA
        spo2_val = SPO2

    # --- Calculate statuses ---
    hr_status = condition_heart_rate(hr_val)
    spo2_status = condition_spo2(spo2_val)
    gsr_status = condition_gsr(gsr_val)
    temp_status = condition_temp(temp_val)

    # --- Metrics dictionary (will store label refs) ---
    metrics_refs = {}

    # --- Metric cards ---
    metrics_refs["Heart Rate"] = create_metric(
        main_frame, 0, ICON_HEART, "Heart Rate",
        hr_val, UNIT_BPM, hr_status, status_to_color(hr_status)
    )
    metrics_refs["SpO2"] = create_metric(
        main_frame, 1, ICON_AIR_QUALITY, "SpO₂ Level",
        spo2_val, UNIT_SPO2, spo2_status, status_to_color(spo2_status)
    )
    metrics_refs["GSR"] = create_metric(
        main_frame, 2, ICON_GSR, "GSR",
        gsr_val, UNIT_MICROS, gsr_status, status_to_color(gsr_status), width=70
    )
    metrics_refs["Temperature"] = create_metric(
        main_frame, 3, ICON_TEMP, "Temperature",
        temp_val, UNIT_CELSIUS, temp_status, status_to_color(temp_status), width=60
    )

    # --- Prescription (AI Output) Frame ---
    prescription_frame = ctk.CTkFrame(
        main_frame, fg_color=PANEL_BG, corner_radius=CORNER_RADIUS_MEDIUM
    )
    prescription_frame.grid(
        row=1, column=0, columnspan=2,
        padx=CARD_SPACING, pady=CARD_SPACING, sticky="nsew"
    )
    prescription_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        prescription_frame, text="Prescription",
        font=ctk.CTkFont(size=FONT_SIZE_MEDIUM, weight="bold"),
        text_color=TEXT_COLOR_PRIMARY
    ).pack(anchor="w", padx=CARD_INNER_PADDING, pady=(10, 5))

    with prescription_lock:
        txt = out

    content_label = ctk.CTkLabel(
        prescription_frame,
        text=txt,
        wraplength=420,
        font=ctk.CTkFont(size=FONT_SIZE_SMALL),
        text_color=TEXT_COLOR_TERTIARY,
        justify="left"
    )
    content_label.pack(anchor="w", padx=CARD_INNER_PADDING, pady=(5, CARD_INNER_PADDING))

    def update_prescription_label():
        with prescription_lock:
            txt_local = out
        content_label.configure(text=txt_local)
        master.after(2000, update_prescription_label)

    update_prescription_label()

    # --- Trends Frame ---
    trends_frame = ctk.CTkFrame(main_frame, fg_color=PANEL_BG, corner_radius=CORNER_RADIUS_MEDIUM)
    trends_frame.grid(
        row=1, column=2, columnspan=2,
        padx=CARD_SPACING, pady=CARD_SPACING,
        sticky="nsew"
    )

    ctk.CTkLabel(
        trends_frame,
        text="Health Trends",
        font=ctk.CTkFont(size=FONT_SIZE_MEDIUM, weight="bold"),
        text_color=TEXT_COLOR_PRIMARY
    ).pack(pady=10)

    ctk.CTkButton(
        trends_frame,
        text="Launch Graph",
        command=launch_graph,
        font=ctk.CTkFont(size=13, weight="bold"),
        fg_color=(GRADIENT_START, GRADIENT_END),
        hover_color=(BUTTON_BLUE_HOVER_DARK, BUTTON_BLUE_DARK),
        width=BUTTON_WIDTH,
        height=BUTTON_HEIGHT,
        corner_radius=CORNER_RADIUS_LARGE,
        text_color=TEXT_COLOR_PRIMARY
    ).pack(pady=(0, 20))

    # --- Logout Button ---
    logout_button = ctk.CTkButton(
        master,
        text="Logout",
        command=lambda: logout(master),
        fg_color="red",
        hover_color="#cc0000",
        text_color=TEXT_COLOR_PRIMARY
    )
    logout_button.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")

    # --- Live Metric Updater ---
    def update_live_metrics():
        # Generate new fake data on every tick
        generate_fake_sensor_data()

        with sensor_lock:
            hr = HEART_DATA
            gsr = GSR_DATA
            spo2 = SPO2
            temp = TEMP_DATA

        # Update text values
        metrics_refs["Heart Rate"]["value"].configure(text=str(hr))
        metrics_refs["SpO2"]["value"].configure(text=str(spo2))
        metrics_refs["GSR"]["value"].configure(text=str(gsr))
        metrics_refs["Temperature"]["value"].configure(text=str(temp))

        # Recalculate color/status
        metrics_refs["Heart Rate"]["badge"].configure(
            fg_color=status_to_color(condition_heart_rate(hr))
        )
        metrics_refs["SpO2"]["badge"].configure(
            fg_color=status_to_color(condition_spo2(spo2))
        )
        metrics_refs["GSR"]["badge"].configure(
            fg_color=status_to_color(condition_gsr(gsr))
        )
        metrics_refs["Temperature"]["badge"].configure(
            fg_color=status_to_color(condition_temp(temp))
        )

        master.after(1000, update_live_metrics)  # Refresh every 1 second

    update_live_metrics()


# ================================
#           ENTRY POINT
# ================================

if __name__ == "__main__":
    root = ctk.CTk()
    main_dash(root)
    root.mainloop()
