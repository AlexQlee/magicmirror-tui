from textual.containers import Vertical
from textual.app import ComposeResult
from textual.style import Color
from textual.widgets import Label, Digits
import requests


class WeatherWidget(Vertical):
    def __init__(self, config: dict, **kwargs):
        super().__init__(**kwargs)
        lat = config.get("lat", 53.5507)
        lon = config.get("lon", 9.993)
        api_key = config.get("api_key", "")
        self.uri = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
        self.update_interval = config.get("update_interval", 1800)

    def compose(self) -> ComposeResult:
        yield Label("Lade Wetter...", id="city")
        yield Digits(id="temp")
        yield Label("", id="description")

    def on_mount(self) -> None:
        self.load_weather()
        self.set_interval(self.update_interval, self.load_weather)

    def load_weather(self):
        self.weather_response = requests.get(self.uri).json()
        city_label = self.query_one("#city", Label)
        weather_digits = self.query_one("#temp", Digits)
        description_label = self.query_one("#description", Label)

        city_label.update("Wetter in " + self.weather_response["name"])
        temp = float(self.weather_response["main"]["temp"]) - 273.15

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
            return Color.parse("#00E5FF")
        elif temp < 15:
            return Color.parse("#4FC3F7")
        elif temp < 20:
            return Color.parse("#66BB6A")
        elif temp < 30:
            return Color.parse("#FFA726")
        else:
            return Color.parse("#EF5350")

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
