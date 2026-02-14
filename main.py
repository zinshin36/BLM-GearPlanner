import json
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QHBoxLayout

LOG_FILE = "runtime_log.txt"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

# Load gear data
data_path = Path("data/gear.json")
if not data_path.exists():
    log("gear.json not found!")
    raise FileNotFoundError("gear.json not found!")

with open(data_path) as f:
    gear = json.load(f)

# Calculate DPS
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

# Best-in-slot selection
def best_in_slot(slot_name):
    items = gear.get(slot_name, [])
    if not items:
        return None
    # Simple BIS: sum of all stats
    return max(items, key=lambda g: g["Crit"] + g["DirectHit"] + g["Determination"] + g["SpellSpeed"])

# GUI
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BLM DPS Simulator (Full Slots)")

        self.slots = ["Head", "Body", "Hands", "Legs", "Feet", "Accessories"]
        self.combos = {}

        layout = QVBoxLayout()
        for slot in self.slots:
            label = QLabel(f"{slot} Gear")
            combo = QComboBox()
            items = [g["Name"] for g in gear.get(slot, [])]
            combo.addItems(items)
            # Select best-in-slot automatically
            bis = best_in_slot(slot)
            if bis:
                combo.setCurrentText(bis["Name"])
            layout.addWidget(label)
            layout.addWidget(combo)
            self.combos[slot] = combo

        # Optional: show DPS configuration boxes
        config_layout = QHBoxLayout()
        self.configs = {}
        for stat in ["Crit", "DirectHit", "Determination", "SpellSpeed"]:
            lbl = QLabel(stat)
            cb = QComboBox()
            cb.addItems([str(i) for i in range(0, 501, 50)])  # allow user to adjust base stats
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
                selected = next((g for g in gear[slot] if g["Name"] == combo.currentText()), None)
                if selected:
                    for stat in total_stats:
                        total_stats[stat] += selected[stat]

            dps = calculate_dps(total_stats["Crit"], total_stats["DirectHit"], total_stats["Determination"], total_stats["SpellSpeed"])
            self.result_label.setText(f"Estimated DPS: {dps:.2f}")

            log(f"Simulation complete. DPS: {dps:.2f} | Gear: " +
                ", ".join([f"{slot}:{combo.currentText()}" for slot, combo in self.combos.items()]))
        except Exception as e:
            log(f"Simulation ERROR: {e}")
            QMessageBox.critical(self, "Error", f"Simulation failed:\n{e}")

# Run application
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    log("Application started.")
    sys.exit(app.exec())
