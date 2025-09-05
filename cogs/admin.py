import discord

from typing import Optional
from datetime import datetime
from discord.ext import commands
from discord.utils import format_dt
from os.path import join

from utils.basebot import DiscordBot
from utils.basetypes import GuildContext
from utils.helper import bot_has_permissions, cogs_manager, load_configs, load_envs, reload_views, root_directory, sort_cogs

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
    @commands.command(name="reloadcogs", aliases=["reload", "rel"], require_var_positional=True)
    @commands.is_owner()
    async def reload_cogs(self, ctx: commands.Context, *cogs: str) -> None:
        """Reload specific cogs."""
        reload_cogs = [f"cogs.{cog}" for cog in cogs]
        await cogs_manager(self.bot, "reload", reload_cogs)

        await ctx.send(f":thumbsup: `{'` `'.join(cogs)}` reloaded!")

    @bot_has_permissions(send_messages=True)
    @commands.command(name="reloadlatest", aliases=["rl"])
    @commands.is_owner()
    async def reload_cogs_latest(self, ctx: commands.Context, n_cogs: int = 1) -> None:
        """Reload the latest edited n cogs."""
        cogs = sort_cogs(list(self.bot.extensions.keys()), folder="./cogs")[:n_cogs]
        await cogs_manager(self.bot, "reload", cogs)

        await ctx.send(f":point_down: `{'` `'.join(cogs)}` reloaded!")

    @bot_has_permissions(send_messages=True)
    @commands.command(name="reloadallcogs", aliases=["rell"])
    @commands.is_owner()
    async def reload_cogs_all(self, ctx: commands.Context) -> None:
        """Reload all cogs."""
        cogs = list(self.bot.extensions.keys())
        await cogs_manager(self.bot, "reload", cogs)	

        await ctx.send(f":muscle: All cogs reloaded: `{len(cogs)}`!")
    
    @bot_has_permissions(send_messages=True)
    @commands.command(name="reloadconfig", aliases=["rc"])
    @commands.is_owner()
    async def reload_configs(self, ctx: commands.Context, *config_files: str) -> None:
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
    @commands.command(name="reloadviews", aliases=["rv"])
    @commands.is_owner()
    async def reload_views(self, ctx: commands.Context) -> None:
        """Reload each registered views."""
        infants = reload_views()
        succes_text = f"👌 All views reloaded ! | 🔄 __`{sum(1 for _ in infants)} view(s) reloaded`__ : "
        for infant in infants: 
            succes_text += f"`{infant.replace('views.', '')}` "
        await ctx.send(succes_text)

    @bot_has_permissions(send_messages=True)
    @commands.command(name="synctree", aliases=["st"])
    @commands.is_owner()
    async def sync_tree(self, ctx: commands.Context, guild_id: Optional[str] = None) -> None:
        """Sync application commands."""
        if guild_id:
            if ctx.guild and (guild_id == "guild" or guild_id == "~"):
                guild_id = str(ctx.guild.id)
            tree = await self.bot.tree.sync(guild=discord.Object(id=guild_id))
        else:
            tree = await self.bot.tree.sync()

        self.bot.log(
            message = f"{ctx.author} synced the tree({len(tree)}): {tree}",
            name = "discord.cogs.admin.sync_tree",
        )

        await ctx.send(f":pinched_fingers: `{len(tree)}` synced!")
    
    @bot_has_permissions(send_messages=True, attach_files=True)
    @commands.command(name="botlogs", aliases=["bl"])
    @commands.is_owner()
    async def send_file_logs(self, ctx: commands.Context) -> None:
        """Upload the bot logs"""
        logs_file = join(root_directory, "discord.log")

        await ctx.send(file=discord.File(fp=logs_file, filename="bot.log"))

    @bot_has_permissions(send_messages=True)
    @commands.command(name="uptime")
    @commands.is_owner()
    async def show_uptime(self, ctx: commands.Context) -> None:
        """Show the bot uptime."""
        uptime = datetime.now() - self.bot.uptime
        await ctx.send(f":clock1: {format_dt(self.bot.uptime, 'R')} ||`{uptime}`||")

    @bot_has_permissions(send_messages=True)
    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown_bot(self, ctx: commands.Context) -> None:
        """Shutdown the bot."""
        await ctx.send(f":wave: `{self.bot.user}` is shutting down...")

        await self.bot.close()

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


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Admin(bot))