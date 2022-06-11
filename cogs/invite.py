import discord

from copy import copy
from datetime import datetime
from discord.ext import commands, tasks
from discord.utils import get
from pytz import UTC
from typing import Optional
from classes.database import MixedTypes

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
        self.granted_guilds: dict[int, tuple[discord.TextChannel, str]] = dict()

    def help_custom(self) -> tuple[str, str, str]:
        emoji = '📨'
        label = "Invite Tracker"
        description = "Log each invite in the system channel."
        return emoji, label, description

    def __is_guild_granted(self, guild: discord.Guild) -> bool:
        return guild.id in self.granted_guilds

    async def __update_granted_guilds(self) -> None:
        granted_guilds: tuple[tuple[int, int, str]] = await self.bot.database.select(self.subconfig_data["table"], "*")
        for guild, channel, custom_message in granted_guilds:
            channel_object = get(self.bot.guilds, id=guild).get_channel(channel)
            self.granted_guilds[guild] = (channel_object, custom_message)

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

        await self.__update_granted_guilds()
        await self.__update_invites()

    @commands.Cog.listener("on_invite_create")
    async def on_invite_create(self, invite: discord.Invite) -> None:
        """Trigger when an invite is created."""
        if not self.__is_guild_granted(invite.guild):
            return

        await self.__update_invites(invite.guild)

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: discord.Member) -> None:
        if not self.__is_guild_granted(member.guild):
            return

        if member.bot:
            return

        try:
            before = copy(self.invites[member.guild.id])
            await self.__update_invites(member.guild)
            after = self.invites[member.guild.id]

            invite = await self.__seek_invite(before, after)
            if not invite:
                return

            format_log_message = self.granted_guilds[member.guild.id][1] if self.granted_guilds[member.guild.id][1] else self.subconfig_data["default_message"]

            log_message = format_log_message.format(
                invite = invite, 
                member = member, 
                created_at_timestamp = round(invite.created_at.timestamp()), 
                expires_at_timestamp = round(invite.expires_at.timestamp()) if invite.expires_at else 33197904000,
                max_uses = '♾️' if invite.max_uses == 0 else invite.max_uses
            )

            embed = discord.Embed(title=f"{self.help_custom()[0]} Invite Tracker", color=0xDC143C, description=log_message)
            embed.timestamp = datetime.now()

            channel = self.granted_guilds[member.guild.id][0]
            if not channel:
                channel = member.guild.system_channel
                if not channel:
                    return

            await channel.send(embed=embed)
        except KeyError: # Guild not in invites -> Missing manage_guild permission
            pass
        except discord.Forbidden or discord.HTTPException: # Missing manage_channels permission
            pass
        except ValueError: # Invalid formating
            pass

    @commands.command(name="logs")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_channels=True, manage_guild=True, view_channel=True)
    @commands.cooldown(1, 25, commands.BucketType.guild)
    async def config_invite_logs(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        """Set the invite tracker channel."""
        await self.bot.database.insert_onduplicate(self.subconfig_data["table"], {"guild_id": ctx.guild.id, "channel_id": channel.id})

        await ctx.send(f"Logs channel set to {channel.mention}.")

        await self.__update_granted_guilds()
        await self.__update_invites(ctx.guild)

    @commands.command(name="logscustom")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_channels=True, manage_guild=True, view_channel=True)
    @commands.cooldown(1, 25, commands.BucketType.guild)
    async def config_invite_logs_custom_message(self, ctx: commands.Context, *, message: str = None) -> None:
        """Set a custom message for the invite tracker.
        
        Formating variables: 
        {invite} - The invite object.
        {member} - The member that joined.
        {created_at_timestamp} - The timestamp of the invite creation (int).
        {expires_at_timestamp} - The timestamp of the invite expiration (int).
        {max_uses} - The max uses of the invite."""
        if not self.__is_guild_granted(ctx.guild):
            return
        if not message:
            await self.bot.database.update(self.subconfig_data["table"], {"custom_message": MixedTypes("NULL")}, f"guild_id = {ctx.guild.id}")
            await ctx.send(f"Logs message set to default.")
            return
        elif lenght_message := len(str(message)) >= 4096:
            await ctx.send(f"Logs message is too long. (Should be less than 4096 characters and is {lenght_message})")
            return

        class FakeInvite():
            approximate_member_count = 111
            approximate_presence_count = 22
            channel = ctx.channel
            code = "fake"
            created_at = datetime.now()
            expires_at = None
            guild = ctx.guild
            id = code
            inviter = ctx.author
            max_age = 60*5
            max_uses = 5
            revoked = False
            scheduled_event = None
            scheduled_event_id = None
            target_application = None
            target_type = discord.InviteTarget.unknown
            target_user = None
            temporary = False
            url = f"https://discord.gg/{code}"
            uses = 2

        fake_invite = FakeInvite()

        try:
            log_message = message.format(
                invite = fake_invite, 
                member = ctx.author, 
                created_at_timestamp = round(fake_invite.created_at.timestamp()), 
                expires_at_timestamp = round(fake_invite.expires_at.timestamp()) if fake_invite.expires_at else 33197904000,
                max_uses = '♾️' if fake_invite.max_uses == 0 else fake_invite.max_uses
            )

            embed = discord.Embed(title=f"{self.help_custom()[0]} Invite Tracker", color=0xDC143C, description=log_message)
            embed.timestamp = datetime.now()

            await self.bot.database.update(self.subconfig_data["table"], {"custom_message": message}, f"guild_id = {ctx.guild.id}")

            self.granted_guilds[ctx.guild.id] = (self.granted_guilds[ctx.guild.id][0], message)

            await ctx.send(embed=embed, content="Custom message set.")
        except ValueError:
            await ctx.send("Wrong formatting.")


async def setup(bot: DiscordBot):
    await bot.add_cog(Invite(bot))