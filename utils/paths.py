from pathlib import Path

utils_dir = Path(__file__).resolve().parent

root_dir = utils_dir.parent

config_dir = root_dir / "config"
env_path = config_dir / ".env"
log_dir = root_dir / "logs"
