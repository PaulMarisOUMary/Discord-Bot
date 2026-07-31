from asyncio import to_thread
from datetime import datetime
from io import BytesIO
from re import IGNORECASE, compile
from typing import Any

from discord import Embed, File, Interaction, Member, Message, User, app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageSequence
from pilmoji import Pilmoji
from requests import get
from sqlmodel import select

from models.sql import Croissant
from utils.bot import DiscordBot
from utils.checks import require_database
from utils.database import crud
from utils.paths import dmsans_path


@app_commands.guild_only()
class Croissants(
    commands.GroupCog,
    name="croissants",
    group_name="croissants",
    group_description="Commands related to croissants.",
):
    """
    Don't leave your computer unlocked!
    A private joke to raise awareness against the risk of leaving your PC unlocked.

    Require intents:
        - message_content
    Require bot permission:
        - read_messages
        - send_messages
        - attach_files
    """

    EMOJI = '🥐'
    REGEX = compile(rf"^(J[e']? ?pa[iy]e? ?(les)? ?(crois|{EMOJI}))", IGNORECASE)

    def __init__(self, bot: DiscordBot) -> None:
        self.bot: DiscordBot = bot
        self.cooldown: dict[int, datetime] = {}
        self.subconfig: dict[str, Any] = self.bot.config.cogs.cogs[
            self.__cog_name__.lower()
        ]

        self.font_name = ImageFont.truetype(dmsans_path, 16)
        self.font_name.set_variation_by_axes([500])
        self.font_time = ImageFont.truetype(dmsans_path, 12)
        self.font_time.set_variation_by_axes([400])
        self.font_text = ImageFont.truetype(dmsans_path, 16)
        self.font_text.set_variation_by_axes([400])

    def help_custom(self) -> tuple[str, str, str]:
        label = "Croissants"
        description = "For when someone left their computer unlocked."
        return self.EMOJI, label, description

    @commands.Cog.listener("on_message")
    async def on_receive_message(self, message: Message) -> None:
        if message.author.bot or not self.REGEX.match(message.content):
            return

        if not self.__is_on_cooldown(message.author):
            self.cooldown[message.author.id] = datetime.now()
            await self.__send_croissants(message)
        else:
            await message.channel.send(
                f"{self.EMOJI} Respect the croissants don't despise them! ||No spam||"
            )

    @app_commands.command(
        name="lore", description="Explain the lore of the croissants."
    )
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
    async def croissants_lore(self, interaction: Interaction) -> None:
        embed = Embed(title="Lore of Croissants", color=0xD3A779)
        embed.add_field(
            name=f"{self.EMOJI} When",
            value="Born in October 2020. During the break time.",
        )
        embed.add_field(
            name=f"{self.EMOJI} Where", value="In computer science, at the school."
        )
        embed.add_field(
            name=f"{self.EMOJI} What",
            value="Croissants were a joke made by Franck on a student's computers.",
        )
        embed.add_field(
            name=f"{self.EMOJI} Why",
            value="Croissants are a sweet way to give awareness for students about their individual responsibility in an IT company/organisation.\nIf you leave your computer unlocked, it means someone else could use it for malicious purposes.",
        )
        embed.add_field(
            name=":arrow_right: Recap",
            value="Don't forget to **lock** your computer when you're not using it.\nSome company/school reset your computer when you leaves it unlocked, because it could leads to a security breach.",
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @require_database(True)
    @app_commands.command(
        name="show", description="Show how many croissants a user paid."
    )
    @app_commands.describe(user="The user to show the croissants of.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
    async def croissants_show(self, interaction: Interaction, user: Member) -> None:
        async with self.bot.database.session() as session:
            croissant = await session.get(Croissant, user.id)

        if croissant:
            text = f"{user.mention} have `{croissant.user_count}` croissants {self.EMOJI} !"
        else:
            text = f"Good job, {user.mention} have no croissants {self.EMOJI} ||[yet](<https://youtu.be/S2t59dPf9K0>)||."

        await interaction.response.send_message(content=text, ephemeral=True)

    @require_database(True)
    @app_commands.command(name="rank", description="Get the global croissants rank.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
    async def croissants_rank(self, interaction: Interaction) -> None:
        async with self.bot.database.session() as session:
            statement = (
                select(Croissant).order_by(Croissant.user_count.desc()).limit(10)  # type: ignore
            )
            top = (await session.exec(statement)).all()

        embed = Embed(title=f"🏆 Croissants rank {self.EMOJI}", color=0xD3A779)
        for rank, croissant in enumerate(top, start=1):
            embed.add_field(
                name=f"Top {self.__rank_emoji(rank)} `{croissant.user_count} {self.EMOJI}`",
                value=f"<@{croissant.user_id}>",
                inline=rank <= 3,
            )

        await interaction.response.send_message(embed=embed)

    async def __send_croissants(self, message: Message) -> None:
        screenshot_file = await to_thread(self.__get_screenshot, message)

        answer_message = await message.reply(
            content=f"{message.author.mention} took out the credit card! {self.EMOJI}",
            file=screenshot_file,
        )

        count = await self.__increment_croissants_counter(message.author.id)
        if count is not None:
            await answer_message.edit(
                content=f"{message.author.mention} took out the credit card ! And this is the `{count}` time, he's so generous! {self.EMOJI}"
            )

    async def __increment_croissants_counter(self, user_id: int) -> int | None:
        if self.bot.database is None:
            return None

        async with self.bot.database.session() as session:
            await crud.increment(session, Croissant, {"user_id": user_id}, "user_count")
            await session.commit()

            croissant = await session.get(Croissant, user_id)
            return croissant.user_count if croissant else None

    def __get_screenshot(self, message: Message) -> File:
        author = message.author
        content = message.content
        timestamp_str = message.created_at.strftime("%I:%M %p").lstrip("0")

        author_color_hex = str(author.color)
        if author_color_hex == "#000000":
            name_color = (242, 243, 245)
        else:
            name_color = tuple(
                int(author_color_hex[i + 1 : i + 3], 16) for i in (0, 2, 4)
            )
        timestamp_color = (148, 155, 164)
        content_color = (219, 222, 225)
        bg_color = (49, 51, 56)
        pfp_size = (40, 40)

        pfp_content = Image.open(BytesIO(get(author.display_avatar.url).content))

        pfp_mask = Image.new("L", pfp_size, 0)
        ImageDraw.Draw(pfp_mask).ellipse((0, 0) + pfp_size, fill=255)

        images_sequence: list[Image.Image] = []
        duration_array: list[int] = []

        for frame in ImageSequence.Iterator(pfp_content):
            duration_array.append(frame.info.get("duration", 0) or 0)

            img = Image.new("RGBA", size=(600, 80), color=bg_color)

            pfp = frame.convert("RGBA").resize(pfp_size)
            pfp.putalpha(pfp_mask)
            img.paste(pfp, (16, 16), pfp)

            draw = ImageDraw.Draw(img)

            time_width = draw.textlength(timestamp_str, font=self.font_time)

            name_gap = 8
            right_margin = 16
            max_name_width = 600 - 72 - right_margin - name_gap - time_width

            display_name = author.display_name
            if draw.textlength(display_name, font=self.font_name) > max_name_width:
                while (
                    display_name
                    and draw.textlength(display_name + "...", font=self.font_name)
                    > max_name_width
                ):
                    display_name = display_name[:-1]
                display_name += "..."

            draw.text((72, 14), display_name, fill=name_color, font=self.font_name)

            name_width = draw.textlength(display_name, font=self.font_name)
            draw.text(
                (72 + name_width + name_gap, 18),
                timestamp_str,
                fill=timestamp_color,
                font=self.font_time,
            )

            with Pilmoji(img) as pilmoji:
                pilmoji.text(
                    (72, 38),
                    content,
                    fill=content_color,
                    font=self.font_text,
                    spacing=5,
                )

            images_sequence.append(img.convert("P", palette=Image.Palette.ADAPTIVE))

        with BytesIO() as img_bin:
            images_sequence[0].save(
                img_bin,
                save_all=True,
                append_images=images_sequence[1:],
                optimize=False,
                format="GIF",
                loop=0,
                duration=duration_array,
            )
            img_bin.seek(0)
            file = File(img_bin, "croissants.gif")

        return file

    def __is_on_cooldown(self, user: User | Member) -> bool:
        return (
            user.id in self.cooldown
            and datetime.now().timestamp() - self.cooldown[user.id].timestamp()
            < self.subconfig["cooldown"]
        )

    def __rank_emoji(self, rank: int) -> str:
        return {1: '🥇', 2: '🥈', 3: '🥉'}.get(rank, str(rank))


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Croissants(bot))
