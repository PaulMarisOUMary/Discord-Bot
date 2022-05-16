import discord

from views.modal import CustomModal

from discord.ext import commands
from discord import app_commands

@app_commands.guild_only()
class PrivateTextual(commands.GroupCog, name="privatetextual", group_name="private", group_description="Private Textual Commands."):
	"""
		Create and manage private textual channels.

		Require intents:
			- default
		
		Require bot permission:
			- manage_channels
	"""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

	def help_custom(self) -> tuple[str, str, str]:
		emoji = '💬'
		label = "Private Textual"
		description = "Add and edit textuals channels."
		return emoji, label, description

	@app_commands.command(name="create", description="Create a private textual channel.")
	@app_commands.checks.cooldown(1, 15.0, key=lambda i: (i.guild_id, i.user.id))
	async def create(self, interaction: discord.Interaction):
		"""Create a private textual channel.
		doc: https://discord.com/developers/docs/resources/channel#channel-object-channel-structure"""
		
		async def when_submit(_class: CustomModal, interaction: discord.Interaction):
			values: dict = _class.values
			try:
				channel = await interaction.guild.create_text_channel(name='_'+values["name"], topic=values["description"], category=interaction.channel.category, reason="Create private textual channel.")
				
				category_permissions = interaction.channel.category.overwrites

				overwrites = dict()
				for role, _ in category_permissions.items():
					overwrites[role] = 1 # ! Need refactor

				await channel.edit(overwrites=overwrites)

				await interaction.response.send_message(f"Success ! {channel.mention} created.")
			except Exception as e:
				print(e)
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
					max_length=1024
				)
			},
			when_submit=when_submit
		)

		await interaction.response.send_modal(modal)



async def setup(bot):
	await bot.add_cog(PrivateTextual(bot))