# MagicMirror TUI

Ein Terminal-basierter Magic Mirror, gebaut mit [Textual](https://textual.textualize.io/) – inspiriert vom klassischen [MagicMirror²](https://magicmirror.builders/) Projekt, aber direkt im Terminal lauffähig.
![MagicMirror TUI](assets/Screenshot.png)
---

## ✨ Features

- **🌤 Wetter** – Aktuelle Wetterdaten via OpenWeatherMap API (Temperatur, Wind, Beschreibung)
- **🖥 System Info** – CPU-, RAM-, Swap- und Festplattenauslastung als Echtzeit-Fortschrittsbalken
- **📰 Nachrichten** – RSS-Feed Slideshow (n-tv, Spiegel) mit automatischem Caching via SQLite
- **💬 Zitat des Tages** – Täglich wechselndes Zitat, automatisch von einer API geholt und lokal gespeichert
- **📅 Kalender** – Lokale Terminverwaltung mit Countdown-Anzeige (heute / morgen / in X Tagen)
- **📶 WiFi-Status** – Signalstärke als Sparkline-Verlauf im Header

---

## 🛠 Technologien

- [Textual](https://textual.textualize.io/) – TUI Framework
- [psutil](https://pypi.org/project/psutil/) – Systemdaten
- [requests](https://pypi.org/project/requests/) – HTTP-Anfragen
- [SQLite](https://www.sqlite.org/) – Lokales Caching & Datenspeicherung
- [OpenWeatherMap API](https://openweathermap.org/api) – Wetterdaten
- [quotable.io](https://api.quotable.io) / [ZenQuotes](https://zenquotes.io) – Zitate

---

## 🚀 Installation

**Es python 3.12.x sollte verwendet werden, da es bei python 3.14.x zu Fehlern mit psutil kommt.**

```bash
git clone https://github.com/AlexQlee/magicmirror-tui
cd magicmirror-tui
pip install -r requirements.txt
```

Erstelle eine `config.py` mit deinem OpenWeatherMap API-Key:

```python
API_KEY_OPENWEATHERMAP = "dein_api_key"
```

Dann starten mit:

```bash
python main.py
```


---

## ⚙️ Konfiguration

| Variable | Beschreibung |
|---|---|
| `API_KEY_OPENWEATHERMAP` | API-Key von openweathermap.org |
| `lat` / `lon` | Koordinaten für die Wetteranfrage |
| `uris` in `NewsWidget` | RSS-Feed URLs |

---

## 📝 Lizenz

MIT License – feel free to use and modify.
