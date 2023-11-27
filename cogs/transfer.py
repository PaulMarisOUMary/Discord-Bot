import discord

from discord import app_commands
from discord.ext import commands, tasks
from discord.utils import get
from typing import Optional

from classes.discordbot import DiscordBot
from classes.utilities import bot_has_permissions

from views.button import CustomButton, View


@app_commands.guild_only()
class Transfer(commands.GroupCog, name="transfer", group_name="transfer", group_description="Commands related to role transfer."):
    """
    Transfer your roles safely to another guild member.

    Require intents:
            - default

    Require bot permission:
            - administrator
    """

    def __init__(self, bot: DiscordBot) -> None:
        self.bot = bot

        self.subconfig_data: dict = self.bot.config["cogs"][self.__cog_name__.lower()]
        self.table = self.subconfig_data["table"]

        self.granted_roles: dict[int, list[discord.Role]] = {}

    def help_custom(self) -> tuple[str, str, str]:
        emoji = "🔁"
        label = "Transfer"
        description = "Show the list of transfer commands."
        return emoji, label, description

    async def cog_load(self) -> None:
        self.init_invites.start()

    @tasks.loop(count=1)
    async def init_invites(self) -> None:
        """This task is run ONLY ONCE at cog load."""
        await self.bot.wait_until_ready()

        await self.__update_granted_roles()

    async def __update_granted_roles(self) -> None:
        self.granted_roles = {}  # Reset the cache

        database_roles: tuple[Optional[tuple[int, int]]] = await self.bot.database.select(self.subconfig_data["table"], "*")
        for (guild_id, role_id) in database_roles:
            guild_object = get(self.bot.guilds, id=guild_id)

            if not guild_object:
                continue

            role_object = guild_object.get_role(role_id)

            if not role_object:
                continue

            if guild_id in self.granted_roles:
                self.granted_roles[guild_id].append(role_object)
            else:
                self.granted_roles[guild_id] = [role_object]

    @bot_has_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="create", description="Create a role transfer.")
    @app_commands.checks.cooldown(1, 15.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.guild_only()
    async def transfer_create(self, interaction: discord.Interaction, role: discord.Role) -> None:
        """Allows you to create a transferable role."""
        if (interaction.guild_id in self.granted_roles and role in self.granted_roles[interaction.guild_id]):
            return await interaction.response.send_message("This role is already transferable.")

        await self.bot.database.insert(self.subconfig_data["table"], {"guild_id": interaction.guild_id, "role_id": role.id})
        await self.__update_granted_roles()

        await interaction.response.send_message(f"The {role.mention} role is now transferable.", allowed_mentions=discord.AllowedMentions.none())

    async def role_suggest(self, interaction: discord.Interaction, _: str) -> list[app_commands.Choice[int]]:
        if interaction.guild_id not in self.granted_roles:
            return []

        choices = [
            app_commands.Choice(name=f"@{role.name}", value=role.id)
            for role in self.granted_roles[interaction.guild_id]
        ]

        return choices[:25]

    @bot_has_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="delete", description="Delete a role transfer.")
    @app_commands.checks.cooldown(1, 15.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.autocomplete(roles=role_suggest)
    @app_commands.guild_only()
    async def transfer_delete(self, interaction: discord.Interaction, roles: int) -> None:
        """Allows you to delete a transferable role."""
        role_object = interaction.guild.get_role(roles)  # type: ignore
        if not role_object:
            return await interaction.response.send_message("This role has not been found.")

        if (interaction.guild_id not in self.granted_roles or role_object not in self.granted_roles[interaction.guild_id]):
            return await interaction.response.send_message("This role can't be deleted.")

        await self.bot.database.delete(self.subconfig_data["table"], f"guild_id = {interaction.guild_id} AND role_id = {role_object.id}")
        await self.__update_granted_roles()

        await interaction.response.send_message(f"The {role_object.mention} role is no longer transferable.", allowed_mentions=discord.AllowedMentions.none())

    @bot_has_permissions(administrator=True)
    @app_commands.command(name="role", description="Transfer your role to another member.")
    @app_commands.checks.cooldown(1, 15.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.autocomplete(role=role_suggest)
    @app_commands.guild_only()
    async def transfer_role(self, interaction: discord.Interaction[DiscordBot], role: int, member: discord.Member) -> None:
        """Allows you to transfer your role to another member."""
        if member.bot:
            return await interaction.response.send_message("You can't transfer your role to a bot.")
        if role not in interaction.user.roles:  # type: ignore
            return await interaction.response.send_message("You don't have this role.")
        if (interaction.guild_id in self.granted_roles and role not in self.granted_roles[interaction.guild_id]):
            return await interaction.response.send_message("This role can't be transfered, ask an administrator to make it transferable using `/transfer create @role`.")
        if role in member.roles:
            return await interaction.response.send_message("This member already has this role.")

        view = View(interaction)

        async def transfer_confirm(_class, view_interaction: discord.Interaction) -> None:
            if _class.view.invoke.user == interaction.user:
                await member.add_roles(role)
                await interaction.user.remove_roles(role)  # type: ignore

                await interaction.delete_original_response()

                await view_interaction.response.send_message(f"✅ {interaction.user.mention} has transfered the {role.mention} role to {member.mention}.", allowed_mentions=discord.AllowedMentions.none())
            else:
                await interaction.response.send_message("❌ Hey it's not your session !", ephemeral=True)

        async def transfer_cancel(_class, view_interaction: discord.Interaction) -> None:
            if _class.view.invoke.user == interaction.user:
                await view_interaction.response.send_message(f"🚫 {interaction.user.mention} has canceled the transfer.", allowed_mentions=discord.AllowedMentions.none())

                await interaction.delete_original_response()
            else:
                await interaction.response.send_message("❌ Hey it's not your session !", ephemeral=True)

        view.add_item(
            CustomButton(
                style=discord.ButtonStyle.green,
                label="Yes, transfer.",
                emoji="✅",
                when_callback=transfer_confirm,
            )
        )
        view.add_item(
            CustomButton(
                style=discord.ButtonStyle.red,
                label="No, abort.",
                emoji="🚫",
                when_callback=transfer_cancel,
            )
        )

        await interaction.response.send_message(f"⚠️ Warning, this action is irreversible.\nThe {role.mention} role will be transfered to {member.mention}.\nAre you sure ?", view=view, allowed_mentions=discord.AllowedMentions.none())



async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Transfer(bot))