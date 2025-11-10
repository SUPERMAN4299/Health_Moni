import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
import sys
import time
import os
import numpy as np

# -------------------------------
# CONFIGURATION
# -------------------------------
DATA_FILE = "BPM_data.txt"
UPDATE_INTERVAL = 1000  # in ms
MAX_POINTS = 120        # points to display
WINDOW_TITLE = "Heart Rate Monitor"

# -------------------------------
# SETUP
# -------------------------------
app = QtWidgets.QApplication(sys.argv)

# Dark, modern look
pg.setConfigOption('background', '#121212')
pg.setConfigOption('foreground', 'w')
pg.setConfigOption('antialias', True)

# Main window and plot
win = pg.GraphicsLayoutWidget(show=True, title=WINDOW_TITLE)
win.resize(1000, 600)

plot = win.addPlot(title="Heart Rate Live")
plot.showGrid(x=True, y=True, alpha=0.3)
plot.setLabel('left', 'Value', **{'color': '#CCCCCC', 'size': '14pt'})
plot.setLabel('bottom', 'Time (s)', **{'color': '#CCCCCC', 'size': '14pt'})
plot.addLegend(offset=(10, 10))
plot.setMouseEnabled(x=False, y=False)

# -------------------------------
# DATA INITIALIZATION
# -------------------------------
x_data, y_data = [], []
start_time = time.time()

# Smooth curve with glow-style pen
curve = plot.plot(pen=pg.mkPen(color='#00E5FF', width=3), name="Sensor Value")

# Text label for dynamic info
avg_text = pg.TextItem(anchor=(1, 0))
avg_text.setPos(MAX_POINTS, 0)
plot.addItem(avg_text)

# -------------------------------
# UPDATE FUNCTION
# -------------------------------
def update():
    global x_data, y_data

    if not os.path.exists(DATA_FILE):
        avg_text.setText("<i>Waiting for data file...</i>", color="#888")
        return

    try:
        with open(DATA_FILE, "r") as f:
            lines = f.readlines()
            if not lines:
                return
            value = float(lines[-1].strip())
    except Exception as e:
        avg_text.setText(f"<b>Error:</b> {e}", color="#FF5252")
        return

    # Update data
    current_time = round(time.time() - start_time, 1)
    x_data.append(current_time)
    y_data.append(value)

    if len(x_data) > MAX_POINTS:
        x_data = x_data[-MAX_POINTS:]
        y_data = y_data[-MAX_POINTS:]

    # Smoothly update the graph
    curve.setData(x_data, y_data)

    # Dynamic y-axis
    plot.enableAutoRange(axis=pg.ViewBox.YAxis, enable=True)

    # Show average value
    avg_value = np.mean(y_data)
    avg_text.setText(f"<b>Avg:</b> {avg_value:.2f}", color="#00E5FF")

# -------------------------------
# TIMER
# -------------------------------
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(UPDATE_INTERVAL)

# -------------------------------
# RUN APP
# -------------------------------
sys.exit(app.exec_())
