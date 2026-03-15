import json
import sys

CONFIG_PATH = "config.json"


def load_config(path: str = CONFIG_PATH) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Fehler: '{path}' nicht gefunden. Bitte config.json anlegen (siehe config.json als Vorlage).")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Fehler beim Parsen der config.json: {e}")
        sys.exit(1)


def get_module_config(config: dict, module: str) -> dict:
    return config.get("modules", {}).get(module, {})
