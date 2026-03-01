import psutil
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Label, Sparkline

class MyHeader(Static):

    def compose(self) -> ComposeResult:
        with Horizontal(id="header-bar"):
            yield Label("Magic Mirror tui - by AlexQlee", id="header-title")
            yield Label("📶", id="wifi-icon")
            yield Sparkline(data=[0] * 20, id="wifi-spark", summary_function=max)

    def on_mount(self) -> None:
        self.signal_history = [0] * 20  # direkt mit 20 Werten füllen
        self.set_interval(2, self.update_wifi)
        self.update_wifi()

    def update_wifi(self) -> None:
        signal = self._get_wifi_signal()
        self.log(f"WiFi Signal: {signal}")

        self.signal_history.append(signal)
        if len(self.signal_history) > 20:
            self.signal_history.pop(0)

        # Direkt setzen statt call_after_refresh
        spark = self.query_one("#wifi-spark", Sparkline)
        spark.data = list(self.signal_history)  # list() erzwingt eine Kopie → triggert das reactive update

        if signal == 0:
            icon = "❌"
        elif signal < 40:
            icon = "📶 schwach"
        elif signal < 70:
            icon = "📶 gut"
        else:
            icon = "📶 stark"

        self.query_one("#wifi-icon", Label).update(icon)

    def _update_spark(self) -> None:
        self.query_one("#wifi-spark", Sparkline).data = self.signal_history

    def _get_wifi_signal(self) -> int:
        # Methode 1: /proc/net/wireless (nur wenn WiFi aktiv)
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

        # Methode 2: psutil Fallback – schaut ob ein WiFi-Interface aktiv ist
        try:
            stats = psutil.net_if_stats()
            for name, iface in stats.items():
                if ("wi" in name.lower() or "wl" in name.lower()) and iface.isup:
                    return 50  # Interface aktiv aber Stärke unbekannt
        except Exception:
            pass

        return 0
