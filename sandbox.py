import requests
from config import API_KEY_OPENWEATHERMAP

api_key = API_KEY_OPENWEATHERMAP
lat = 53.55
lon = 9.99

uri = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"

r = requests.get(uri).json()

print(r)
print(r["weather"][0]["description"])