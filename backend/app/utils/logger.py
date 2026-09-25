import logging
import os

LOG_DIR = "/mnt/data/logs"


def get_logger(name: str, dataset: str):
    logger_name = f"{dataset}.{name}"
    logger = logging.getLogger(logger_name)

    if logger.handlers:
        return logger

    os.makedirs(LOG_DIR, exist_ok=True)

    log_file = os.path.join(
        LOG_DIR,
        f"{dataset}.log"
    )

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        log_file,
        mode="a",
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    return logger