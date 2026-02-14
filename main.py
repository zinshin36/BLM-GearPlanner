import sys
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QHBoxLayout

# --- Logging function ---
LOG_FILE = "runtime_log.txt"
def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

# --- Determine base path (works in PyInstaller EXE too) ---
if getattr(sys, 'frozen', False):
    # Running as EXE
    base_path = Path(sys._MEIPASS)
else:
    # Running as script
    base_path = Path(__file__).parent

data_path = base_path / "data" / "gear.json"

# --- Load gear data ---
if not data_path.exists():
    raise FileNotFoundError(f"gear.json not found at {data_path}")

with open(data_path, "r") as f:
    gear = json.load(f)

# --- DPS calculator ---
def calculate_dps(crit, dh, det, sps):
    BaseSub = 400
    LevelDiv = 1900
    gcd = (2500 - int(130*(sps-BaseSub)/LevelDiv)) / 1000
    casts = 60 / gcd
    potency = casts * 310
    critRate = (200*(crit-BaseSub)/LevelDiv + 50)/1000
    critBonus = (200*(crit-BaseSub)/LevelDiv + 1400)/1000
    dhRate = (550*(dh-BaseSub)/LevelDiv)/1000
    detBonus = (140*(det-BaseSub)/LevelDiv + 1000)/1000
    spsBonus = 1 + (sps-BaseSub)/10000
    multiplier = detBonus*(1 + critRate*(critBonus-1))*(1 + dhRate*0.25)*spsBonus
    return potency/60 * multiplier

# --- Best-in-slot selection ---
def best_in_slot(slot_name, top_n=3):
    items = gear.get(slot_name, [])
    if not items:
        return []
    sorted_items = sorted(items, key=lambda g: g["Crit"]+g["DirectHit"]+g["Determination"]+g["SpellSpeed"], reverse=True)
    return sorted_items[:top_n]

# --- GUI ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BLM DPS Simulator (Portable)")

        self.slots = ["Head", "Body", "Hands", "Legs", "Feet", "Accessories"]
        self.combos = {}

        layout = QVBoxLayout()
        for slot in self.slots:
            label = QLabel(f"{slot} Gear (Top 3 options)")
            combo = QComboBox()
            top_items = best_in_slot(slot)
            if not top_items:
                combo.addItem("No gear")
            else:
                for g in top_items:
                    combo.addItem(g["Name"])
                combo.setCurrentText(top_items[0]["Name"])
            layout.addWidget(label)
            layout.addWidget(combo)
            self.combos[slot] = combo

        # Base stat configuration
        config_layout = QHBoxLayout()
        self.configs = {}
        for stat in ["Crit", "DirectHit", "Determination", "SpellSpeed"]:
            lbl = QLabel(stat)
            cb = QComboBox()
            cb.addItems([str(i) for i in range(0, 501, 50)])
            cb.setCurrentText("0")
            config_layout.addWidget(lbl)
            config_layout.addWidget(cb)
            self.configs[stat] = cb
        layout.addLayout(config_layout)

        self.result_label = QLabel("Estimated DPS: ")
        layout.addWidget(self.result_label)

        btn = QPushButton("Simulate DPS")
        btn.clicked.connect(self.simulate)
        layout.addWidget(btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def simulate(self):
        try:
            total_stats = {"Crit":0, "DirectHit":0, "Determination":0, "SpellSpeed":0}

            # Add configured base stats
            for stat, combo in self.configs.items():
                total_stats[stat] += int(combo.currentText())

            # Add gear stats
            for slot, combo in self.combos.items():
                selected_name = combo.currentText()
                selected = next((g for g in gear.get(slot, []) if g["Name"] == selected_name), None)
                if selected:
                    for stat in total_stats:
                        total_stats[stat] += selected[stat]
                else:
                    bis_items = best_in_slot(slot)
                    if bis_items:
                        for stat in total_stats:
                            total_stats[stat] += bis_items[0][stat]
                        log(f"Auto-selected BIS for {slot}: {bis_items[0]['Name']}")

            dps = calculate_dps(total_stats["Crit"], total_stats["DirectHit"], total_stats["Determination"], total_stats["SpellSpeed"])
            self.result_label.setText(f"Estimated DPS: {dps:.2f}")

            log(f"Simulation complete. DPS: {dps:.2f} | Gear: " +
                ", ".join([f"{slot}:{combo.currentText()}" for slot, combo in self.combos.items()]))
        except Exception as e:
            log(f"Simulation ERROR: {e}")
            QMessageBox.critical(self, "Error", f"Simulation failed:\n{e}")

# --- Run app ---
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    log("Application started.")
    sys.exit(app.exec())
