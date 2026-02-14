import sys
import json
import requests
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel

# ============================================
# CONFIG
# ============================================

API_URL = "https://xivapi.com/search"
MIN_ILVL = 700      # Adjust per current tier
MAX_ILVL = 999
JOB_CATEGORY = "Caster"

# ============================================
# PATH HANDLING (Portable)
# ============================================

if getattr(sys, 'frozen', False):
    BASE_PATH = Path(sys.executable).parent
else:
    BASE_PATH = Path(__file__).parent

GEAR_FILE = BASE_PATH / "current_tier.json"
LOG_FILE = BASE_PATH / "runtime_log.txt"

# ============================================
# LOGGING
# ============================================

def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# ============================================
# FETCH GEAR FROM XIVAPI
# ============================================

def fetch_gear():
    log("Fetching gear from XIVAPI...")

    params = {
        "indexes": "Item",
        "filters": f"LevelItem>={MIN_ILVL},LevelItem<={MAX_ILVL},ClassJobCategory.Name_en={JOB_CATEGORY}",
        "columns": "ID,Name,LevelItem,EquipSlotCategory.Name_en",
        "limit": 200
    }

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    gear_list = []

    for item in data.get("Results", []):
        gear_list.append({
            "ID": item.get("ID"),
            "Name": item.get("Name"),
            "ItemLevel": item.get("LevelItem"),
            "Slot": item.get("EquipSlotCategory", {}).get("Name_en")
        })

    with open(GEAR_FILE, "w", encoding="utf-8") as f:
        json.dump(gear_list, f, indent=2)

    log(f"Saved {len(gear_list)} items.")
    return gear_list

# ============================================
# LOAD OR FETCH GEAR
# ============================================

def load_gear():
    if GEAR_FILE.exists():
        log("Loading cached gear...")
        with open(GEAR_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        log("No cached gear found. Fetching new data.")
        return fetch_gear()

# ============================================
# GUI
# ============================================

class MainWindow(QMainWindow):
    def __init__(self, gear):
        super().__init__()
        self.setWindowTitle("BLM BiS Solver (Phase 1)")

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Loaded {len(gear)} gear items."))
        layout.addWidget(QLabel("Gear cache saved locally."))
        layout.addWidget(QLabel("Next: Materia + Stat extraction phase."))

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    try:
        gear = load_gear()
    except Exception as e:
        print("Error loading gear:", e)
        log(f"ERROR: {e}")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = MainWindow(gear)
    window.show()
    sys.exit(app.exec())
