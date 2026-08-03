from discord import Embed, Message
from discord.ext import commands

from utils.ansi import Background as bg
from utils.ansi import Foreground as fg
from utils.ansi import Format as fmt
from utils.basetypes import GuildContext
from utils.bot import DiscordBot
from utils.checks import bot_has_permissions


class Useful(commands.Cog, name="useful"):
    """
    Usefull commands for Devs & more.

    Require intents:
        - message_content

    Require bot permission:
        - send_messages
    """

    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

    def help_custom(self) -> tuple[str, str, str]:
        return '🚩', "Useful", "Useful commands."

    @bot_has_permissions(send_messages=True)
    @commands.command(name="emojilist", aliases=["ce", "el"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def getcustomemojis(self, ctx: GuildContext) -> None:
        """List all custom emojis in the guild."""
        emojis = ctx.guild.emojis
        if not emojis:
            await ctx.send("This server does not have custom emoji.")
            return

        lines = [
            f"{i}. {emoji} - :\u200b{emoji.name}: - `{emoji}`"
            for i, emoji in enumerate(emojis, start=1)
        ]

        chunk_size = 15
        chunks = [lines[i : i + chunk_size] for i in range(0, len(lines), chunk_size)]

        total_pages = len(chunks)

        for page, chunk in enumerate(chunks, start=1):
            embed = Embed(
                title=f"Custom emojis list ({len(emojis)})",
                description="\n".join(chunk),
            )
            if total_pages > 1:
                embed.set_footer(text=f"Page {page}/{total_pages}")

            await ctx.send(embed=embed)

    @bot_has_permissions(send_messages=True)
    @commands.command(name="colors")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def codeblock_colors(self, ctx: commands.Context) -> None:
        """List all different ANSI colors."""
        codeblock = "```ansi\n"

        for item, text in [
            (fmt.__members__, "Format"),
            (fg.__members__, "Foreground"),
            (bg.__members__, "Background"),
        ]:
            codeblock += f"{fmt.UNDERLINE + fg.BLUE + bg.WHITE}{text}{fmt.RESET}:\n"
            for key, value in item.items():
                codeblock += f"ESC[{value.value}m {value}{key}{fmt.RESET}\n"

        await ctx.send(f"{codeblock}```")

    @bot_has_permissions(send_messages=True)
    @commands.command(name="cleanup")
    @commands.guild_only()
    async def cleanup(self, ctx: GuildContext, n_message: int) -> None:
        """Cleanup your n bot's commands invocation."""
        if n_message < 1 or n_message > 150:
            raise ValueError("Invalid number of messages to delete.")

        prefix = self.bot.get_guild_prefix(ctx.guild.id)

        def check(message: Message) -> bool:
            return (
                message.author == ctx.me or message.content.startswith(prefix)
            ) and not (message.mentions or message.role_mentions)

        deleted = await ctx.channel.purge(
            limit=n_message, check=check, before=ctx.message
        )

        await ctx.message.reply(
            content=f"🗑️ Deleted {len(deleted)} messages.",
            delete_after=5,
            mention_author=False,
        )


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Useful(bot))
