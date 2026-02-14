import json
from pathlib import Path

DATA_FILE = Path("data/current_tier.json")

def load_gear():
    if not DATA_FILE.exists():
        raise FileNotFoundError("No cached gear found. Run fetch_gear.py first.")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
