import time
import random
import os

filename = "data.txt"

while True:
    # Count lines in the file
    if os.path.exists(filename):
        with open(filename, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # If file has 86 lines, reset (clear it)
    if len(lines) >= 30:
        with open(filename, "w") as f:
            f.write("")  # clear file
        #print("File reset after 86 lines")

    # Generate new random value
    value = random.randint(10, 100)

    # Append to file
    with open(filename, "a") as f:
        f.write(str(value) + "\n")

    print(value)
    time.sleep(2)


# this is for heart beat testing
