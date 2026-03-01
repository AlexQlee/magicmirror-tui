from textual.containers import Vertical
from textual.app import ComposeResult
from textual.widgets import Label, ProgressBar

import psutil

class SystemInfoWidget(Vertical):

    def compose(self) -> ComposeResult:
        yield Label("── System Info ──")

        yield Label("CPU", id="cpu-label")
        yield ProgressBar(total=100, id="cpu-bar", show_eta=False)

        yield Label("Memory", id="mem-label")
        yield ProgressBar(total=100, id="mem-bar", show_eta=False)

        yield Label("Swap", id="swap-label")
        yield ProgressBar(total=100, id="swap-bar", show_eta=False)

        yield Label("Disk(/)", id="disk-label")
        yield ProgressBar(total=100, id="disk-bar", show_eta=False)
        
        yield Label("Disk (/home)", id="disk-label-home")
        yield ProgressBar(total=100, id="disk-bar-home", show_eta=False)

    def on_mount(self) -> None:
        self.set_interval(1, self.update_usage)
        self.update_usage()

    def update_usage(self) -> None:
        cpu = psutil.cpu_percent(interval=0)
        mem = psutil.virtual_memory().percent
        swap = psutil.swap_memory().percent
        disk = psutil.disk_usage('/').percent
        disk_home = psutil.disk_usage('/home').percent

        self.query_one("#cpu-label", Label).update(f"CPU: {cpu:.1f}%")
        self.query_one("#cpu-bar", ProgressBar).progress = cpu

        self.query_one("#mem-label", Label).update(f"Memory: {mem:.1f}%")
        self.query_one("#mem-bar", ProgressBar).progress = mem

        self.query_one("#swap-label", Label).update(f"Swap: {swap:.1f}%")
        self.query_one("#swap-bar", ProgressBar).progress = swap

        self.query_one("#disk-label", Label).update(f"Disk (/): {disk:.1f}%")
        self.query_one("#disk-bar", ProgressBar).progress = disk
        
        self.query_one("#disk-label-home", Label).update(f"Disk (/home): {disk_home:.1f}%")
        self.query_one("#disk-bar-home", ProgressBar).progress = disk_home
        
        self._color_bar("#cpu-bar", cpu)
        self._color_bar("#mem-bar", mem)
        self._color_bar("#swap-bar", swap)
        self._color_bar("#disk-bar", disk)
        self._color_bar("#disk-bar-home", disk_home)
        
        
    def _color_bar(self, bar_id: str, percent: float) -> None:
        bar = self.query_one(bar_id, ProgressBar)
        if percent > 80:
            bar.styles.color = "red"
        elif percent > 50:
            bar.styles.color = "yellow"
        else:
            bar.styles.color = "green"