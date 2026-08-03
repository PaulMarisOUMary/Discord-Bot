from logging import DEBUG, INFO, Formatter, StreamHandler, getLogger
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from discord.utils import setup_logging as d_logging


def setup_logging(
    log_dir: Path = Path("logs"), file_level: int = INFO, stream_level: int = INFO
) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)

    d_logging(level=DEBUG)
    root_logger = getLogger()

    for handler in root_logger.handlers:
        if isinstance(handler, StreamHandler):
            handler.setLevel(stream_level)

    file_formatter = Formatter(
        fmt="[{asctime}] [{levelname:<8}] {name}: {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )
    file_handler = TimedRotatingFileHandler(
        filename=log_dir / "bot.log",
        when="D",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(file_level)

    root_logger.addHandler(file_handler)
