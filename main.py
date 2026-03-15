from textual.app import App, ComposeResult
from textual.widgets import Footer
from textual.containers import Horizontal

from config_loader import load_config, get_module_config
from widgets.WeatherWidget import WeatherWidget
from widgets.NewsWidget import NewsWidget
from widgets.SystemInfoWidget import SystemInfoWidget
from widgets.MyHeader import MyHeader
from widgets.QuoteWidget import QuoteWidget
# from widgets.CalendarWidget import CalendarWidget

config = load_config()


class MagicMirrorTUI(App):

    TITLE = "Magic Mirror - tui version"
    SUB_TITLE = "created by AlexQlee"

    CSS_PATH = "magic_mirror.tcss"

    def compose(self) -> ComposeResult:
        weather_cfg  = get_module_config(config, "weather")
        sysinfo_cfg  = get_module_config(config, "system_info")
        quote_cfg    = get_module_config(config, "quote")
        news_cfg     = get_module_config(config, "news")
        header_cfg   = get_module_config(config, "header")
        # calendar_cfg = get_module_config(config, "calendar")

        yield MyHeader(config=header_cfg)

        with Horizontal(id="top-bar"):
            if weather_cfg.get("enabled", True):
                yield WeatherWidget(config=weather_cfg, id="weather")
            if sysinfo_cfg.get("enabled", True):
                yield SystemInfoWidget(config=sysinfo_cfg, id="sysinfo")

        if quote_cfg.get("enabled", True):
            yield QuoteWidget(config=quote_cfg, id="quote")

        # if calendar_cfg.get("enabled", False):
        #     yield CalendarWidget(id="calendar")

        if news_cfg.get("enabled", True):
            yield NewsWidget(config=news_cfg)

        yield Footer()


if __name__ == "__main__":
    app = MagicMirrorTUI()
    app.run()
