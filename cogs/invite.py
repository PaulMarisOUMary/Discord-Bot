import discord

from copy import copy
from datetime import datetime
from discord.ext import commands, tasks
from pytz import UTC
from typing import Optional

from classes.discordbot import DiscordBot

class Invite(commands.Cog, name="invite"):
    """
        Invite tracker.
    
        Require intents: 
            - invites
        
        Require bot permission:
            - manage_channels
            - manage_guild
            - view_channel
    """
    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

        self.subconfig_data: dict = self.bot.config["cogs"][self.__cog_name__.lower()]

        self.invites: dict[int, dict[str, discord.Invite]] = dict()

    def help_custom(self) -> tuple[str, str, str]:
        emoji = '📨'
        label = "Invite Tracker"
        description = "Log each invite in the system channel."
        return emoji, label, description

    async def __seek_invite(self, before: dict[str, discord.Invite], after: dict[str, discord.Invite]) -> Optional[discord.Invite]:
        # Seek increment uses in invites
        for id, invite in after.items():
            if invite.uses > before[id].uses:
                return invite

        # Seek missing invite (only expirable)
        before_after = set(before.items()) - set(after.items())
        for id, invite in before_after:
            if expire := invite.expires_at:
                if expire > UTC.localize(datetime.now()):
                    invite.uses = invite.max_uses
                    return invite

        # Mystery
        return None

    async def __update_invites(self, *guilds: Optional[discord.Guild]) -> None:
        if not guilds:
            guilds = self.bot.guilds

        try:
            for guild in guilds:
                if guild.id not in self.invites:
                    self.invites[guild.id] = dict()
                self.invites[guild.id] = {invite.id: invite for invite in await guild.invites()}
        except discord.Forbidden or discord.HTTPException:
            pass

    async def cog_load(self):
        self.init_invites.start()

    @tasks.loop(count=1)
    async def init_invites(self) -> None:
        """This task is run ONLY ONCE at cog load."""
        await self.bot.wait_until_ready()
        await self.__update_invites()

    @commands.Cog.listener("on_invite_create")
    async def on_invite_create(self, invite: discord.Invite) -> None:
        """Trigger when an invite is created."""
        await self.__update_invites(invite.guild)

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: discord.Member) -> None:
        if member.bot:
            return

        try:
            before = copy(self.invites[member.guild.id])
            await self.__update_invites(member.guild)
            after = self.invites[member.guild.id]

            invite = await self.__seek_invite(before, after)
            if not invite:
                return

            log_message = self.subconfig_data["default_message"].format(
                invite = invite, 
                member = member, 
                created_at_timestamp = round(invite.created_at.timestamp()), 
                expires_at_timestamp = round(invite.expires_at.timestamp()) if invite.expires_at else 33197904000,
                max_uses = '♾️' if invite.max_uses == 0 else invite.max_uses
            )

            embed = discord.Embed(title=f"{self.help_custom()[0]} Invite Tracker", color=0xDC143C, description=log_message)
            embed.timestamp = datetime.now()
            
            system_channel = member.guild.system_channel
            if not system_channel:
                return

            await system_channel.send(embed=embed)
        except KeyError: # Guild not in invites -> Missing manage_guild permission
            pass
        except discord.Forbidden or discord.HTTPException: # Missing manage_channels permission
            pass
        except ValueError: # Invalid formating
            pass



async def setup(bot: DiscordBot):
    await bot.add_cog(Invite(bot))