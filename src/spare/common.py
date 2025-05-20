from pathlib import Path

SERVICE_NAME = "spare"

CONFIG_DIR_PATH = Path.home() / ".config" / SERVICE_NAME
DATA_DIR_PATH = Path.home() / ".local" / "share" / SERVICE_NAME

CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.toml"
LOG_FILE_PATH = DATA_DIR_PATH / f"{SERVICE_NAME}.log"
