import asyncio
import logging
import platform

from sys import modules
from json import load
from types import ModuleType
from os import listdir
from os.path import dirname, abspath, join, basename, splitext
from discord.ext import commands
from importlib import reload

root_directory = dirname(dirname(abspath(__file__)))
config_directory = join(root_directory, "config")
cogs_directory = join(root_directory, "cogs")

def credential(file) -> dict:
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

def set_logging(level = logging.WARNING, filename: str = "discord.log") -> None:
	logger = logging.getLogger('discord')
	logger.setLevel(level)
	handler = logging.FileHandler(filename=filename, encoding='utf-8', mode='w')
	handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
	logger.addHandler(handler)

def clean_close() -> None:
	if platform.system().lower() == 'windows':
		asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())