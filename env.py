from urllib.request import urlopen
import requests
import json
import time

SECURITY_FILE = 'config.json'

lat = None
lon = None
public_ip = None

def get_location_from_ip():
    global lat, lon, public_ip

    try:
        # Fetch public IP
        public_ip = urlopen('https://api.ipify.org').read().decode('utf-8')
        print("Public IP:", public_ip)

        # Get geolocation using IP
        url = f"http://ip-api.com/json/{public_ip}"
        response = requests.get(url)
        data = response.json()

        if data["status"] == "success":
            lat = data["lat"]
            lon = data["lon"]
            print(f"Latitude : {lat}")
            print(f"Longitude: {lon}")
        else:
            print("IP API Error:", data["message"])

    except Exception as e:
        print("Something went wrong:", e)


def AQI_call():
    while True:
        global lat, lon

        if lat is None or lon is None:
            print("Location not set! Call get_location_from_ip() first.")
            return

        try:
            with open(SECURITY_FILE, "r") as api_aqi:
                call = json.load(api_aqi)

            token = call['AQI_API_KEY']
            url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={token}"

            res = requests.get(url)
            data_aqi = res.json()

            if data_aqi["status"] == "ok":
                print("AQI:", data_aqi["data"]["aqi"])
            else:
                print("AQI API Error:", data_aqi.get("data", "Unknown Error"))

        except Exception as e:
            print("Something went wrong:", e)
        time.sleep(30)


if __name__ == '__main__':
    get_location_from_ip()
    AQI_call()
