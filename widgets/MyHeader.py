import psutil
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Label, Sparkline


class MyHeader(Static):

    def __init__(self, config: dict, **kwargs):
        super().__init__(**kwargs)
        self.update_interval = config.get("update_interval", 2)

    def compose(self) -> ComposeResult:
        with Horizontal(id="header-bar"):
            yield Label("Magic Mirror tui - by AlexQlee", id="header-title")
            yield Label("📶", id="wifi-icon")
            yield Sparkline(data=[0] * 20, id="wifi-spark", summary_function=max)

    def on_mount(self) -> None:
        self.signal_history = [0] * 20
        self.set_interval(self.update_interval, self.update_wifi)
        self.update_wifi()

    def update_wifi(self) -> None:
        signal = self._get_wifi_signal()
        self.log(f"WiFi Signal: {signal}")

        self.signal_history.append(signal)
        if len(self.signal_history) > 20:
            self.signal_history.pop(0)

        spark = self.query_one("#wifi-spark", Sparkline)
        spark.data = list(self.signal_history)

        if signal == 0:
            icon = "❌"
        elif signal < 40:
            icon = "📶 schwach"
        elif signal < 70:
            icon = "📶 gut"
        else:
            icon = "📶 stark"

        self.query_one("#wifi-icon", Label).update(icon)

    def _get_wifi_signal(self) -> int:
        try:
            with open("/proc/net/wireless") as f:
                lines = f.readlines()
            for line in lines[2:]:
                parts = line.split()
                dbm = float(parts[3].strip("."))
                percent = max(0, min(100, int((dbm + 90) * (100 / 60))))
                return percent
        except Exception:
            pass

        try:
            stats = psutil.net_if_stats()
            for name, iface in stats.items():
                if ("wi" in name.lower() or "wl" in name.lower()) and iface.isup:
                    return 50
        except Exception:
            pass

        return 0
