from copy import copy
from datetime import datetime, timezone
from typing import Any

from discord import (
    Embed,
    Forbidden,
    Guild,
    HTTPException,
    InviteTarget,
    Member,
    TextChannel,
)
from discord import (
    Invite as dInvite,
)
from discord.ext import commands, tasks
from discord.utils import get
from sqlmodel import select

from models.sql import Invite as InviteModel
from utils.bot import DiscordBot
from utils.checks import bot_has_permissions
from utils.database import crud


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
        self.subconfig: dict[str, Any] = self.bot.config.cogs.cogs[
            self.__cog_name__.lower()
        ]

        self.invites: dict[int, dict[str, dInvite]] = {}
        self.granted_guilds: dict[int, tuple[TextChannel | None, str | None]] = {}

    def help_custom(self) -> tuple[str, str, str]:
        return "\U0001f4e8", "Invite Tracker", "Log each invite in the system channel."

    def __is_guild_granted(self, guild: Guild) -> bool:
        return guild.id in self.granted_guilds

    async def __update_granted_guilds(self) -> None:
        if self.bot.database is None:
            return

        async with self.bot.database.session() as session:
            granted_guilds = (await session.exec(select(InviteModel))).all()

        for row in granted_guilds:
            guild_object = get(self.bot.guilds, id=row.guild_id)
            if not guild_object:
                continue

            channel_object = guild_object.get_channel(row.channel_id)
            if not isinstance(channel_object, TextChannel):
                continue

            self.granted_guilds[row.guild_id] = (channel_object, row.custom_message)

    async def __seek_invite(
        self, before: dict[str, dInvite], after: dict[str, dInvite]
    ) -> dInvite | None:
        # Seek increment uses in invites
        for id, invite in after.items():
            before_uses = before[id].uses
            if (
                invite.uses is not None
                and before_uses is not None
                and invite.uses > before_uses
            ):
                return invite

        # Seek missing invite (only expirable)
        before_after = set(before.items()) - set(after.items())
        for id, invite in before_after:
            if expire := invite.expires_at:
                if expire > datetime.now(timezone.utc):
                    invite.uses = invite.max_uses
                    return invite

        # Mystery
        return None

    async def __update_invites(self, *guilds: Guild | None) -> None:
        if not guilds:
            guilds = tuple(self.bot.guilds)

        try:
            for guild in guilds:
                if not guild:
                    continue
                self.invites.setdefault(guild.id, {})
                self.invites[guild.id] = {
                    invite.id: invite for invite in await guild.invites()
                }
        except (Forbidden, HTTPException):
            pass

    async def cog_load(self) -> None:
        self.init_invites.start()

    @tasks.loop(count=1)
    async def init_invites(self) -> None:
        """This task is run ONLY ONCE at cog load."""
        await self.bot.wait_until_ready()

        await self.__update_granted_guilds()
        await self.__update_invites()

    @commands.Cog.listener("on_invite_create")
    async def on_invite_create(self, invite: dInvite) -> None:
        """Trigger when an invite is created."""
        if not isinstance(invite.guild, Guild) or not self.__is_guild_granted(
            invite.guild
        ):
            return

        await self.__update_invites(invite.guild)

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: Member) -> None:
        if not self.__is_guild_granted(member.guild) or member.bot:
            return

        try:
            before = copy(self.invites[member.guild.id])
            await self.__update_invites(member.guild)
            after = self.invites[member.guild.id]

            invite = await self.__seek_invite(before, after)
            if not invite:
                return

            channel, custom_message = self.granted_guilds[member.guild.id]
            format_log_message = custom_message or self.subconfig["default_message"]

            log_message = format_log_message.format(
                invite=invite,
                member=member,
                created_at_timestamp=round(invite.created_at.timestamp())
                if invite.created_at
                else 0,
                expires_at_timestamp=round(invite.expires_at.timestamp())
                if invite.expires_at
                else 33197904000,
                max_uses="\u267e\ufe0f" if invite.max_uses == 0 else invite.max_uses,
            )

            embed = Embed(
                title=f"{self.help_custom()[0]} Invite Tracker",
                color=0xDC143C,
                description=log_message,
            )
            embed.timestamp = datetime.now()

            if not channel:
                channel = member.guild.system_channel
                if not channel:
                    return

            await channel.send(embed=embed)
        except KeyError:  # Guild not in invites -> Missing manage_guild permission
            pass
        except (Forbidden, HTTPException):  # Missing manage_channels permission
            pass
        except ValueError:  # Invalid formatting
            pass

    @bot_has_permissions(manage_channels=True, manage_guild=True, view_channel=True)
    @commands.command(name="logs")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 25, commands.BucketType.guild)
    @commands.guild_only()
    async def config_invite_logs(
        self, ctx: commands.Context, channel: TextChannel
    ) -> None:
        """Set the invite tracker channel."""
        assert ctx.guild is not None  # guaranteed by @commands.guild_only()

        if self.bot.database is None:
            await ctx.send(
                ":warning: The database isn't available, the invite tracker can't be configured."
            )
            return

        async with self.bot.database.session() as session:
            await crud.upsert(
                session, InviteModel(guild_id=ctx.guild.id, channel_id=channel.id)
            )
            await session.commit()

        await ctx.send(f"Logs channel set to {channel.mention}.")

        await self.__update_granted_guilds()
        await self.__update_invites(ctx.guild)

    @bot_has_permissions(manage_channels=True, manage_guild=True, view_channel=True)
    @commands.command(name="logscustom")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 25, commands.BucketType.guild)
    @commands.guild_only()
    async def config_invite_logs_custom_message(
        self, ctx: commands.Context, *, message: str | None = None
    ) -> None:
        """Set a custom message for the invite tracker.

        Formatting variables:
        {invite} - The invite object.
        {member} - The member that joined.
        {created_at_timestamp} - The timestamp of the invite creation (int).
        {expires_at_timestamp} - The timestamp of the invite expiration (int).
        {max_uses} - The max uses of the invite."""
        assert ctx.guild is not None  # guaranteed by @commands.guild_only()

        if not self.__is_guild_granted(ctx.guild):
            return

        if self.bot.database is None:
            await ctx.send(
                ":warning: The database isn't available, the invite tracker can't be configured."
            )
            return

        if not message:
            async with self.bot.database.session() as session:
                invite_row = await session.get(InviteModel, ctx.guild.id)
                if invite_row:
                    invite_row.custom_message = None
                    session.add(invite_row)
                    await session.commit()

            self.granted_guilds[ctx.guild.id] = (
                self.granted_guilds[ctx.guild.id][0],
                None,
            )
            await ctx.send("Logs message set to default.")
            return

        if len(message) >= 4096:
            await ctx.send(
                f"Logs message is too long. (Should be less than 4096 characters and is {len(message)})"
            )
            return

        class FakeInvite:
            approximate_member_count = 111
            approximate_presence_count = 22
            channel = ctx.channel
            code = "fake"
            created_at = datetime.now()
            expires_at = None
            guild = ctx.guild
            id = code
            inviter = ctx.author
            max_age = 60 * 5
            max_uses = 5
            revoked = False
            scheduled_event = None
            scheduled_event_id = None
            target_application = None
            target_type = InviteTarget.unknown
            target_user = None
            temporary = False
            url = f"https://discord.gg/{code}"
            uses = 2

        fake_invite = FakeInvite()

        try:
            log_message = message.format(
                invite=fake_invite,
                member=ctx.author,
                created_at_timestamp=round(fake_invite.created_at.timestamp()),
                expires_at_timestamp=round(fake_invite.expires_at.timestamp())
                if fake_invite.expires_at
                else 33197904000,
                max_uses="\u267e\ufe0f"
                if fake_invite.max_uses == 0
                else fake_invite.max_uses,
            )

            embed = Embed(
                title=f"{self.help_custom()[0]} Invite Tracker",
                color=0xDC143C,
                description=log_message,
            )
            embed.timestamp = datetime.now()

            async with self.bot.database.session() as session:
                invite_row = await session.get(InviteModel, ctx.guild.id)
                if invite_row:
                    invite_row.custom_message = message
                    session.add(invite_row)
                    await session.commit()

            self.granted_guilds[ctx.guild.id] = (
                self.granted_guilds[ctx.guild.id][0],
                message,
            )

            await ctx.send(embed=embed, content="Custom message set.")
        except (KeyError, IndexError):
            await ctx.send("Wrong formatting.")


async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Invite(bot))
