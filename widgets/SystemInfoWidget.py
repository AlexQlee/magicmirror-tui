from textual.containers import Vertical
from textual.app import ComposeResult
from textual.widgets import Label, ProgressBar

import psutil


class SystemInfoWidget(Vertical):

    def __init__(self, config: dict, **kwargs):
        super().__init__(**kwargs)
        self.disks = config.get("disks", ["/", "/home"])
        self.update_interval = config.get("update_interval", 1)

    def compose(self) -> ComposeResult:
        yield Label("── System Info ──")

        yield Label("CPU", id="cpu-label")
        yield ProgressBar(total=100, id="cpu-bar", show_eta=False)

        yield Label("Memory", id="mem-label")
        yield ProgressBar(total=100, id="mem-bar", show_eta=False)

        yield Label("Swap", id="swap-label")
        yield ProgressBar(total=100, id="swap-bar", show_eta=False)

        for i, disk in enumerate(self.disks):
            yield Label(f"Disk ({disk})", id=f"disk-label-{i}")
            yield ProgressBar(total=100, id=f"disk-bar-{i}", show_eta=False)

    def on_mount(self) -> None:
        self.set_interval(self.update_interval, self.update_usage)
        self.update_usage()

    def update_usage(self) -> None:
        cpu  = psutil.cpu_percent(interval=0)
        mem  = psutil.virtual_memory().percent
        swap = psutil.swap_memory().percent

        self.query_one("#cpu-label",  Label).update(f"CPU: {cpu:.1f}%")
        self.query_one("#cpu-bar",    ProgressBar).progress = cpu

        self.query_one("#mem-label",  Label).update(f"Memory: {mem:.1f}%")
        self.query_one("#mem-bar",    ProgressBar).progress = mem

        self.query_one("#swap-label", Label).update(f"Swap: {swap:.1f}%")
        self.query_one("#swap-bar",   ProgressBar).progress = swap

        for i, disk in enumerate(self.disks):
            try:
                percent = psutil.disk_usage(disk).percent
            except Exception:
                percent = 0
            self.query_one(f"#disk-label-{i}", Label).update(f"Disk ({disk}): {percent:.1f}%")
            self.query_one(f"#disk-bar-{i}",   ProgressBar).progress = percent
            self._color_bar(f"#disk-bar-{i}", percent)

        self._color_bar("#cpu-bar",  cpu)
        self._color_bar("#mem-bar",  mem)
        self._color_bar("#swap-bar", swap)

    def _color_bar(self, bar_id: str, percent: float) -> None:
        bar = self.query_one(bar_id, ProgressBar)
        if percent > 80:
            bar.styles.color = "red"
        elif percent > 50:
            bar.styles.color = "yellow"
        else:
            bar.styles.color = "green"
