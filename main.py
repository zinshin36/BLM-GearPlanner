import sys
import json
import requests
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel

# =====================================================
# CONFIG
# =====================================================

API_SEARCH_URL = "https://xivapi.com/search"
API_ITEM_URL = "https://xivapi.com/item"

MIN_ILVL = 700      # Adjust when new raid tier launches
MAX_ILVL = 999
JOB_CATEGORY = "Caster"

# =====================================================
# PATH HANDLING (FULLY PORTABLE)
# =====================================================

if getattr(sys, 'frozen', False):
    BASE_PATH = Path(sys.executable).parent
else:
    BASE_PATH = Path(__file__).parent

GEAR_FILE = BASE_PATH / "current_tier.json"
LOG_FILE = BASE_PATH / "runtime_log.txt"

# =====================================================
# LOGGING
# =====================================================

def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# =====================================================
# XIVAPI SEARCH (GET ITEM IDS)
# =====================================================

def search_gear_ids():
    log("Searching XIVAPI for caster gear...")

    params = {
        "indexes": "Item",
        "filters": f"LevelItem>={MIN_ILVL},LevelItem<={MAX_ILVL},ClassJobCategory.Name_en={JOB_CATEGORY}",
        "columns": "ID,Name,LevelItem,EquipSlotCategory.Name_en",
        "limit": 200
    }

    response = requests.get(API_SEARCH_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    return data.get("Results", [])

# =====================================================
# FETCH FULL ITEM DATA
# =====================================================

def fetch_full_item(item_id):
    response = requests.get(f"{API_ITEM_URL}/{item_id}", timeout=30)
    response.raise_for_status()
    return response.json()

# =====================================================
# PARSE STATS FROM ITEM
# =====================================================

def parse_stats(item_data):
    stats = {
        "Crit": 0,
        "DirectHit": 0,
        "Determination": 0,
        "SpellSpeed": 0
    }

    for param in item_data.get("BaseParam", []):
        name = param.get("BaseParam", {}).get("Name_en")
        value = param.get("Value", 0)

        if name == "Critical Hit":
            stats["Crit"] = value
        elif name == "Direct Hit Rate":
            stats["DirectHit"] = value
        elif name == "Determination":
            stats["Determination"] = value
        elif name == "Spell Speed":
            stats["SpellSpeed"] = value

    return stats

# =====================================================
# FETCH AND CACHE FULL GEAR DATA
# =====================================================

def fetch_and_cache_gear():
    log("Fetching full gear data...")

    basic_items = search_gear_ids()
    full_gear = []

    for item in basic_items:
        try:
            full_data = fetch_full_item(item["ID"])

            stats = parse_stats(full_data)

            gear_entry = {
                "ID": item["ID"],
                "Name": item["Name"],
                "ItemLevel": item["LevelItem"],
                "Slot": item.get("EquipSlotCategory", {}).get("Name_en"),
                "MateriaSlots": full_data.get("MateriaSlotCount", 0),
                "Stats": stats
            }

            full_gear.append(gear_entry)

            log(f"Loaded: {gear_entry['Name']}")

        except Exception as e:
            log(f"Failed to load item {item.get('Name')} - {e}")

    with open(GEAR_FILE, "w", encoding="utf-8") as f:
        json.dump(full_gear, f, indent=2)

    log(f"Saved {len(full_gear)} items to cache.")

    return full_gear

# =====================================================
# LOAD OR FETCH
# =====================================================

def load_gear():
    if GEAR_FILE.exists():
        log("Loading cached gear...")
        with open(GEAR_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        log("No cache found. Fetching from XIVAPI.")
        return fetch_and_cache_gear()

# =====================================================
# GUI
# =====================================================

class MainWindow(QMainWindow):
    def __init__(self, gear):
        super().__init__()
        self.setWindowTitle("BLM BiS Engine - Phase 2")

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Loaded {len(gear)} gear items."))
        layout.addWidget(QLabel("Stats + Materia slots extracted."))
        layout.addWidget(QLabel("Ready for Materia Solver Phase."))

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    try:
        gear = load_gear()
    except Exception as e:
        print("Fatal Error:", e)
        log(f"FATAL ERROR: {e}")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = MainWindow(gear)
    window.show()
    sys.exit(app.exec())
