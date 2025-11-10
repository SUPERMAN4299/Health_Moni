import subprocess
import sys
import re

# Path to BluetoothCL.exe
btcl_path = r"C:\Users\HP\Downloads\bluetoothcl\BluetoothCL.exe"

try:
    result = subprocess.run(
        [btcl_path, "-timeout", "20"],
        capture_output=True,
        text=True,
        encoding='utf-8',
        check=True
    )
except FileNotFoundError:
    print(f"Error: BluetoothCL.exe not found at {btcl_path}", file=sys.stderr)
    sys.exit(1)
except subprocess.CalledProcessError as e:
    print(f"Error running BluetoothCL.exe. Return code: {e.returncode}", file=sys.stderr)
    print(f"Error output:\n{e.stderr}", file=sys.stderr)
    sys.exit(1)

# Extract and print only MAC addresses
for line in result.stdout.splitlines():
    match = re.match(r"^([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})", line)
    if match:
        print(match.group(1))
