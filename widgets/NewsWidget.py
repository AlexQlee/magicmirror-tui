from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult
from textual.widgets import Label, Static
from textual.reactive import reactive
from textual import log
from datetime import datetime
from widgets.RSSParser import get_news
import sqlite3

DB_PATH = "news.db"


class NewsWidget(Vertical):

    current_index = reactive(0)

    def __init__(self, config: dict, **kwargs):
        super().__init__(**kwargs)
        self.uris = config.get("feeds", {
            "n-tv": "https://www.n-tv.de/rss",
            "Spiegel": "https://www.spiegel.de/schlagzeilen/tops/index.rss",
        })
        self.carousel_interval = config.get("carousel_interval", 20)
        self.cache_refresh_interval = config.get("cache_refresh_interval", 900)
        self.news_items = []
        self._init_db()

    # ─── Datenbank ────────────────────────────────────────────────────────────

    def _init_db(self) -> None:
        with sqlite3.connect(DB_PATH) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    source      TEXT NOT NULL,
                    title       TEXT NOT NULL,
                    description TEXT,
                    fetched_at  TEXT NOT NULL,
                    UNIQUE(source, title)
                )
            """)

    def _save_to_db(self, source: str, title: str, description: str) -> None:
        with sqlite3.connect(DB_PATH) as con:
            con.execute("""
                INSERT OR IGNORE INTO news (source, title, description, fetched_at)
                VALUES (?, ?, ?, ?)
            """, (source, title, description, datetime.now().isoformat()))

    def _load_from_db(self) -> list[tuple]:
        with sqlite3.connect(DB_PATH) as con:
            rows = con.execute("""
                SELECT source, title, description, fetched_at
                FROM news
                ORDER BY fetched_at DESC
                LIMIT 100
            """).fetchall()
        return rows

    def _is_cache_fresh(self) -> bool:
        max_age_minutes = self.cache_refresh_interval / 60
        with sqlite3.connect(DB_PATH) as con:
            row = con.execute("""
                SELECT fetched_at FROM news ORDER BY fetched_at DESC LIMIT 1
            """).fetchone()
        if not row:
            return False
        last = datetime.fromisoformat(row[0])
        age = (datetime.now() - last).total_seconds() / 60
        return age < max_age_minutes

    # ─── Compose / Mount ──────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Static("📰 Nachrichten", id="news-header")
        with Vertical(id="news-card"):
            yield Label("", id="news-source")
            yield Label("", id="news-title")
            yield Label("", id="news-desc")
        with Horizontal(id="news-footer"):
            yield Label("", id="news-counter")

    def on_mount(self) -> None:
        if self._is_cache_fresh():
            log("News: lade aus Cache")
            self._load_news_from_db()
        else:
            log("News: hole neue Meldungen")
            self._fetch_and_store()

        self.set_interval(self.carousel_interval, self.next_news)
        self.set_interval(self.cache_refresh_interval, self._fetch_and_store)

    # ─── Laden ────────────────────────────────────────────────────────────────

    def _fetch_and_store(self) -> None:
        for source, uri in self.uris.items():
            try:
                for title, description in get_news(uri):
                    self._save_to_db(source, title.strip(), description.strip())
            except Exception as e:
                log(f"Fehler beim Laden von {source}: {e}")
        self._load_news_from_db()

    def _load_news_from_db(self) -> None:
        rows = self._load_from_db()
        self.news_items = [
            (
                source,
                title,
                description or "",
                datetime.fromisoformat(fetched_at).strftime("%H:%M Uhr")
            )
            for source, title, description, fetched_at in rows
        ]
        if self.news_items:
            self.current_index = 0
            self.show_news(0)

    # ─── Anzeige ──────────────────────────────────────────────────────────────

    def next_news(self) -> None:
        if not self.news_items:
            return
        self.current_index = (self.current_index + 1) % len(self.news_items)
        self.show_news(self.current_index)

    def show_news(self, index: int) -> None:
        source, title, desc, timestamp = self.news_items[index]
        self.query_one("#news-source", Label).update(f"🗞  {source}  ·  {timestamp}")
        self.query_one("#news-title",  Label).update(title)
        self.query_one("#news-desc",   Label).update(desc)
        self.query_one("#news-counter", Label).update(
            f"{index + 1} / {len(self.news_items)}"
        )
