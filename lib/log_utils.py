import os
import sys
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
import logging
from pathlib import Path

Path('./log').mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=f'./log/ddns.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    filemode='w'
)

def log_print(msg,log_level="INFO"):
    if log_level == "INFO":
        logging.info(msg)
        print(msg)
    elif log_level == "WARNING":
        logging.warning(msg)
        print(msg)
    elif log_level == "DEBUG":
        logging.debug(msg)
        print(msg)
    elif log_level == "ERROR":
        logging.error(msg)
        print(msg)