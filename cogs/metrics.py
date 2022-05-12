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
			return

		if isinstance(context.command, commands.hybrid.HybridCommand) and not context.interaction:
			print("hybrid_command", context.command.qualified_name)
		elif isinstance(context.command, commands.core.Command) and not context.interaction:
			print("command", context.command.qualified_name)

			#await self.add_metrics(f"{context.command.qualified_name}", "commands.Command" , context.author)
			#await self.add_metrics(f"{context.interaction.command.qualified_name}", "commands.HybridCommand" , context.author)

	@commands.Cog.listener("on_interaction")
	async def on_interaction(self, interaction: discord.Interaction) -> None:
		if not interaction.type == discord.InteractionType.application_command:
			return
		
		if isinstance(interaction.command, commands.hybrid.HybridAppCommand):
			print("hybrid_command", interaction.command.qualified_name)
		elif isinstance(interaction.command, discord.app_commands.commands.Command):
			print("app_command", interaction.command.qualified_name)
			
			#await self.add_metrics(interaction.command.qualified_name, "application_commands.Command", interaction.user)

	async def add_metrics(self, command_name: str, command_type: str, invoker: discord.User) -> None:
		"""Add a metric to the database."""
		#if invoker.id in self.bot.owner_ids:
		#	return

		exist = await self.bot.database.exist(self.metrics_data["table"], "*", f'command_name="{command_name}"')

		if exist:
			await self.bot.database.increment(self.metrics_data["table"], "command_count", condition=f"command_name='{command_name}'")
		else:
			await self.bot.database.insert(table=self.metrics_data["table"], args={"command_name": command_name, "command_count": 1, "command_type": command_type})




async def setup(bot):
	await bot.add_cog(Metrics(bot))
