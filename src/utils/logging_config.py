"""
src/utils/logging_config.py

Jednotny logging setup pro cely projekt.
Pouziti v kazdem modulu:

    from src.utils.logging_config import get_logger
    logger = get_logger(__name__)
"""

from __future__ import annotations

import logging
import sys


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:  # ochrana proti duplicitnim handlerum pri opakovanem importu
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger
