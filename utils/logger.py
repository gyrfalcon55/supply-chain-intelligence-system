import os
import logging
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logs_path = os.path.join(BASE_DIR, "..", "logs")
logs_path = os.path.abspath(logs_path)

os.makedirs(logs_path, exist_ok=True)

LOG_FILE = datetime.now().strftime("%m_%d_%Y_%H_%M_%S.log")
LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)