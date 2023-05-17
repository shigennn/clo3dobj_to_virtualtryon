import os
import datetime
from logging import getLogger, FileHandler, StreamHandler, Formatter

LOG_FILE_DIR = '../logs/'

FORMAT = '[%(asctime)s] %(name)s %(funcName)s [%(levelname)s]: %(message)s'

def get_root_logger(root_path: str, level: int) -> any:
    root_logger_name = os.path.splitext(os.path.basename(root_path))[0]
    logger = getLogger(root_logger_name)
    print(f'{type(logger)}')
    logger.setLevel(level)
    fh = FileHandler(f'{LOG_FILE_DIR}{str_today()}-{root_logger_name}.log')
    fh.setLevel(level)
    formatter = Formatter(FORMAT)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    sfh = StreamHandler()
    sfh.setFormatter(formatter)
    logger.addHandler(sfh)

    return logger

def str_today():
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d_%H%M%S")

