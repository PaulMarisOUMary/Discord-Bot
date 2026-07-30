import time

from discord import Color, Embed
from discord.ext import commands

from utils.bot import DiscordBot
from utils.checks import bot_has_permissions


class Basic(commands.Cog, name="basic"):
    """
    Basic commands, like ping.

    Require intents:
        - None

    Require bot permission:
        - send_messages
    """

    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

    def help_custom(self) -> tuple[str, str, str]:
        return '📙', "Basic", "Basic commands, like ping."

    @bot_has_permissions(send_messages=True)
    @commands.hybrid_command(name="ping", description="Ping the bot.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, ctx: commands.Context) -> None:
        """Show Bot & WebSocket latency."""
        ws_latency = round(self.bot.latency * 1000)

        text = ":ping_pong: Pong !"

        start_time = time.perf_counter()
        message = await ctx.send(text)
        end_time = time.perf_counter()

        api_latency = round((end_time - start_time) * 1000)

        embed = Embed(title=text, color=Color.green())
        embed.add_field(name="WebSocket", value=f"`{ws_latency} ms`", inline=True)
        embed.add_field(name="API Round-Trip", value=f"`{api_latency} ms`", inline=True)

        await message.edit(content=None, embed=embed)


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Basic(bot))
