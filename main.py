import sys
import threading
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
)
from solver_engine import SolverEngine
from data_models import CharacterStats


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FFXIV Solver - Phase 1")
        self.setGeometry(200, 200, 650, 550)

        self.engine = SolverEngine()
        self.inputs = {}

        layout = QVBoxLayout()

        fields = [
            "Main Stat",
            "Crit",
            "Direct Hit",
            "Determination",
            "Skill Speed",
            "Weapon Damage",
        ]

        for field in fields:
            label = QLabel(field)
            entry = QLineEdit()
            entry.setText("1000")
            layout.addWidget(label)
            layout.addWidget(entry)
            self.inputs[field] = entry

        self.run_button = QPushButton("Calculate DPS")
        self.run_button.clicked.connect(self.run_solver)
        layout.addWidget(self.run_button)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def run_solver(self):
        self.output.append("Starting calculation...")
        thread = threading.Thread(target=self.calculate, daemon=True)
        thread.start()

    def calculate(self):
        try:
            stats = CharacterStats(
                main_stat=int(self.inputs["Main Stat"].text()),
                crit=int(self.inputs["Crit"].text()),
                direct_hit=int(self.inputs["Direct Hit"].text()),
                determination=int(self.inputs["Determination"].text()),
                skill_speed=int(self.inputs["Skill Speed"].text()),
                weapon_damage=int(self.inputs["Weapon Damage"].text()),
            )

            dps = self.engine.calculate_dps(stats)
            self.output.append(f"Calculated DPS: {dps}")

        except Exception as e:
            self.output.append(f"Error: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
