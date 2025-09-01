import subprocess
import re

target_mac = "4142F6551D9C".lower()

# Run PowerShell command
cmd = 'powershell "Get-PnpDevice -Class Bluetooth | Select-Object -Property Name,InstanceId"'
result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

output = result.stdout
print("🔍 Raw output:\n", output)

# Extract MACs
matches = re.findall(r'DEV_([0-9A-F]{12})', output, re.IGNORECASE)
mac_list = [m.lower() for m in matches]

print("📡 Found Bluetooth MACs:", mac_list)

if target_mac.lower() in mac_list:
    print("✅ Device is paired/connected!")
else:
    print("❌ Device not found.")
