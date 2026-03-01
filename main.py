from datetime import datetime

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Horizontal, Vertical

from config import API_KEY_OPENWEATHERMAP
from widgets.WeatherWidget import WeatherWidget 
from widgets.NewsWidget import NewsWidget
from widgets.SystemInfoWidget import SystemInfoWidget
from widgets.MyHeader import MyHeader

from widgets.QuoteWidget import QuoteWidget
# from widgets.CalendarWidget import CalendarWidget


api_key = API_KEY_OPENWEATHERMAP
lat = 53.5507
lon = 9.993

uri = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"

class MagicMirrorTUI(App):

    TITLE = "Magic Mirror - tui version"
    SUB_TITLE = "created by AlexQlee"

    CSS_PATH = "magic_mirror.tcss"

    def compose(self) -> ComposeResult:
        yield MyHeader()
        with Horizontal(id="top-bar"):
            yield WeatherWidget(uri=uri, id="weather")
            yield SystemInfoWidget(id="sysinfo")
        yield QuoteWidget(id="quote")
        # yield CalendarWidget(id="calendar")
        yield NewsWidget()
        yield Footer()

    def on_ready(self) -> None:
        pass
        # self.update_clock()
        # self.set_interval(1, self.update_clock)

    def update_clock(self) -> None:
        pass
        clock = datetime.now().time()
        # self.query_one(Digits).update(f"{clock:%T}")


if __name__ == "__main__":
    app = MagicMirrorTUI()
    app.run()