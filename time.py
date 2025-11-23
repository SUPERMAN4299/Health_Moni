import time

def loop_with_timers(value):
    last_30 = time.time()
    last_180 = time.time()

    while True:
        now = time.time()

        # Call every 30 seconds
        if now - last_30 >= 30:
            print("30s call:", value)
            last_30 = now

        # Call every 180 seconds
        if now - last_180 >= 50:
            print("180s call:", value)
            last_180 = now

        time.sleep(0.2)   # reduce CPU usage


loop_with_timers("Sensor Value")

