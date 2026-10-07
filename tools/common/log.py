"""Console logging for the ad pipeline CLIs.

Library code only calls ``logging.getLogger(__name__)``; the CLI entry point decides
where messages go. Progress lines are printed as-is (they are the tool's UI), while
warnings and errors keep their level as a prefix.
"""
from __future__ import annotations

import logging
import sys

# Parent of every ``tools.*`` module logger.
ROOT_LOGGER = "tools"


class _ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        return message if record.levelno < logging.WARNING else f"[{record.levelname}] {message}"


def configure_cli_logging(level: int = logging.INFO) -> logging.Logger:
    """Send ``tools.*`` logs to stdout once; safe to call repeatedly."""
    logger = logging.getLogger(ROOT_LOGGER)
    if not any(getattr(h, "_flowkit_cli", False) for h in logger.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_ConsoleFormatter("%(message)s"))
        handler._flowkit_cli = True  # type: ignore[attr-defined]
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger


__all__ = ["ROOT_LOGGER", "configure_cli_logging"]
