from math import log
from typing import Any

from discord import (
    Embed,
    Forbidden,
    Message,
    NotFound,
    RawMessageDeleteEvent,
    RawReactionActionEvent,
    Reaction,
    StickerFormatType,
    TextChannel,
    utils,
)
from discord.ext import commands

from models.sql import Starboard as StarboardModel
from utils.bot import DiscordBot
from utils.database import crud


@commands.guild_only()
class Starboard(commands.Cog, name="starboard"):
    """
    Starboard.

    Require intents:
            - Intents.messages
            - Intents.reactions

    Require bot permission:
            - send_messages
            - view_channel
    """

    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot
        self.subconfig: dict[str, Any] = self.bot.config.cogs.cogs[
            self.__cog_name__.lower()
        ]

        self.star_emoji = '⭐'
        self.stars_emojis = ['⭐', '🌟', '✨', '💫', '☄️', '🎇', '🎆', '🌠', '💖', '🪄']

    def help_custom(self) -> tuple[str, str, str]:
        return self.star_emoji, "Starboard", "Allows users to star messages."

    def __star_emoji_upgrade(self, stars: int) -> str | None:
        if stars != 0:
            index = round(log(stars))
            return self.stars_emojis[index]
        return None

    def __star_gradient_colour(self, stars: int) -> int:
        p = min(stars / 13, 1.0)

        red = 255
        green = int((194 * p) + (253 * (1 - p)))
        blue = int((12 * p) + (247 * (1 - p)))
        return (red << 16) + (green << 8) + blue

    def __get_starboard_embeds(self, message: Message, n_star: int) -> list[Embed]:
        embed = Embed(
            description=message.content,
            color=self.__star_gradient_colour(n_star),
            timestamp=message.created_at,
            url="https://youtu.be/L_jWHffIx5E?t=36",
        )
        embeds = [embed]
        embed.set_author(
            name=message.author.name, icon_url=message.author.display_avatar.url
        )
        embed.add_field(name="Original", value=f"[Jump !]({message.jump_url})")

        reference = message.reference
        if reference and isinstance(reference.resolved, Message):
            embed.add_field(
                name="Replying to...",
                value=f"[{reference.resolved.author}]({reference.resolved.jump_url})",
                inline=False,
            )

        if message.attachments:
            images = [
                attachment.url
                for attachment in message.attachments
                if attachment.url.lower().endswith(
                    ("jpg", "jpeg", "png", "webp", "gif")
                )
            ]
            for image_url in images:
                if not embed.image.url:
                    embed.set_image(url=image_url)
                else:
                    embeds.append(
                        Embed(url="https://youtu.be/L_jWHffIx5E?t=36").set_image(
                            url=image_url
                        )
                    )

        if message.stickers:
            png_stickers = [
                sticker
                for sticker in message.stickers
                if sticker.format in (StickerFormatType.png, StickerFormatType.apng)
            ]
            for image_sticker in png_stickers:
                if not embed.image.url:
                    embed.set_image(url=image_sticker.url)
                else:
                    embeds.append(
                        Embed(url="https://youtu.be/L_jWHffIx5E?t=36").set_image(
                            url=image_sticker.url
                        )
                    )

        return embeds

    async def __get_starboard_row(
        self, reference_message_id: int
    ) -> StarboardModel | None:
        if self.bot.database is None:
            return None

        async with self.bot.database.session() as session:
            return await session.get(StarboardModel, reference_message_id)

    async def __get_display_message(self, reference_message_id: int) -> Message | None:
        row = await self.__get_starboard_row(reference_message_id)
        if not row:
            return None

        guild = self.bot.get_guild(row.reference_guild_id)
        display_channel = guild.get_channel(row.display_channel_id) if guild else None

        if not isinstance(display_channel, TextChannel):
            if self.bot.database is not None:
                async with self.bot.database.session() as session:
                    stale_row = await session.get(StarboardModel, reference_message_id)
                    if stale_row:
                        await session.delete(stale_row)
                        await session.commit()
            return None

        try:
            return await display_channel.fetch_message(row.display_message_id)
        except NotFound:
            return None

    async def __get_message_from_payload(
        self, payload: RawReactionActionEvent
    ) -> tuple[Message | None, Reaction | None]:
        cached_message = utils.get(self.bot.cached_messages, id=payload.message_id)

        if cached_message:
            message = cached_message
        else:
            channel = self.bot.get_channel(payload.channel_id)
            if not isinstance(channel, TextChannel):
                return None, None
            message = await channel.fetch_message(payload.message_id)

        reaction = utils.get(message.reactions, emoji=self.star_emoji)
        return message, reaction

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent) -> None:
        if self.bot.database is None:
            return

        try:
            if str(payload.emoji) != self.star_emoji:
                return

            message, reaction = await self.__get_message_from_payload(payload)

            if (
                not reaction or not message or not message.guild
            ):  # not a self.star_emoji
                return

            starboard_channel = utils.find(
                lambda c: "starboard" in c.name, message.guild.text_channels
            )

            if not starboard_channel or starboard_channel.id == payload.channel_id:
                return

            if not isinstance(message.channel, TextChannel):
                return

            n_star = reaction.count
            star_emoji = self.__star_emoji_upgrade(n_star)

            if n_star == 1:
                embeds = self.__get_starboard_embeds(message, n_star)
                display_message = await starboard_channel.send(
                    content=f"{star_emoji} **{n_star}** {message.channel.mention} ID: {message.id}",
                    embeds=embeds,
                )

                async with self.bot.database.session() as session:
                    await crud.upsert(
                        session,
                        StarboardModel(
                            reference_message_id=message.id,
                            reference_guild_id=message.guild.id,
                            reference_channel_id=message.channel.id,
                            display_channel_id=starboard_channel.id,
                            display_message_id=display_message.id,
                            star_count=n_star,
                        ),
                    )
                    await session.commit()
            else:
                display_message = await self.__get_display_message(message.id)
                if not display_message:
                    return

                await display_message.edit(
                    content=f"{star_emoji} **{n_star}** {message.channel.mention} ID: {message.id}",
                    embeds=display_message.embeds,
                )

                async with self.bot.database.session() as session:
                    row = await session.get(StarboardModel, message.id)
                    if row:
                        row.star_count = n_star
                        session.add(row)
                        await session.commit()
        except (Forbidden, NotFound):
            pass

    @commands.Cog.listener("on_raw_reaction_remove")
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent) -> None:
        if self.bot.database is None:
            return

        try:
            message, reaction = await self.__get_message_from_payload(payload)

            if not message or not isinstance(message.channel, TextChannel):
                return

            n_star = reaction.count if reaction else 0
            star_emoji = self.__star_emoji_upgrade(n_star)

            display_message = await self.__get_display_message(message.id)
            if not display_message:
                return

            async with self.bot.database.session() as session:
                row = await session.get(StarboardModel, message.id)

                if not reaction:
                    if row:
                        await session.delete(row)
                        await session.commit()
                    await display_message.delete()
                else:
                    await display_message.edit(
                        content=f"{star_emoji} **{n_star}** {message.channel.mention} ID: {message.id}",
                        embeds=display_message.embeds,
                    )

                    if row:
                        row.star_count = n_star
                        session.add(row)
                        await session.commit()
        except (Forbidden, NotFound):
            pass

    @commands.Cog.listener("on_raw_message_delete")
    async def on_raw_message_delete(self, payload: RawMessageDeleteEvent) -> None:
        if self.bot.database is None:
            return

        try:
            row = await self.__get_starboard_row(payload.message_id)
            if not row:
                return

            display_message = await self.__get_display_message(payload.message_id)

            async with self.bot.database.session() as session:
                stale_row = await session.get(StarboardModel, payload.message_id)
                if stale_row:
                    await session.delete(stale_row)
                    await session.commit()

            if display_message:
                await display_message.delete()
        except (Forbidden, NotFound):
            pass


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Starboard(bot))
