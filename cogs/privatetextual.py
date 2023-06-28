import discord

from datetime import datetime
from discord import app_commands
from discord.ext import commands
from discord.utils import format_dt
from typing import Optional

from classes.discordbot import DiscordBot
from classes.utilities import bot_has_permissions

from views.modal import CustomModal

@app_commands.guild_only()
class PrivateTextual(commands.GroupCog, name="privatetextual", group_name="private", group_description="Private Textual Commands."):
	"""
		Create and manage private textual channels.

		Require intents:
			- None
		
		Require bot permission:
			- manage_channels
			- manage_roles
			- view_channel
	"""
	def __init__(self, bot: DiscordBot) -> None:
		self.bot = bot

		self.dashlock = '🔒'

	def help_custom(self) -> tuple[str, str, str]:
		emoji = '💬'
		label = "Private Textual"
		description = "Add and edit textuals channels."
		return emoji, label, description
	
	def __get_owner_id(self, private_role: discord.Role) -> str:
		return private_role.name.split(':')[1]

	def __is_dash_channel(self, channel: discord.TextChannel) -> bool:
		return self.dashlock == channel.name[0]

	def __get_private_role(self, channel: discord.TextChannel) -> Optional[discord.Role]:
		for role, permissions in channel.overwrites.items():
			if isinstance(role, discord.Role) and permissions.send_messages:
				if role.name[len(self.dashlock):len(self.dashlock)+4] == "team" and len(role.name.split(':')) > 1:
					return role

	@bot_has_permissions(manage_channels=True, manage_roles=True, view_channel=True)
	@app_commands.command(name="create", description="Create a private textual channel.")
	@app_commands.checks.cooldown(1, 300.0, key=lambda i: (i.guild_id, i.user.id))
	async def create(self, interaction: discord.Interaction) -> None:
		"""Create a private textual channel.
		doc: https://discord.com/developers/docs/resources/channel#channel-object-channel-structure"""
		
		async def when_submit(_class: CustomModal, interaction: discord.Interaction) -> None:
			values: dict = _class.values
			reason = f"Create private textual role, requested by: {interaction.user}."
			try:
				channel = await interaction.guild.create_text_channel(name=self.dashlock+values["name"], topic=values["description"], category=interaction.channel.category, reason=reason) # type: ignore (@guild_only)

				channel_role = await interaction.guild.create_role(name=f"{self.dashlock}team {round(datetime.now().timestamp())}:{interaction.user.id}", reason=reason) # type: ignore (@guild_only)
				
				category_permissions = interaction.channel.category.overwrites # type: ignore (@guild_only)

				new_overwrites = dict()
				for role in category_permissions.keys():
					new_overwrites[role] = discord.PermissionOverwrite.from_pair(discord.Permissions.none(), discord.Permissions.all())
				new_overwrites[channel_role] = discord.PermissionOverwrite(
					add_reactions=True,
					attach_files=True,
					create_private_threads=True,
					create_public_threads=True,
					embed_links=True,
					external_emojis=True,
					external_stickers=True,
					manage_messages=True,
					manage_threads=True,
					mention_everyone=True,
					read_message_history=True,
					read_messages=True,
					send_messages=True,
					send_messages_in_threads=True,
					use_application_commands=True,
					use_embedded_activities=True,
					view_channel=True
				)

				await channel.edit(overwrites=new_overwrites)

				await interaction.user.add_roles(channel_role, reason=reason) # type: ignore (@guild_only)

				await interaction.response.send_message(f"Success ! {channel.mention} created.")

				await channel.send(f"{channel.mention} has been created by {interaction.user.mention} !\n||Delete the channel with: `/private delete`||\nAdd your teammates with: `/private add <user>`.")
			except Exception as e:
				await interaction.response.send_message(e, ephemeral=True)

		modal = CustomModal(
			title = "Create private textual channel",
			fields = {
				"name": discord.ui.TextInput(
					label="Channel name",
					placeholder="Your channel name here...",
					style=discord.TextStyle.short,
					required=True,
					min_length=1,
					max_length=100
				),
				"description": discord.ui.TextInput(
					label="Channel description",
					placeholder="Your channel description here...",
					style=discord.TextStyle.long,
					required=False,
					max_length=1024,
					default=f"{interaction.user.display_name}' private textual channel."
				)
			},
			when_submit=when_submit
		)

		await interaction.response.send_modal(modal)

	@bot_has_permissions(manage_channels=True, manage_roles=True, view_channel=True)
	@app_commands.command(name="delete", description="Delete a private textual channel.")
	@app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.channel_id, i.user.id))
	async def delete(self, interaction: discord.Interaction) -> None:
		"""Delete a private textual channel."""

		reason = f"Delete private textual channel, requested by: {interaction.user}."
		channel_role = self.__get_private_role(interaction.channel) # type: ignore (@guild_only)

		if not self.__is_dash_channel(interaction.channel) or not channel_role: # Private channel check # type: ignore (@guild_only)
			await interaction.response.send_message("You can't delete a non private textual channel.\nTry to type this command in your private channel.", ephemeral=True)
			return

		if (owner := self.__get_owner_id(channel_role)) != str(interaction.user.id) and not interaction.user.guild_permissions.administrator: # Avoid user to delete channel: must be owner or admin # type: ignore (@guild_only)
			await interaction.response.send_message(f"You can't delete a private textual channel that you don't own.\nOwner: <@{owner}>", ephemeral=True)
			return

		await channel_role.delete(reason=reason)

		await interaction.response.send_message(self.dashlock)
		await interaction.channel.delete(reason=reason) # type: ignore (@guild_only)

	@bot_has_permissions(manage_roles=True)
	@app_commands.command(name="add", description="Add a user in the private textual channel.")
	@app_commands.describe(user="User to add.")
	@app_commands.checks.cooldown(1, 2.5, key=lambda i: (i.channel_id, i.user.id))
	async def add(self, interaction: discord.Interaction, user: discord.Member) -> None:
		channel_role = self.__get_private_role(interaction.channel) # type: ignore (@guild_only)

		if not self.__is_dash_channel(interaction.channel) or not channel_role: # Private channel check # type: ignore (@guild_only)
			await interaction.response.send_message("You can't add a user in a non private textual channel.\nTry to type this command in your private channel.", ephemeral=True)
			return

		await user.add_roles(channel_role, reason=f"Add private textual role to {user}, requested by: {interaction.user}.")

		await interaction.response.send_message(f"{user.mention} joined {interaction.channel.mention} !") # type: ignore (@guild_only)

	@bot_has_permissions(manage_roles=True)
	@app_commands.command(name="remove", description="Remove a user from the private textual channel.")
	@app_commands.describe(user="User to remove.")
	@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.channel_id, i.user.id))
	async def remove(self, interaction: discord.Interaction, user: discord.Member) -> None:
		channel_role = self.__get_private_role(interaction.channel) # type: ignore (@guild_only)

		if not self.__is_dash_channel(interaction.channel) or not channel_role: # Private channel check # type: ignore (@guild_only)
			await interaction.response.send_message("You can't remove a user from a non private textual channel.\nTry to type this command in your private channel.", ephemeral=True)
			return

		if not channel_role in user.roles: # Avoiding to remove a non-member: user must be member
			await interaction.response.send_message(f"You can't remove a non-member in your private textual private channel.\nType `/private add {user.name}`.", ephemeral=True)
			return

		if (owner := self.__get_owner_id(channel_role)) != str(interaction.user.id): # Avoid member to remove member: must be owner
			await interaction.response.send_message(f"You can't remove a user from the textual channel that you don't own.\nOwner: <@{owner}>.\nFor ownership ||<@{owner}> must type: `/private transferownership {interaction.user}`||", ephemeral=True)
			return

		if owner == str(user.id): # Avoid self remove
			await interaction.response.send_message("You can't remove yourself from the private textual channel.\nTransfer ownership to someone else using: `/private transferownership <user>`.\nOr delete the private textual channel with: `/private delete`", ephemeral=True)
			return

		await user.remove_roles(channel_role, reason=f"Remove private textual role from {user}, requested by: {interaction.user}.")

		await interaction.response.send_message(f"{user.mention} left {interaction.channel.mention} !") # type: ignore (@guild_only)

	@app_commands.command(name="info", description="Get information about a private textual channel.")
	@app_commands.checks.cooldown(1, 15.0, key=lambda i: (i.channel_id, i.user.id))
	async def info(self, interaction: discord.Interaction) -> None:
		channel_role = self.__get_private_role(interaction.channel) # type: ignore (@guild_only)

		if not self.__is_dash_channel(interaction.channel) or not channel_role: # Private channel check # type: ignore (@guild_only)
			await interaction.response.send_message("You can't get information about a non private textual channel.\nTry to type this command in your private channel.", ephemeral=True)
			return

		await interaction.response.send_message(f"Owner: <@{self.__get_owner_id(channel_role)}>\nCreated: {format_dt(interaction.channel.created_at, 'F')}", ephemeral=True) # type: ignore (@guild_only)

	@bot_has_permissions(manage_roles=True)
	@app_commands.command(name="transferownership", description="Transfer ownership of a private textual channel.")
	@app_commands.describe(user="User to transfer ownership.")
	@app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.channel_id, i.user.id))
	async def transferownership(self, interaction: discord.Interaction, user: discord.Member) -> None:
		if user.bot: # Avoid bot
			await interaction.response.send_message("You can't transfer ownership to a bot.", ephemeral=True)
			return

		channel_role = self.__get_private_role(interaction.channel) # type: ignore (@guild_only)

		if not self.__is_dash_channel(interaction.channel) or not channel_role: # Private channel check # type: ignore (@guild_only)
			await interaction.response.send_message("You can't transfer ownership of a non private textual channel.\nTry to type this command in your private channel.", ephemeral=True)
			return
		
		if not channel_role in user.roles: # Avoiding to transfer ownership to a non-member: user must be member
			await interaction.response.send_message(f"You can't transfer ownership to a non-member of your private textual private channel.\nType `/private add {user.name}`.", ephemeral=True)
			return

		if (owner := self.__get_owner_id(channel_role)) != str(interaction.user.id): # Avoid member to transfer ownership: must be owner
			await interaction.response.send_message(f"You can't transfer ownership of a textual channel that you don't own.\nOwner: <@{owner}>.\nFor ownership ||<@{owner}> must type: `/private transferownership {interaction.user}`||", ephemeral=True)
			return

		await channel_role.edit(name=f"{channel_role.name.split(':')[0]}:{user.id}", reason=f"Transfer ownership of {interaction.channel.mention} to {user.mention}, requested by {interaction.user}.") # type: ignore (@guild_only)

		await interaction.response.send_message(f"{interaction.channel.mention} ownership transfered to {user.mention} !") # type: ignore (@guild_only)

	@bot_has_permissions(manage_roles=True, manage_channels=True)
	@app_commands.command(name="edit", description="Edit a private textual channel.")
	@app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.channel_id, i.user.id))
	async def edit(self, interaction: discord.Interaction) -> None:
		channel_role = self.__get_private_role(interaction.channel) # type: ignore (@guild_only)

		if not self.__is_dash_channel(interaction.channel) or not channel_role: # Private channel check  # type: ignore (@guild_only)
			await interaction.response.send_message("You can't edit a non private textual channel.\nTry to type this command in your private channel.", ephemeral=True)
			return

		async def when_submit(_class: CustomModal, interaction: discord.Interaction) -> None:
			values: dict = _class.values
			await interaction.channel.edit(name=self.dashlock+values["name"], topic=values["description"], reason=f"Edit private textual channel {interaction.channel.mention} requested by {interaction.user}.") # type: ignore (@guild_only)
			await interaction.response.send_message(f"{interaction.channel.mention} edited !") # type: ignore (@guild_only)

		modal = CustomModal(
			title="Edit your private textual channel",
			fields={
				"name": discord.ui.TextInput(
					label="Channel name",
					placeholder="Your channel name here...",
					style=discord.TextStyle.short,
					required=True,
					min_length=1,
					max_length=100,
					default=f"{interaction.channel.name.replace(self.dashlock, '')}" # type: ignore (@guild_only)
				),
				"description": discord.ui.TextInput(
					label="Channel description",
					placeholder="Your channel description here...",
					style=discord.TextStyle.long,
					required=False,
					max_length=1024,
					default=f"{'' if not interaction.channel.topic else interaction.channel.topic}" # type: ignore (@guild_only)
				)
			},
			when_submit=when_submit
		)

		await interaction.response.send_modal(modal)

	@bot_has_permissions(manage_roles=True, manage_channels=True)
	@app_commands.command(name="leave", description="Leave a private textual channel owned by someone else.")
	@app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.channel_id, i.user.id))
	async def leave(self, interaction: discord.Interaction) -> None:
		channel_role = self.__get_private_role(interaction.channel) # type: ignore (@guild_only)

		if not self.__is_dash_channel(interaction.channel) or not channel_role: # Private channel check # type: ignore (@guild_only)
			await interaction.response.send_message("You can't leave a non private textual channel.\nTry to type this command in a private channel.", ephemeral=True)
			return

		if self.__get_owner_id(channel_role) == str(interaction.user.id): # Avoid owner to leave: must be member
			await interaction.response.send_message("You can't leave a textual channel that you own.\nType `/private delete` to delete your private textual channel.\nOr transfer the ownership with /private transferownership.", ephemeral=True)
			return
		
		await interaction.user.remove_roles(channel_role, reason=f"Leave private textual channel {interaction.channel.mention} requested by {interaction.user}.") # type: ignore (@guild_only)

		await interaction.response.send_message(f"{interaction.user.mention} left {interaction.channel.mention} !") # type: ignore (@guild_only)



async def setup(bot: DiscordBot) -> None:
	await bot.add_cog(PrivateTextual(bot))