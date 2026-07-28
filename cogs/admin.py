from datetime import datetime, timedelta, timezone
from logging import getLogger

from discord import Object
from discord.ext import commands
from discord.utils import format_dt

from utils.bot import DiscordBot
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

    @commands.command("load")
    @commands.is_owner()
    async def load_cog(self, ctx: commands.Context, cog: str) -> None:
        await cogs_manager(self.bot, "load", cog)
        await ctx.send(f":point_right: Cog `{cog}` loaded!")

    @commands.command("unload")
    @commands.is_owner()
    async def unload_cog(self, ctx: commands.Context, cog: str) -> None:
        await cogs_manager(self.bot, "unload", cog)
        await ctx.send(f":point_left: Cog `{cog}` unloaded!")

    @commands.command("reload")
    @commands.is_owner()
    async def reload_cogs(self, ctx: commands.Context, *cogs: str) -> None:
        reload_cogs = {f"cogs.{cog}" for cog in cogs}
        await cogs_manager(self.bot, "reload", *reload_cogs)
        await ctx.send(f":thumbsup: `{'` `'.join(cogs)}` reloaded!")

    @commands.command("reloadlatest", aliases=["rl"])
    @commands.is_owner()
    async def reload_latest_cogs(self, ctx: commands.Context, n_cogs: int = 1) -> None:
        reload_cogs = sort_cogs(list(self.bot.extensions.keys()), True)[:n_cogs]
        await cogs_manager(self.bot, "reload", *reload_cogs)
        await ctx.send(f":point_down: `{'` `'.join(reload_cogs)}` reloaded!")

    @commands.command("reloadall", aliases=["rll"])
    @commands.is_owner()
    async def reload_all_cogs(self, ctx: commands.Context) -> None:
        reload_cogs = set(self.bot.extensions.keys())
        await cogs_manager(self.bot, "reload", *reload_cogs)
        await ctx.send(f":muscle: All cogs reloaded: `{len(reload_cogs)}`!")

    @commands.command("reloadconfig", aliases=["rc"])
    @commands.is_owner()
    async def reload_configs(self, ctx: commands.Context) -> None:
        self.config = load_config(config_dir, env_path)
        await ctx.send(":handshake: Config files reloaded!")

    @commands.command(name="synctree", aliases=["st"])
    @commands.is_owner()
    async def sync_tree(
        self, ctx: commands.Context, guild_id: str | None = None
    ) -> None:
        if guild_id:
            if ctx.guild and (guild_id == "guild" or guild_id == "~"):
                guild_id = str(ctx.guild.id)
            tree = await self.bot.tree.sync(guild=Object(id=guild_id))
        else:
            tree = await self.bot.tree.sync()

        _log.info(f"{ctx.author} synced the tree({len(tree)}): {tree}")

        await ctx.send(f":pinched_fingers: `{len(tree)}` synced!")

    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown_bot(self, ctx: commands.Context) -> None:
        await ctx.send(f":wave: `{self.bot.user}` is shutting down...")
        await self.bot.close()

    @commands.command("uptime")
    async def uptime(self, ctx: commands.Context) -> None:
        start_time = datetime.now(timezone.utc) - timedelta(seconds=self.bot.uptime)
        await ctx.send(f":clock1: {format_dt(start_time, 'R')} ||`{start_time}`||")


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Admin(bot))
