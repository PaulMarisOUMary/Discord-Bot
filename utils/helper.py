from importlib import reload
import logging
from sys import modules
from types import ModuleType
import discord

from discord import app_commands
from discord.ext import commands
from dotenv import dotenv_values
from json import load as json_load
from os import environ, listdir, sep
from os.path import dirname, abspath, getmtime, join, basename, splitext
from typing import Any, Awaitable, Callable, Dict, Generator, List, Literal, NoReturn, Optional, Tuple, Union

from utils.basetypes import MISSING


root_directory = dirname(dirname(abspath(__file__)))


def json_to_dict(file_path: str) -> Dict[Any, Any]:
    with open(file_path, "r", encoding="utf-8") as file:
        return json_load(file)


def load_configs(folder: str = MISSING, files: List[str] = MISSING) -> Dict[Any, Any]:
    """Paths should be relative to the project root directory."""
    if (folder is MISSING) and (files is MISSING):
        raise ValueError("Either 'folder' or 'files' must be provided.")

    config = dict()
    
    paths = files
    if folder is not MISSING:
        paths = [
            join(folder, file)
            for file in listdir(join(root_directory, folder))
            if file.endswith(".json")
        ]

    for path in paths:
        name, _ = splitext(basename(path))
        config[name] = json_to_dict(join(root_directory, path))

    return config


def load_envs(files: List[str]) -> Dict[Any, Any]:
    """Paths should be relative to the project root directory."""
    env: Dict[str, Any] = dict(environ)

    for file in files:
        env.update(dotenv_values(join(root_directory,file)))

    return env


def get_cogs(folder: str) -> List[str]:
    """Paths should be relative to the project root directory."""
    cogs: List[str] = []

    path = join(root_directory, folder)

    for filename in listdir(path):
        if filename.endswith(".py") and not filename.startswith("_"):
            cogs.append(f"cogs.{filename[:-3]}")

    return cogs


def _cog_to_path(cog: str) -> str:
    """Map 'cogs.foo' -> '<root>/<folder>/foo.py'."""
    return join(root_directory, f"{cog.replace('.', sep)}.py")


def sort_cogs(cogs: List[str], sortby: Optional[Callable[[str], Any]] = None, reverse: bool = False) -> List[str]:
    """Cogs names must be dot separated like regular Python imports if accessing a sub-module. e.g. `foo.test` if you want to import `foo/test.py`."""
    def default_sortby(cog: str) -> Tuple[float, str]:
        try:
            mtime = getmtime(_cog_to_path(cog))
        except OSError:
            mtime = 0.0
        return (-mtime, cog)

    return sorted(cogs, key=sortby or default_sortby, reverse=reverse)


async def cogs_manager(bot: commands.Bot, action: Literal["load", "unload", "reload"], cogs: List[str]) -> None:
    """Cogs names must be dot separated like regular Python imports if accessing a sub-module. e.g. `foo.test` if you want to import `foo/test.py`."""
    actions: dict[str, Callable[[str], Awaitable[None]]] = {
        "load": bot.load_extension,
        "unload": bot.unload_extension,
        "reload": bot.reload_extension,
    }

    action_func = actions[action]

    for cog in cogs:
        try:
            await action_func(cog)
        except Exception as e:
            raise e


def reload_views() -> Generator[str, None, None]:
    for mod in modules.values():
        if not isinstance(mod, ModuleType):
            continue
        
        try:
            if basename(dirname(str(mod.__file__))) == "views":
                reload(mod)
                yield mod.__name__
        except (AttributeError, ImportError):
            pass


def set_logging(file_level: int = logging.DEBUG, console_level: int = logging.INFO, filename: str = "discord.log") -> tuple[logging.Logger, logging.StreamHandler]:
    """Sets up logging for the bot."""
    
    logger = logging.getLogger("discord") # discord.py logger
    logger.setLevel(logging.DEBUG)
    log_formatter = logging.Formatter(fmt="[{asctime}] [{levelname:<8}] {name}: {message}", datefmt="%Y-%m-%d %H:%M:%S", style="{")

    # File-logs
    file_handler = logging.FileHandler(filename=join(root_directory, filename), encoding="utf-8", mode='w')
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(file_level)
    logger.addHandler(file_handler)

    # Console-logs
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(console_level)
    logger.addHandler(console_handler)

    return logger, console_handler


def bot_has_permissions(**perms: bool):
    """A decorator that add specified permissions to Command.extras and add bot_has_permissions check to Command with specified permissions.
    
    Warning:
    - This decorator must be on the top of the decorator stack
    - This decorator is not compatible with commands.check()
    """
    def wrapped(command: Union[app_commands.Command, commands.HybridCommand, commands.Command]) -> Union[app_commands.Command, commands.HybridCommand, commands.Command]:
        if not isinstance(command, (app_commands.Command, commands.hybrid.HybridCommand, commands.Command)):
            raise TypeError(f"Cannot decorate a class that is not a subclass of Command, get: {type(command)} must be Command")

        valid_required_permissions = [
            perm for perm, value in perms.items() if getattr(discord.Permissions.none(), perm) != value
        ]
        command.extras.update({"bot_permissions": valid_required_permissions})

        if isinstance(command, commands.HybridCommand) and command.app_command:
            command.app_command.extras.update({"bot_permissions": valid_required_permissions})

        if isinstance(command, (app_commands.Command, commands.HybridCommand)):
            app_commands.checks.bot_has_permissions(**perms)(command)
        if isinstance(command, (commands.Command, commands.HybridCommand)):
            commands.bot_has_permissions(**perms)(command)

        return command

    return wrapped
