import discord
from discord.ext import commands

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

		self.metrics_data = self.bot.config["database"]["metrics"]

	def help_custom(self) -> tuple[str, str, str]:
		emoji = '📈'
		label = "Metrics"
		description = "All metrics related to the bot."
		return emoji, label, description

	@commands.Cog.listener("on_command")
	async def on_command(self, context: commands.Context) -> None:
		if context.interaction:
			print(f"hybrid {context.command.name}")
		else:
			print(f"command {context.command.name}")

	@commands.Cog.listener("on_interaction")
	async def on_interaction(self, interaction: discord.Interaction) -> None:
		if interaction.type == discord.InteractionType.application_command:
			print(f"slash {interaction.command.qualified_name} {discord.InteractionType.application_command}")
			await self.add_metrics(interaction.command.qualified_name, discord.InteractionType.application_command)

	async def add_metrics(self, command_name: str, command_type: any):
		"""Add a metric to the database."""
		try:
			await self.bot.database.increment(self.metrics_data["table"], "command_count", condition=f"command_name='{command_name}'")
		except Exception as e:
			await self.bot.database.insert(table=self.metrics_data["table"], args={"command_name": command_name, "command_count": 1, "command_type": str(command_type)})




async def setup(bot):
	await bot.add_cog(Metrics(bot))
