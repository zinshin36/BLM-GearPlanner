import sys
import os
import logging
import traceback
from datetime import datetime

# -----------------------------
# FORCE LOG CREATION ALWAYS
# -----------------------------

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def setup_logging():
    base_path = get_base_path()
    log_path = os.path.join(base_path, "app_debug.log")

    logging.basicConfig(
        filename=log_path,
        filemode="a",
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    logging.info("=========================================")
    logging.info("Application Launch: %s", datetime.now())
    logging.info("Python Version: %s", sys.version)
    logging.info("Executable Path: %s", sys.executable)

    return log_path


log_file = setup_logging()

# -----------------------------
# WRAP EVERYTHING
# -----------------------------

try:
    logging.info("Importing PyQt6 modules...")
    from PyQt6.QtWidgets import QApplication, QLabel
    from PyQt6.QtCore import Qt

    logging.info("Creating QApplication...")
    app = QApplication(sys.argv)

    logging.info("Creating main window...")
    label = QLabel("Application Started Successfully")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.resize(500, 250)
    label.show()

    logging.info("Entering event loop...")
    sys.exit(app.exec())

except Exception:
    logging.critical("Fatal exception occurred:")
    logging.critical(traceback.format_exc())

    print("Fatal error. See app_debug.log for details.")
    print(traceback.format_exc())

    input("Press Enter to exit...")
