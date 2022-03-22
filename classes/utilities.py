from sys import modules
from json import load
from types import ModuleType
from os.path import dirname, abspath, join, basename
from discord.ext import commands
from importlib import reload

root_directory = dirname(dirname(abspath(__file__)))
config_directory = join(root_directory, "config")
cogs_directory = join(root_directory, "cogs")

def credential(file):
    with open(join(config_directory, file), "r") as f:
        return load(f)

bot_data = credential("bot.json")
database_data = credential("database.json")

async def cogs_manager(bot: commands.Bot, mode: str, cogs: str) -> None:
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
            print(f"{mode} {cog} failed: {e}")
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