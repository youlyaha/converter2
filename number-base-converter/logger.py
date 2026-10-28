"""Модуль логирования приложения-конвертера."""

import logging
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_FILE = LOG_DIR / "app.log"


def setup_logging() -> logging.Logger:
    """Создаёт журнал и настраивает запись событий в logs/app.log."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("converter")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Не добавляем повторные обработчики при повторном вызове функции.
    if not logger.handlers:
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setLevel(logging.INFO)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)

    return logger


logger = setup_logging()
