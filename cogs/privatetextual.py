import discord

from views.modal import CustomModal

from datetime import datetime
from discord.ext import commands
from discord import app_commands

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
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

		self.dashlock = '🔒'

	def help_custom(self) -> tuple[str, str, str]:
		emoji = '💬'
		label = "Private Textual"
		description = "Add and edit textuals channels."
		return emoji, label, description

	def __is_dash_channel(self, channel: discord.TextChannel) -> bool:
		return self.dashlock == channel.name[0]

	def __get_private_role(self, channel: discord.TextChannel) -> discord.Role:
		for role, permissions in channel.overwrites.items():
			if permissions.send_messages:
				return role

	@app_commands.command(name="create", description="Create a private textual channel.")
	@app_commands.checks.bot_has_permissions(manage_channels=True, manage_roles=True, view_channel=True)
	@app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.guild_id, i.user.id))
	async def create(self, interaction: discord.Interaction):
		"""Create a private textual channel.
		doc: https://discord.com/developers/docs/resources/channel#channel-object-channel-structure"""
		
		async def when_submit(_class: CustomModal, interaction: discord.Interaction):
			values: dict = _class.values
			reason = f"Create private textual role, requested by: {interaction.user}."
			try:
				channel = await interaction.guild.create_text_channel(name=self.dashlock+values["name"], topic=values["description"], category=interaction.channel.category, reason=reason)

				channel_role = await interaction.guild.create_role(name=f"{self.dashlock}team {round(datetime.now().timestamp())}:{interaction.user.id}", reason=reason)
				
				category_permissions = interaction.channel.category.overwrites

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

				await interaction.user.add_roles(channel_role, reason=reason)

				await interaction.response.send_message(f"Success ! {channel.mention} created.", ephemeral=True)

				await channel.send(f"{channel.mention} has been created by {interaction.user.mention} !\n||Delete the channel with: `/private delete`||\nAdd your teammates with: `/private add <user>`.")
			except Exception as e:
				await interaction.response.send_message(e)

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
					default=f"{interaction.user.display_name}'s private textual channel."
				)
			},
			when_submit=when_submit
		)

		await interaction.response.send_modal(modal)

	@app_commands.command(name="delete", description="Delete a private textual channel.")
	@app_commands.checks.bot_has_permissions(manage_channels=True, manage_roles=True, view_channel=True)
	@app_commands.checks.cooldown(1, 15.0, key=lambda i: (i.channel_id, i.user.id))
	async def delete(self, interaction: discord.Interaction):
		"""Delete a private textual channel."""

		reason = f"Delete private textual channel, requested by: {interaction.user}."
		channel_role = self.__get_private_role(interaction.channel)

		if not self.__is_dash_channel(interaction.channel) or not channel_role:
			await interaction.response.send_message("You can't delete a non private textual channel.\nTry to type this command in your private channel.", ephemeral=True)
			return

		if (owner := channel_role.name.split(":")[1]) != str(interaction.user.id) and not interaction.user.guild_permissions.administrator:
			await interaction.response.send_message(f"You can't delete a private textual channel that you don't own.\nOwner: <@{owner}>", ephemeral=True)
			return

		await channel_role.delete(reason=reason)

		await interaction.response.send_message(self.dashlock)
		await interaction.channel.delete(reason=reason)

	@app_commands.command(name="add", description="Add a user in the private textual channel.")
	@app_commands.describe(user="User to add.")
	@app_commands.checks.bot_has_permissions(manage_roles=True)
	@app_commands.checks.cooldown(1, 15.0, key=lambda i: (i.channel_id, i.user.id))
	async def add(self, interaction: discord.Interaction, user: discord.Member):
		channel_role = self.__get_private_role(interaction.channel)

		if not self.__is_dash_channel(interaction.channel) or not channel_role:
			await interaction.response.send_message("You can't delete a non private textual channel.\nTry to type this command in your private channel.", ephemeral=True)
			return

		await user.add_roles(channel_role, reason=f"Add private textual role to {user}, requested by: {interaction.user}.")

		await interaction.response.send_message(f"{user.mention} joined {interaction.channel.mention} !", ephemeral=True)



async def setup(bot):
	await bot.add_cog(PrivateTextual(bot))