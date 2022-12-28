import discord

from discord.ext import commands
from typing import Union

from classes.database import MixedTypes
from classes.discordbot import DiscordBot

class Metrics(commands.Cog, name="metrics"):
	"""
		Store bot's metrics in the database.
		Fore statistics and analytics. 
	
		Require intents: 
			- None
		
		Require bot permission:
			- None
	"""
	def __init__(self, bot: DiscordBot) -> None:
		self.bot = bot

		self.subconfig_data: dict = self.bot.config["cogs"][self.__cog_name__.lower()]

	def help_custom(self) -> tuple[str, str, str]:
		emoji = '📈'
		label = "Metrics"
		description = "All metrics related to the bot."
		return emoji, label, description

	@commands.Cog.listener("on_command")
	async def on_command(self, context: commands.Context) -> None:
		if context.interaction:
			return

		if isinstance(context.command, commands.hybrid.HybridCommand):
			await self.add_metrics(context.command.qualified_name, "commands.HybridCommand", context.author)

		elif isinstance(context.command, commands.core.Command):
			await self.add_metrics(context.command.qualified_name, "commands.Command", context.author)

	@commands.Cog.listener("on_interaction")
	async def on_interaction(self, interaction: discord.Interaction) -> None:
		if not interaction.type == discord.InteractionType.application_command:
			return
		
		if isinstance(interaction.command, commands.hybrid.HybridAppCommand):
			await self.add_metrics(interaction.command.qualified_name, "commands.HybridCommand", interaction.user)

		elif isinstance(interaction.command, discord.app_commands.commands.Command):
			await self.add_metrics(interaction.command.qualified_name, "application_commands.Command", interaction.user)

	async def add_metrics(self, command_name: str, command_type: str, invoker: Union[discord.Member, discord.User]) -> None:
		"""Add a metric to the database."""
		# Avoid owner from being counted
		if self.bot.owner_ids and invoker.id in self.bot.owner_ids:
			return
		if invoker.id == self.bot.owner_id:
			return

		await self.bot.database.insert_onduplicate(
			self.subconfig_data["table"],
			{
				"command_name": command_name, 
				"command_count": MixedTypes("COALESCE(command_count, 0) + 1"), 
				"command_type": command_type
			}
		)



async def setup(bot: DiscordBot):
	await bot.add_cog(Metrics(bot))
