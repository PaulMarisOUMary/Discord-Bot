from typing import Protocol, runtime_checkable

from discord import (
    Guild,
    Member,
    StageChannel,
    TextChannel,
    Thread,
    VoiceChannel,
    app_commands,
)
from discord.ext import commands

from utils.bot import DiscordBot


class GuildContext(commands.Context[DiscordBot]):
    author: Member
    guild: Guild
    channel: Thread | TextChannel | VoiceChannel | StageChannel
    me: Member


CommandLike = commands.Command | app_commands.Command | commands.HybridCommand
GroupLike = commands.Group | app_commands.Group | commands.HybridGroup


@runtime_checkable
class HasHelpCustom(Protocol):
    def help_custom(self) -> tuple[str, str, str]: ...
