import logging
from config import LOG_FILE

def setup_logger():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logging.info("=========================================")
    logging.info("Application Launch")

def log_info(msg: str):
    print(msg)
    logging.info(msg)
