from textual.containers import Vertical
from textual.app import ComposeResult
from textual.widgets import Label, Static
import sqlite3
import requests
from datetime import date

DB_PATH = "quotes.db"

FALLBACK_QUOTES = [
    ("Albert Einstein", "Die Definition von Wahnsinn ist, immer wieder das Gleiche zu tun und andere Ergebnisse zu erwarten."),
    ("Seneca", "Nicht weil es schwer ist, wagen wir es nicht – weil wir es nicht wagen, ist es schwer."),
    ("Aristoteles", "Wir sind, was wir wiederholt tun. Vorzüglichkeit ist also keine Handlung, sondern eine Gewohnheit."),
]


class QuoteWidget(Vertical):

    def __init__(self, config: dict, **kwargs):
        super().__init__(**kwargs)
        self.language = config.get("language", "de")
        self.update_interval = config.get("update_interval", 86400)

    def compose(self) -> ComposeResult:
        yield Static("💬 Zitat des Tages", id="quote-header")
        yield Label("", id="quote-text")
        yield Label("", id="quote-author")

    def on_mount(self) -> None:
        self._init_db()
        self.show_quote()
        self.set_interval(self.update_interval, self._fetch_and_store)

    def _init_db(self) -> None:
        with sqlite3.connect(DB_PATH) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS quotes (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    author  TEXT NOT NULL,
                    text    TEXT NOT NULL,
                    UNIQUE(author, text)
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS daily_quote (
                    date    TEXT PRIMARY KEY,
                    author  TEXT,
                    text    TEXT
                )
            """)
            for author, text in FALLBACK_QUOTES:
                con.execute(
                    "INSERT OR IGNORE INTO quotes (author, text) VALUES (?, ?)",
                    (author, text)
                )

    def _fetch_and_store(self) -> None:
        try:
            response = requests.get(
                f"https://api.quotable.io/quotes/random?limit=10&language={self.language}",
                timeout=5
            )
            if response.status_code == 200:
                quotes = response.json()
                with sqlite3.connect(DB_PATH) as con:
                    for q in quotes:
                        con.execute(
                            "INSERT OR IGNORE INTO quotes (author, text) VALUES (?, ?)",
                            (q["author"], q["content"])
                        )
                self.log(f"✅ {len(quotes)} neue Zitate gespeichert")
                return
        except Exception as e:
            self.log(f"⚠️ API nicht erreichbar: {e}")

        try:
            response = requests.get("https://zenquotes.io/api/quotes", timeout=5)
            if response.status_code == 200:
                quotes = response.json()
                with sqlite3.connect(DB_PATH) as con:
                    for q in quotes:
                        con.execute(
                            "INSERT OR IGNORE INTO quotes (author, text) VALUES (?, ?)",
                            (q["a"], q["q"])
                        )
                self.log(f"✅ {len(quotes)} Zitate via ZenQuotes gespeichert")
        except Exception as e:
            self.log(f"⚠️ ZenQuotes nicht erreichbar: {e}")

    def _get_quote(self) -> tuple[str, str]:
        today = date.today().isoformat()
        with sqlite3.connect(DB_PATH) as con:
            row = con.execute(
                "SELECT author, text FROM daily_quote WHERE date = ?", (today,)
            ).fetchone()
            if row:
                return row

            row = con.execute(
                "SELECT author, text FROM quotes ORDER BY RANDOM() LIMIT 1"
            ).fetchone()

            if not row:
                return ("Unbekannt", "Kein Zitat verfügbar.")

            author, text = row
            con.execute(
                "INSERT OR REPLACE INTO daily_quote (date, author, text) VALUES (?, ?, ?)",
                (today, author, text)
            )
            return author, text

    def show_quote(self) -> None:
        with sqlite3.connect(DB_PATH) as con:
            count = con.execute("SELECT COUNT(*) FROM quotes").fetchone()[0]
        if count <= len(FALLBACK_QUOTES):
            self._fetch_and_store()

        author, text = self._get_quote()
        self.query_one("#quote-text",   Label).update(f'„{text}"')
        self.query_one("#quote-author", Label).update(f"— {author}")
