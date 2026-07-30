from os import environ
from pathlib import Path

from dotenv import dotenv_values
from msgspec import convert
from msgspec.toml import decode

from models.config import Config


def load_env(*files: Path) -> dict[str, str | None]:
    env: dict[str, str | None] = dict(environ)

    for file in files:
        if file.exists:
            file_env = {k.lower(): v for k, v in dotenv_values(file).items()}
            env.update(file_env)

    return env


def load_config(config_dir: Path, env_path: Path) -> Config:
    if not config_dir.exists() or not config_dir.is_dir():
        raise FileNotFoundError(f"'{config_dir}' not found.")

    config = {}

    for file in config_dir.glob("*.toml"):
        namespace = file.stem

        with open(file, "rb") as f:
            config[namespace] = decode(f.read(), type=dict)

    config["env"] = load_env(env_path)

    return convert(config, Config, strict=False)
