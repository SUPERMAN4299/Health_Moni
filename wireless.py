import serial
import json
import time

BT_PORT = "COM8"  # Change to your BT COM port
BAUD = 115200

def connect_bt():
    try:
        bt = serial.Serial(BT_PORT, BAUD, timeout=1)
        print("[BT] Connected!")
        return bt
    except Exception as e:
        print("[BT] Error:", e)
        return None

def read_bt():
    bt = connect_bt()
    if not bt:
        return
    
    print("[BT] Listening wirelessly...")
    
    while True:
        if bt.in_waiting:
            raw = bt.readline().decode(errors="ignore").strip()
            print("RAW:", raw)

            try:
                data = json.loads(raw)
                print("JSON:", data)
            except:
                pass
        
        time.sleep(0.05)

if __name__ == "__main__":
    read_bt()
