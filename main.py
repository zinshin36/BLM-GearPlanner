import json
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox

LOG_FILE = "runtime_log.txt"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

# Load gear
data_path = Path("data/gear.json")
if not data_path.exists():
    log("gear.json not found!")
    sys.exit("gear.json not found!")

with open(data_path) as f:
    gear = json.load(f)

# Simple DPS calculator
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

# Build GUI
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BLM DPS Simulator")
        layout = QVBoxLayout()

        self.head_combo = QComboBox()
        self.head_combo.addItems([g["Name"] for g in gear["Head"]])
        layout.addWidget(QLabel("Head Gear"))
        layout.addWidget(self.head_combo)

        self.body_combo = QComboBox()
        self.body_combo.addItems([g["Name"] for g in gear["Body"]])
        layout.addWidget(QLabel("Body Gear"))
        layout.addWidget(self.body_combo)

        self.result_label = QLabel("DPS: ")
        layout.addWidget(self.result_label)

        btn = QPushButton("Simulate DPS")
        btn.clicked.connect(self.simulate)
        layout.addWidget(btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def simulate(self):
        try:
            head = next(g for g in gear["Head"] if g["Name"] == self.head_combo.currentText())
            body = next(g for g in gear["Body"] if g["Name"] == self.body_combo.currentText())
            crit = head["Crit"] + body["Crit"]
            dh = head["DirectHit"] + body["DirectHit"]
            det = head["Determination"] + body["Determination"]
            sps = head["SpellSpeed"] + body["SpellSpeed"]

            dps = calculate_dps(crit, dh, det, sps)
            self.result_label.setText(f"DPS: {dps:.2f}")
            log(f"Simulated DPS: {dps:.2f} | Head: {head['Name']} | Body: {body['Name']}")
        except Exception as e:
            log(f"Simulation error: {e}")
            QMessageBox.critical(self, "Error", f"Simulation failed:\n{e}")

# Run app
if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    log("Application started.")
    sys.exit(app.exec())
