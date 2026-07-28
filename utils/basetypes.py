from discord import Guild, Member, Thread, app_commands
from discord.abc import GuildChannel
from discord.ext import commands


class GuildContext(commands.Context):
    author: Member
    guild: Guild
    channel: GuildChannel | Thread
    me: Member

CommandLike = commands.Command | app_commands.Command | commands.HybridCommand
GroupLike = commands.Group | app_commands.Group | commands.HybridGroup