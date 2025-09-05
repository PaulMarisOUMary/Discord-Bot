import discord
import os

from typing import Optional
from datetime import datetime
from discord.ext import commands
from discord.utils import format_dt

from utils.basebot import DiscordBot
from utils.basetypes import GuildContext
from utils.helper import bot_has_permissions, cogs_manager, load_configs, load_envs, sort_cogs

class Admin(commands.Cog, name="admin"):
    """
        Admin commands.

        Require intents: 
            - message_content
        
        Require bot permission:
            - read_messages
            - send_messages
            - attach_files
    """
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

    def help_custom(self) -> tuple[str, str, str]:
        emoji = '⚙️'
        label = "Admin"
        description = "Show the list of admin commands."
        return emoji, label, description
    
    @bot_has_permissions(send_messages=True)
    @commands.command(name="loadcog", aliases=["load"])
    @commands.is_owner()
    async def load_cog(self, ctx: commands.Context, cog: str) -> None:
        """Load a cog."""
        await cogs_manager(self.bot, "load", [f"cogs.{cog}"])
        await ctx.send(f":point_right: Cog {cog} loaded!")

    @bot_has_permissions(send_messages=True)
    @commands.command(name="unloadcog", aliases=["unload"])
    @commands.is_owner()
    async def unload_cog(self, ctx: commands.Context, cog: str) -> None:
        """Unload a cog."""
        await cogs_manager(self.bot, "unload", [f"cogs.{cog}"])
        await ctx.send(f":point_left: Cog {cog} unloaded!")

    @bot_has_permissions(send_messages=True)
    @commands.command(name="reloadcog", aliases=["reload", "rel"], require_var_positional=True)
    @commands.is_owner()
    async def reload_specified_cogs(self, ctx: commands.Context, *cogs: str) -> None:
        """Reload specific cogs."""
        reload_cogs = [f"cogs.{cog}" for cog in cogs]
        await cogs_manager(self.bot, "reload", reload_cogs)

        await ctx.send(f":thumbsup: `{'` `'.join(cogs)}` reloaded!")

    @bot_has_permissions(send_messages=True)
    @commands.command(name="reloadlatest", aliases=["rl"])
    @commands.is_owner()
    async def reload_latest_cogs(self, ctx: commands.Context, n_cogs: int = 1) -> None:
        """Reload the latest edited n cogs."""
        cogs = [
            f"cogs.{cog}"
            for cog in sort_cogs(list(self.bot.cogs.keys()), folder="./cogs")[:n_cogs]
        ]
        await cogs_manager(self.bot, "reload", cogs)

        await ctx.send(f":point_down: `{'` `'.join(cogs)}` reloaded!")

    @bot_has_permissions(send_messages=True)
    @commands.command(name="reloadallcogs", aliases=["rell"])
    @commands.is_owner()
    async def reload_all_cogs(self, ctx: commands.Context) -> None:
        """Reload all cogs."""
        cogs = [
            f"cogs.{name}"
            for name in self.bot.cogs.keys()
        ]
        await cogs_manager(self.bot, "reload", cogs)	

        await ctx.send(f":muscle: All cogs reloaded: `{len(cogs)}`!")

    @bot_has_permissions(send_messages=True)
    @commands.command(name="changeprefix", aliases=["cp", "prefix"], require_var_positional=True)
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def change_guild_prefix(self, ctx: GuildContext, new_prefix: str) -> None:
        """Change the guild prefix."""
        if not self.bot.use_database or not ctx.guild:
            await ctx.send(":warning: Database not used, prefix not changed.")
            return
        try:
            table = self.bot.config["bot"]["prefix"]["table"]
            await self.bot.database.insert_onduplicate(table, {"guild_id": ctx.guild.id, "guild_prefix": new_prefix})

            self.bot.prefixes[ctx.guild.id] = new_prefix
            await ctx.send(f":warning: Prefix changed to `{new_prefix}`")
        except Exception as e:
            await ctx.send(f"Error: {e}")
    
    @bot_has_permissions(send_messages=True)
    @commands.command(name="reloadconfig", aliases=["rc"])
    @commands.is_owner()
    async def reload_config(self, ctx: commands.Context, *config_files: str) -> None:
        """Reload each json config file."""
        if not config_files:
            config = load_configs(folder="./config")
            env = load_envs(files=["./config/.env"])

            self.bot.config.update(config)
            self.bot.config["env"].update(env)

            await ctx.send(f":handshake: `{len(self.bot.config)}` config file(s) reloaded!")
        else:
            for file in config_files:
                if file == ".env":
                    env = load_envs(files=[f"./config/{file}"])
                    self.bot.config["env"].update(env)
                else:
                    partial_config = load_configs(files=[f"./config/{file}"])
                    if partial_config:
                        self.bot.config.update(partial_config)
            
            await ctx.send(f":handshake: `{len(config_files)}` config file(s) reloaded!")


    @bot_has_permissions(send_messages=True)
    @commands.command(name="test")
    @commands.is_owner()
    async def test(self, ctx: commands.Context) -> None:
        pass


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Admin(bot))