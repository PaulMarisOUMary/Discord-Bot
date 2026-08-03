from contextlib import suppress
from time import monotonic
from typing import Any

from discord import (
    HTTPException,
    Member,
    StageChannel,
    VoiceChannel,
    VoiceState,
    app_commands,
)
from discord.ext import commands

from utils.basetypes import GuildContext
from utils.bot import DiscordBot
from utils.checks import bot_has_permissions


class PrivateVocal(commands.Cog, name="privatevocal"):
    """
    Create and manage private vocal channels.

    Require intents:
            - voice_states

    Require bot permission:
            - manage_channels
            - manage_permissions
            - move_members
    """

    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

        self.subconfig: dict[str, Any] = self.bot.config.cogs.cogs[
            self.__cog_name__.lower()
        ]

        self.tracker: dict[int, dict[str, dict[int, Any]]] = {}
        self.MAIN_CHANNEL_NAME = self.subconfig["main_channel_name"]
        self.CHANNEL_NAME = self.subconfig["channel_name"]
        self.COOLDOWN_TIME = self.subconfig["cooldown"]

    def help_custom(self) -> tuple[str, str, str]:
        return '💭', "Private Vocal", "Create a private vocal channel."

    def _get_guild_data(self, guild_id: int) -> dict[str, dict[int, Any]]:
        if guild_id not in self.tracker:
            self.tracker[guild_id] = {"cooldown": {}, "channels": {}}
        return self.tracker[guild_id]

    def _is_private_vocal(
        self, channel_id: int, guild_channels: dict[int, int]
    ) -> bool:
        return channel_id in guild_channels

    def _is_join_channel(self, channel: VoiceChannel | StageChannel) -> bool:
        return channel.user_limit == 1 and channel.name == self.MAIN_CHANNEL_NAME

    def _get_remaining_cooldown(
        self, user_id: int, guild_cooldown: dict[int, float]
    ) -> float:
        if user_id not in guild_cooldown:
            return 0
        remaining = self.COOLDOWN_TIME - (monotonic() - guild_cooldown[user_id])
        return max(0, remaining)

    @commands.Cog.listener("on_voice_state_update")
    async def on_voice_state_update(
        self, member: Member, before: VoiceState, after: VoiceState
    ) -> None:
        guild_data = self._get_guild_data(member.guild.id)
        guild_cooldown = guild_data["cooldown"]
        guild_channels = guild_data["channels"]

        if after.channel is not None and self._is_join_channel(after.channel):
            remaining = self._get_remaining_cooldown(member.id, guild_cooldown)

            if remaining > 0:
                with suppress(HTTPException):
                    await member.move_to(None)
                    await member.send(
                        f"Sorry you're on cooldown, time remaining: `{round(remaining)}` seconds."
                    )
            else:
                try:
                    private_vocal = await member.guild.create_voice_channel(
                        self.CHANNEL_NAME.format(user=member),
                        category=after.channel.category,
                    )
                    await member.move_to(private_vocal)
                    guild_cooldown[member.id] = monotonic()
                    guild_channels[private_vocal.id] = member.id
                except HTTPException:
                    pass

        if before.channel is not None and before.channel.id in guild_channels:
            if members := before.channel.members:
                new_owner = members[0]
                guild_channels[before.channel.id] = new_owner.id
                with suppress(HTTPException):
                    await before.channel.edit(
                        name=self.CHANNEL_NAME.format(user=new_owner)
                    )
            else:
                del guild_channels[before.channel.id]
                with suppress(HTTPException):
                    await before.channel.delete()

    @bot_has_permissions(send_messages=True)
    @commands.hybrid_command(  # type: ignore
        name="userlimit",
        description="Limit the number of user(s) in your private channel.",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    @app_commands.describe(limit="The number of max user(s) in your private channel.")
    @app_commands.guild_only()
    async def lock_private_vocal(
        self, ctx: GuildContext, limit: app_commands.Range[int, 1, 99] | None = None
    ) -> None:
        """Limit the number of user(s) in your private channel."""
        voice = ctx.author.voice
        if not voice or not voice.channel:
            await ctx.send("You're not in a voice channel.", ephemeral=True)
            return

        channel = voice.channel
        guild_channels = self._get_guild_data(ctx.guild.id)["channels"]

        if channel and not self._is_private_vocal(channel.id, guild_channels):
            await ctx.send("You're not in a private vocal channel.", ephemeral=True)
            return

        target_limit = limit if limit is not None else len(channel.members)

        await voice.channel.edit(user_limit=target_limit)
        await ctx.send(f"Vocal user-limit set to `{target_limit}`.", ephemeral=True)


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(PrivateVocal(bot))
