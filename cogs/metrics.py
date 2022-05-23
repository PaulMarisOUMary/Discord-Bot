import discord
from discord.ext import commands

from classes.database import MixedTypes

class Metrics(commands.Cog, name="metrics"):
	"""
		Store bot's metrics in the database.
		Fore statistics and analytics. 
	
		Require intents: 
			- None
		
		Require bot permission:
			- None
	"""
	def __init__(self, bot: commands.Bot) -> None:
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

	async def add_metrics(self, command_name: str, command_type: str, invoker: discord.User) -> None:
		"""Add a metric to the database."""
		if invoker.id in self.bot.owner_ids or invoker.id == self.bot.owner_id: # Avoid owner from being counted
			return

		await self.bot.database.insert_onduplicate(
			self.subconfig_data["table"],
			{
				"command_name": command_name, 
				"command_count": MixedTypes("COALESCE(command_count, 0) + 1"), 
				"command_type": command_type
			}
		)



async def setup(bot):
	await bot.add_cog(Metrics(bot))
