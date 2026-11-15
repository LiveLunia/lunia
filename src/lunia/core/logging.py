import copy
import logging
from pathlib import Path


def hex_to_ansi(hex_color: str) -> str:
    """将 HEX 颜色转换为 ANSI 24-bit 前景色序列."""
    color = hex_color.lstrip("#")
    r, g, b = (int(color[i : i + 2], 16) for i in (0, 2, 4))
    return f"\033[38;2;{r};{g};{b}m"


LEVEL_COLORS = {
    logging.DEBUG: hex_to_ansi("#9AA0A6"),
    logging.INFO: hex_to_ansi("#66CCFF"),
    logging.WARNING: hex_to_ansi("#E5B84B"),
    logging.ERROR: hex_to_ansi("#E45656"),
    logging.CRITICAL: hex_to_ansi("#E186FF"),
}
RESET = "\033[0m"
LEVEL_NAMES = {
    logging.WARNING: "WARN",
    logging.CRITICAL: "FATAL",
}


class LuniaFormatter(logging.Formatter):
    """Lunia CLI日志格式化器."""

    def format(self, record: logging.LogRecord) -> str:
        new_record = copy.copy(record)
        level = LEVEL_NAMES.get(
            record.levelno,
            record.levelname,
        )
        color = LEVEL_COLORS.get(record.levelno, "")
        new_record.levelname = f"{color}{level.ljust(5)}{RESET}"
        return super().format(new_record)


def setup_logging() -> None:
    """初始化 Lunia 日志系统."""
    logger = logging.getLogger("lunia")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if logger.handlers:
        return

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console_formatter = LuniaFormatter(
        fmt="%(levelname)s %(asctime)s.%(msecs)03d [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    console.setFormatter(console_formatter)
    logger.addHandler(console)

    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(
        log_dir / "lunia.log",
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler_formatter = logging.Formatter(
        fmt="%(levelname)-8s %(asctime)s.%(msecs)03d [%(name)s] %(message)s",
        datefmt="%y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_handler_formatter)
    logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """获取 Lunia 模块 Logger."""
    logger = logging.getLogger(name)
    return logger
