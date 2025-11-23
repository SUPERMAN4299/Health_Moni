from flask import Flask, request
import threading

# your global variables
HEART_DATA = 0
GSR_DATA = 0
TEMP_DATA = 0
AIR_QUA_DATA = 0
SPO2 = 0

sensor_lock = threading.Lock()

app = Flask(__name__)

@app.route("/sensor", methods=["POST"])
def sensor():
    global HEART_DATA, GSR_DATA, TEMP_DATA, AIR_QUA_DATA, SPO2

    data = request.get_json(force=True)

    with sensor_lock:
        HEART_DATA = data.get("HEART_DATA", HEART_DATA)
        GSR_DATA = data.get("GSR_DATA", GSR_DATA)
        TEMP_DATA = data.get("TEMP_DATA", TEMP_DATA)
        AIR_QUA_DATA = data.get("AIR_QUA_DATA", AIR_QUA_DATA)
        SPO2 = data.get("SPO2", SPO2)

    return "OK", 200

def start_flask():
    app.run(host="0.0.0.0", port=5000)

# start flask in background
threading.Thread(target=start_flask, daemon=True).start()
