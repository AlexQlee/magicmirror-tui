from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult
from textual.widgets import Label, Static, Input, Button
from textual.reactive import reactive
from datetime import datetime, date
import sqlite3

DB_PATH = "calendar.db"

class CalendarWidget(Vertical):

    def compose(self) -> ComposeResult:
        yield Static("📅 Termine", id="cal-header")
        yield Vertical(id="cal-list")
        with Horizontal(id="cal-input-bar"):
            yield Input(placeholder="Titel", id="cal-input-title")
            yield Input(placeholder="Datum (TT.MM.JJJJ)", id="cal-input-date")
            yield Button("＋", id="cal-add-btn", variant="primary")

    def on_mount(self) -> None:
        self._init_db()
        self.refresh_list()

    def _init_db(self) -> None:
        with sqlite3.connect(DB_PATH) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    title   TEXT NOT NULL,
                    date    TEXT NOT NULL
                )
            """)

    def _get_upcoming(self) -> list[tuple]:
        today = date.today().isoformat()
        with sqlite3.connect(DB_PATH) as con:
            return con.execute("""
                SELECT id, title, date FROM events
                WHERE date >= ?
                ORDER BY date ASC
                LIMIT 5
            """, (today,)).fetchall()

    def _add_event(self, title: str, date_str: str) -> bool:
        try:
            # Datum validieren
            parsed = datetime.strptime(date_str, "%d.%m.%Y").date().isoformat()
            with sqlite3.connect(DB_PATH) as con:
                con.execute(
                    "INSERT INTO events (title, date) VALUES (?, ?)",
                    (title, parsed)
                )
            return True
        except ValueError:
            return False

    def refresh_list(self) -> None:
        cal_list = self.query_one("#cal-list", Vertical)
        cal_list.remove_children()
        events = self._get_upcoming()

        if not events:
            cal_list.mount(Label("Keine Termine", id="cal-empty"))
            return

        today = date.today()
        for _, title, date_str in events:
            event_date = date.fromisoformat(date_str)
            days_left = (event_date - today).days
            formatted = event_date.strftime("%d.%m.%Y")

            if days_left == 0:
                countdown = "[bold red]heute[/bold red]"
            elif days_left == 1:
                countdown = "[yellow]morgen[/yellow]"
            else:
                countdown = f"[green]in {days_left} Tagen[/green]"

            cal_list.mount(Label(f"• {formatted}  {title}  ({countdown})"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cal-add-btn":
            title = self.query_one("#cal-input-title", Input).value.strip()
            date_str = self.query_one("#cal-input-date", Input).value.strip()

            if title and date_str:
                success = self._add_event(title, date_str)
                if success:
                    self.query_one("#cal-input-title", Input).value = ""
                    self.query_one("#cal-input-date", Input).value = ""
                    self.refresh_list()