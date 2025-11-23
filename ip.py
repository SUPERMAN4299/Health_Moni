import requests

def get_location_from_ip(ip_address):
    try:
        url = f"http://ip-api.com/json/{ip_address}"
        response = requests.get(url)
        data = response.json()

        if data["status"] == "success":
            lat = data["lat"]
            lon = data["lon"]
            print(f"IP Address: {ip_address}")
            print(f"Latitude : {lat}")
            print(f"Longitude: {lon}")
        else:
            print("Error:", data["message"])

    except Exception as e:
        print("Something went wrong:", e)


# --------- MAIN ---------
from urllib.request import urlopen

public_ip = urlopen('https://api.ipify.org').read().decode('utf-8')
print(public_ip)
ip = public_ip
get_location_from_ip(ip)
