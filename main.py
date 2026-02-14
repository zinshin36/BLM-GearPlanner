import sys
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QComboBox, QCheckBox, QProgressBar
from PySide6.QtCore import Qt
from config import ILVL_WINDOW_DEFAULT, PRIORITY_MODES, THEMES
from gear_cache import load_cache, refresh_gear_cache
from tier_detector import detect_max_ilvl, filter_by_ilvl_window
from brute_solver import solve_bis

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BLM Perfect BiS Engine")
        self.cache = load_cache() or {"gear": [], "max_ilvl":0, "theme":"Dark"}
        self.max_ilvl = self.cache["max_ilvl"]
        self.theme = self.cache.get("theme","Dark")
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        main = QVBoxLayout()

        # Max Ilvl label
        self.label_ilvl = QLabel(f"Detected Max ILvl: {self.max_ilvl}")
        main.addWidget(self.label_ilvl)

        # Ilvl window slider
        slider_layout = QHBoxLayout()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(5)
        self.slider.setMaximum(60)
        self.slider.setValue(ILVL_WINDOW_DEFAULT)
        self.slider.valueChanged.connect(self.update_window_label)
        self.window_label = QLabel(f"Window: {self.slider.value()}")
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.window_label)
        main.addLayout(slider_layout)

        # Priority mode dropdown
        self.priority_dropdown = QComboBox()
        self.priority_dropdown.addItems(PRIORITY_MODES)
        main.addWidget(self.priority_dropdown)

        # Checkboxes
        self.chk_relic = QCheckBox("Include Relic Weapons")
        self.chk_pvp = QCheckBox("Exclude PvP Gear")
        main.addWidget(self.chk_relic)
        main.addWidget(self.chk_pvp)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh Gear (Expansion)")
        self.btn_refresh.clicked.connect(self.refresh_gear)
        self.btn_calc = QPushButton("Recalculate BiS")
        self.btn_calc.clicked.connect(self.run_solver)
        self.btn_theme = QPushButton("Toggle Light/Dark")
        self.btn_theme.clicked.connect(self.toggle_theme)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_calc)
        btn_layout.addWidget(self.btn_theme)
        main.addLayout(btn_layout)

        # Progress and output
        self.progress = QProgressBar()
        main.addWidget(self.progress)
        self.output_label = QLabel("Solver output will appear here")
        main.addWidget(self.output_label)

        container = QWidget()
        container.setLayout(main)
        self.setCentralWidget(container)

    def update_window_label(self):
        self.window_label.setText(f"Window: {self.slider.value()}")

    def refresh_gear(self):
        self.output_label.setText("Refreshing gear cache...")
        QApplication.processEvents()
        self.cache["gear"], self.max_ilvl = refresh_gear_cache()
        self.cache["max_ilvl"] = self.max_ilvl
        self.label_ilvl.setText(f"Detected Max ILvl: {self.max_ilvl}")
        self.output_label.setText(f"Loaded {len(self.cache['gear'])} gear items.")

    def run_solver(self):
        self.output_label.setText("Running solver...")
        QApplication.processEvents()
        window = self.slider.value()
        filtered_gear = filter_by_ilvl_window(self.cache["gear"], self.max_ilvl, window)
        priority = self.priority_dropdown.currentText()
        best_build, best_dps = solve_bis(filtered_gear, priority)
        if best_build:
            out_text = f"Best DPS: {best_dps:.2f}\nGear:\n"
            for piece in best_build:
                out_text += f"{piece['Slot']}: {piece['Name']}\n"
            self.output_label.setText(out_text)
        else:
            self.output_label.setText("No valid build found.")

    def toggle_theme(self):
        self.theme = "Light" if self.theme=="Dark" else "Dark"
        self.apply_theme()
        self.cache["theme"] = self.theme
        Path("data/gear_cache.json").parent.mkdir(exist_ok=True)
        with open("data/gear_cache.json","w") as f:
            json.dump(self.cache,f,indent=2)

    def apply_theme(self):
        if self.theme=="Dark":
            self.setStyleSheet("background-color:#121212;color:#FFFFFF;")
        else:
            self.setStyleSheet("background-color:#FFFFFF;color:#000000;")

if __name__=="__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
