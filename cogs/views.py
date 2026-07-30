from discord import Interaction
from discord.ext import commands

from utils.basetypes import GuildContext
from utils.bot import DiscordBot
from utils.checks import bot_has_permissions
from views import dropdown


class Views(commands.Cog, name="views"):
    """Experimental cog, new features such buttons, dropdown or whispering."""

    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

    def help_custom(self) -> tuple[str, str, str]:
        return '🔘', "Views", "Demo : New discord features."

    @bot_has_permissions(send_messages=True)
    @commands.command(name="dropdown")
    @commands.guild_only()
    async def drop(self, ctx: GuildContext) -> None:
        """Discover select menu feature with this command."""

        async def when_callback(_class, interaction: Interaction) -> None:
            if _class.view.invoke.author == interaction.user:
                message = "Selected languages : "
                for value in _class.values:
                    message += f"`{value}` "
                await interaction.response.defer()
                await interaction.delete_original_response()
                await _class.view.invoke.reply(message)
            else:
                await interaction.response.send_message(
                    "❌ Hey it's not your session !", ephemeral=True
                )

        options = [
            {"label": "Mandarin", "description": "你好", "emoji": "🇨🇳"},
            {"label": "Spanish", "description": "Buenos dias", "emoji": "🇪🇸"},
            {"label": "English", "description": "Hello", "emoji": "🇬🇧"},
            {"label": "Hindi", "description": "नमस्ते", "emoji": "🇮🇳"},
            {"label": "Arabic", "description": "صباح الخير", "emoji": "🇸🇦"},
            {"label": "Potuguese", "description": "Olá", "emoji": "🇵🇹"},
            {"label": "Bengali", "description": "হ্যালো", "emoji": "🇧🇩"},
            {"label": "Russian", "description": "Привет", "emoji": "🇷🇺"},
            {"label": "Japanese", "description": "こんにちは", "emoji": "🇯🇵"},
            {"label": "Turkish", "description": "Merhaba", "emoji": "🇹🇷"},
            {"label": "Korean", "description": "안녕하십니까", "emoji": "🇰🇷"},
            {"label": "French", "description": "Bonjour", "emoji": "🇫🇷"},
            {"label": "German", "description": "Hallo", "emoji": "🇩🇪"},
            {"label": "Vietnamese", "description": "xin chào", "emoji": "🇻🇳"},
            {"label": "Italian", "description": "Buongiorno", "emoji": "🇮🇹"},
            {"label": "Polish", "description": "dzień dobry", "emoji": "🇵🇱"},
            {"label": "Romanian", "description": "Buna ziua", "emoji": "🇷🇴"},
            {"label": "Dutch", "description": "Hallo", "emoji": "🇳🇱"},
            {"label": "Thai", "description": "สวัสดี", "emoji": "🇹🇭"},
            {"label": "Nepali", "description": "नमस्कार", "emoji": "🇳🇵"},
            {"label": "Greek", "description": "γεια σας", "emoji": "🇬🇷"},
            {"label": "Czech", "description": "Ahoj", "emoji": "🇨🇿"},
            {"label": "Persian", "description": "سلام", "emoji": "🇮🇷"},
        ]

        view = dropdown.View(
            invoke=ctx,
            placeholder="Select your language(s)",
            min_val=1,
            max_val=9,
            options=options,
            when_callback=when_callback,
        )
        await ctx.send("Dropdown demo right there !", view=view)


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Views(bot))
