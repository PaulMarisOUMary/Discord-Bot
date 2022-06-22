import asyncio
import discord
import logging
import platform

from discord.ext import commands
from discord import app_commands

from importlib import reload
from json import load
from os import listdir
from os.path import dirname, abspath, join, basename, splitext
from sys import modules
from types import ModuleType
from typing import Any

root_directory = dirname(dirname(abspath(__file__)))
config_directory = join(root_directory, "config")
cogs_directory = join(root_directory, "cogs")

def credential(file: str) -> dict:
	with open(join(config_directory, file), "r") as f:
		return load(f)

def load_config() -> dict:
	config = dict()
	for file in listdir(config_directory):
		filename, ext = splitext(file)
		if ext == ".json":
			config[filename] = credential(file)
	return config

async def cogs_manager(bot: commands.Bot, mode: str, cogs: list[str]) -> None:
	for cog in cogs:
		try:
			if mode == "unload":
				await bot.unload_extension(cog)
			elif mode == "load":
				await bot.load_extension(cog)
			elif mode == "reload":
				await bot.reload_extension(cog)
			else:
				raise ValueError("Invalid mode.")
		except Exception as e:
			raise e

def reload_views():
	mods = [module[1] for module in modules.items() if isinstance(module[1], ModuleType)]
	for mod in mods:
		try:
			if basename(dirname(mod.__file__)) == "views":
				reload(mod)
				yield mod.__name__
		except: 
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

def clean_close() -> None:
	if platform.system().lower() == 'windows':
		asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def bot_has_permissions(**perms: bool):
	def wrapped(command: app_commands.Command[Any, ..., Any]) -> app_commands.Command[Any, ..., Any]:
		if not isinstance(command, app_commands.Command):
			raise TypeError(f"Cannot decorate a class that is not a subclass of Command, get: {type(command)} must be Command")

		valid_required_permissions = [
			perm for perm, value in perms.items() if getattr(discord.Permissions.none(), perm) != value
		]
		command.extras.update({"bot_permissions": valid_required_permissions})
		
		app_commands.checks.bot_has_permissions(**perms)(command)

		return command

	return wrapped