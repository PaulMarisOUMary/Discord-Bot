from datetime import datetime
from logging import getLogger
from random import choice
from typing import Any

from discord import ChannelType, Colour, Embed, Member, User, app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks
from discord.utils import format_dt
from sqlalchemy import extract
from sqlmodel import select

from models.sql import Birthday as BirthdayModel
from utils.basetypes import GuildInteraction
from utils.bot import DiscordBot
from utils.checks import bot_has_permissions, require_database
from utils.database import crud

_log = getLogger(__name__)


@app_commands.guild_only()
class Birthday(
    commands.GroupCog,
    name="birthday",
    group_name="birthday",
    group_description="Commands related to birthday.",
):
    """
    Set your birthday, and when the time comes I will wish you a happy birthday !

    Require intents:
        - default

    Require bot permission:
        - view_channel
    """

    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot
        self.subconfig: dict[str, Any] = self.bot.config.cogs.cogs[
            self.__cog_name__.lower()
        ]

        self.birthday_images: list[str] = self.subconfig.get("images", [])
        self.birthday_post_hour: int = int(self.subconfig.get("post_hour", 9))

    def help_custom(self) -> tuple[str, str, str]:
        return '🎁', "Birthday", "Maybe I'll wish you soon a happy birthday !"

    async def cog_load(self) -> None:
        self.daily_birthday.start()

    async def cog_unload(self) -> None:
        self.daily_birthday.cancel()

    @tasks.loop(hours=1)
    async def daily_birthday(self) -> None:
        if datetime.now().hour != self.birthday_post_hour:
            return

        await self.trigger_global_birthday()

    @daily_birthday.before_loop
    async def before_daily_birthday(self) -> None:
        await self.bot.wait_until_ready()

    async def trigger_global_birthday(self, specify_guild: int | None = None) -> None:
        if self.bot.database is None:
            return

        async with self.bot.database.session() as session:
            statement = select(BirthdayModel).where(
                extract("day", BirthdayModel.user_birth) == datetime.now().day,  # ty: ignore[invalid-argument-type]
                extract("month", BirthdayModel.user_birth) == datetime.now().month,  # ty: ignore[invalid-argument-type]
            )
            todays_birthdays = (await session.exec(statement)).all()

        if not todays_birthdays:
            _log.info("No birthday today")
            return

        response_guilds = {row.guild_id for row in todays_birthdays}

        for guild in self.bot.guilds:
            if guild.id not in response_guilds:
                continue
            if specify_guild and guild.id != specify_guild:
                continue

            for channel in guild.text_channels:
                if channel.type == ChannelType.forum:
                    continue
                if (
                    not channel.permissions_for(guild.me).send_messages
                    or not channel.permissions_for(guild.me).embed_links
                ):
                    continue
                if "birthday" not in channel.name:
                    continue

                mentions = " & ".join(
                    f"<@{row.user_id}>"
                    for row in todays_birthdays
                    if row.guild_id == guild.id
                )
                embed = Embed(
                    title="🎉 Happy birthday !",
                    description=f"Today is the birthday of {mentions} !",
                    colour=Colour.dark_gold(),
                )
                embed.set_image(url=choice(self.birthday_images))

                await channel.send(embed=embed)

    @require_database(True)
    @app_commands.guild_only()
    @app_commands.command(name="set", description="Set your own birthday.")  # type: ignore
    @app_commands.describe(
        month="Your month of birth.",
        day="Your day of birth.",
        year="Your year of birth.",
    )
    @app_commands.choices(
        month=[
            Choice(name=datetime(1, i, 1).strftime("%B"), value=i) for i in range(1, 13)
        ]
    )
    @app_commands.checks.cooldown(1, 15.0, key=lambda i: (i.guild_id, i.user.id))
    async def set_birthday(
        self,
        interaction: GuildInteraction,
        month: int,
        day: app_commands.Range[int, 1, 31],
        year: app_commands.Range[
            int, datetime.now().year - 99, datetime.now().year - 15
        ],
    ) -> None:
        """Allows you to set/show your birthday."""
        try:
            birth_date = datetime.strptime(f"{day}{month}{year}", "%d%m%Y").date()
        except ValueError:
            raise commands.CommandError("Please provide a real date of birth.")

        async with self.bot.database.session() as session:
            await crud.upsert(
                session,
                BirthdayModel(
                    guild_id=interaction.guild.id,
                    user_id=interaction.user.id,
                    user_birth=birth_date,
                ),
            )
            await session.commit()

        await self.show_birthday_message(interaction, interaction.user)

    @app_commands.guild_only()
    @app_commands.command(name="show", description="Display the birthday of a user.")  # type: ignore
    @app_commands.describe(user="The user to get the birthdate from.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
    async def show_birthday(
        self,
        interaction: GuildInteraction,
        user: Member | User | None = None,
    ) -> None:
        """Allows you to show the birthday of other users."""
        await self.show_birthday_message(interaction, user or interaction.user)

    async def show_birthday_message(
        self, interaction: GuildInteraction, user: Member | User
    ) -> None:
        if self.bot.database is None:
            await interaction.response.send_message(
                ":birthday: The database isn't available, birthdays are disabled."
            )
            return

        async with self.bot.database.session() as session:
            birthday = await session.get(BirthdayModel, (interaction.guild.id, user.id))

        if birthday:
            birthdate = datetime.combine(birthday.user_birth, datetime.min.time())
            await interaction.response.send_message(
                f":birthday: Birthday the {format_dt(birthdate, 'D')} and was born {format_dt(birthdate, 'R')}."
            )
        else:
            await interaction.response.send_message(
                ":birthday: Nothing was found. Set the birthday and retry."
            )

    @bot_has_permissions(view_channel=True)
    @commands.command(name="triggerbirthday")
    @commands.is_owner()
    @commands.guild_only()
    async def trigger_birthday(
        self, ctx: commands.Context, guild_id: int | None = None
    ) -> None:
        """Trigger manually the birthday."""
        if guild_id and guild_id not in [guild.id for guild in self.bot.guilds]:
            await ctx.send(f"Invalid Guild id `{guild_id}`.")
            return

        await self.trigger_global_birthday(guild_id)
        await ctx.send(
            f"Manually trigger birthday for `{guild_id if guild_id else 'all guilds'}`."
        )


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Birthday(bot))
