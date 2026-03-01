from textual.containers import Vertical
from textual.app import ComposeResult
from textual.style import Color
from textual.widgets import Label, Digits
from config import API_KEY_OPENWEATHERMAP
import requests


class WeatherWidget(Vertical):
    def __init__(self, uri: str, **kwargs):
        super().__init__(**kwargs)  # jetzt wird id etc. weitergegeben
        print(uri)
        self.uri = uri
        self.weather_response = None

    def compose(self) -> ComposeResult:
        yield Label("Lade Wetter...", id="city")
        yield Digits(id="temp")
        yield Label("", id="description")

    def on_mount(self) -> None:
        self.load_weather()  # sofort

        # alle 30 min die Wetterdaten laden
        self.set_interval(30 * 60, self.load_weather)

    def load_weather(self):
        self.weather_response = requests.get(self.uri).json()
        city_label = self.query_one("#city", Label)
        weather_digits = self.query_one("#temp", Digits)
        description_label = self.query_one("#description", Label)

        city_label.update("Wetter in " + self.weather_response["name"])
        temp = float(self.weather_response["main"]["temp"]) - 273.15
        # feels_like_temp = float(self.weather_response["main"]["feels_like"]) - 273.15
       
        weather_digits.styles.color = self.get_temp_color(temp)
        weather_digits.update(f"{temp:.1f} °C")
        description = self.weather_response["weather"][0]["description"]

        if "rain" in description:
            description_label.styles.color = "#4FC3F7"
        elif "clear" in description:
            description_label.styles.color = "#FFD54F"
        elif "snow" in description:
            description_label.styles.color = "#E1F5FE"

        description_label.update(self.format_weather(description))


    def get_temp_color(self, temp: float) -> Color:
        if temp <= 0:
            return Color.parse("#00E5FF")   # Eisblau
        elif temp < 15:
            return Color.parse("#4FC3F7")   # Kühlblau
        elif temp < 20:
            return Color.parse("#66BB6A")   # Frühlingsgrün
        elif temp < 30:
            return Color.parse("#FFA726")   # Warmorange
        else:
            return Color.parse("#EF5350")   # Hitzerot
        
    def format_weather(self, description: str) -> str:
        mapping = {
            "clear sky": "☀ Klarer Himmel",
            "few clouds": "🌤 Wenige Wolken",
            "scattered clouds": "⛅ Aufgelockert",
            "broken clouds": "☁ Stark bewölkt",
            "overcast clouds": "☁ Bedeckt",
            "rain": "🌧 Regen",
            "light rain": "🌦 Leichter Regen",
            "thunderstorm": "⛈ Gewitter",
            "snow": "❄ Schnee",
            "mist": "🌫 Nebel",
        }

        return mapping.get(description.lower(), description.capitalize())