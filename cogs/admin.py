from datetime import datetime, timedelta, timezone
from logging import getLogger

from discord import Object
from discord.ext import commands
from discord.utils import format_dt
from sqlmodel import col, update

from models.sql import Prefix
from utils.basetypes import GuildContext
from utils.bot import DiscordBot
from utils.checks import bot_has_permissions, require_database
from utils.cogs import cogs_manager, sort_cogs
from utils.config import load_config
from utils.paths import config_dir, env_path

_log = getLogger(__name__)


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
        return '⚙️', "Admin", "Show the list of admin commands."

    @bot_has_permissions(send_messages=True)
    @commands.command("load")
    @commands.is_owner()
    async def load_cog(self, ctx: commands.Context, cog: str) -> None:
        """Load a cog: cogs.<cogname>"""
        await cogs_manager(self.bot, "load", cog)
        await ctx.send(f":point_right: Cog `{cog}` loaded!")

    @bot_has_permissions(send_messages=True)
    @commands.command("unload")
    @commands.is_owner()
    async def unload_cog(self, ctx: commands.Context, cog: str) -> None:
        """Unload a cog: cogs.<cogname>"""
        await cogs_manager(self.bot, "unload", cog)
        await ctx.send(f":point_left: Cog `{cog}` unloaded!")

    @bot_has_permissions(send_messages=True)
    @commands.command("reload")
    @commands.is_owner()
    async def reload_cogs(self, ctx: commands.Context, *cogs: str) -> None:
        """Reload cog(s): *cogs.<cogname>"""
        reload_cogs = {f"cogs.{cog}" for cog in cogs}
        await cogs_manager(self.bot, "reload", *reload_cogs)
        await ctx.send(f":thumbsup: `{'` `'.join(cogs)}` reloaded!")

    @bot_has_permissions(send_messages=True)
    @commands.command("reloadlatest", aliases=["rl"])
    @commands.is_owner()
    async def reload_latest_cogs(self, ctx: commands.Context, n_cogs: int = 1) -> None:
        """Reload latest n specified cogs."""
        reload_cogs = sort_cogs(list(self.bot.extensions.keys()), True)[:n_cogs]
        await cogs_manager(self.bot, "reload", *reload_cogs)
        await ctx.send(f":point_down: `{'` `'.join(reload_cogs)}` reloaded!")

    @bot_has_permissions(send_messages=True)
    @commands.command("reloadall", aliases=["rll"])
    @commands.is_owner()
    async def reload_all_cogs(self, ctx: commands.Context) -> None:
        """Reload all loaded cogs."""
        reload_cogs = set(self.bot.extensions.keys())
        await cogs_manager(self.bot, "reload", *reload_cogs)
        await ctx.send(f":muscle: All cogs reloaded: `{len(reload_cogs)}`!")

    @bot_has_permissions(send_messages=True)
    @commands.command("reloadconfig", aliases=["rc"])
    @commands.is_owner()
    async def reload_configs(self, ctx: commands.Context) -> None:
        """Reload each .toml and the .env."""
        self.bot.config = load_config(config_dir, env_path)
        await ctx.send(":handshake: Config files reloaded!")

    @bot_has_permissions(send_messages=True)
    @commands.command(name="synctree", aliases=["st"])
    @commands.is_owner()
    async def sync_tree(
        self, ctx: commands.Context, guild_id: str | None = None
    ) -> None:
        """Sync manually application commands."""
        if guild_id:
            if ctx.guild and (guild_id == "guild" or guild_id == "~"):
                guild_id = str(ctx.guild.id)
            tree = await self.bot.tree.sync(guild=Object(id=guild_id))
        else:
            tree = await self.bot.tree.sync()

        _log.info(f"{ctx.author} synced the tree({len(tree)}): {tree}")

        await ctx.send(f":pinched_fingers: `{len(tree)}` synced!")

    @bot_has_permissions(send_messages=True)
    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown_bot(self, ctx: commands.Context) -> None:
        """Shutdown the bot."""
        await ctx.send(f":wave: `{self.bot.user}` is shutting down...")
        await self.bot.close()

    @bot_has_permissions(send_messages=True)
    @commands.command("uptime")
    async def uptime(self, ctx: commands.Context) -> None:
        """Show the bot uptime."""
        start_time = datetime.now(timezone.utc) - timedelta(seconds=self.bot.uptime)
        await ctx.send(f":clock1: {format_dt(start_time, 'R')} ||`{start_time}`||")

    @require_database(True)
    @bot_has_permissions(send_messages=True)
    @commands.command("changeprefix", aliases=["prefix"])
    @commands.has_guild_permissions(administrator=True)
    @commands.guild_only()
    async def change_guild_prefix(self, ctx: GuildContext, prefix: str) -> None:
        """Change your guild prefix."""
        guild_id = ctx.guild.id

        async with self.bot.database.session() as session:
            statement = (
                update(Prefix)
                .where(col(Prefix.guild_id) == guild_id)
                .values(guild_prefix=prefix)
            )
            await session.exec(statement)
            await session.commit()

        self.bot.prefixes_cache[guild_id] = prefix
        await ctx.send(f":warning: Prefix changed to `{prefix}`")


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Admin(bot))
