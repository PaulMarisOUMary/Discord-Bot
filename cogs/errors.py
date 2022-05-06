import discord
import logging

from discord.ext import commands
from discord import app_commands

class Errors(commands.Cog, name="errors"):
	"""Errors handler."""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		bot.tree.error(coro = self.__dispatch_to_app_command_handler)

		self.logger = logging.getLogger('discord')
		self.default_error_message = "🕳️ There is an error."

	"""def help_custom(self):
		emoji = "<a:crossmark:842800737221607474>"
		label = "Error"
		description = "A custom errors handler. Nothing to see here."
		return emoji, label, description"""

	def trace_error(self, level: str, error: Exception):
		self.logger.name = f"discord.{level}"
		self.logger.error(msg=type(error).__name__, exc_info=error)
		
		print(f"! {level}: {error}")

	async def __dispatch_to_app_command_handler(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
		self.bot.dispatch("app_command_error", interaction, error)

	async def __respond_to_interaction(self, interaction: discord.Interaction) -> bool:
		try:
			await interaction.response.send_message(content=self.default_error_message, ephemeral=True)
			return True
		except discord.errors.InteractionResponded:
			return False

	@commands.Cog.listener("on_error")
	async def get_error(self, event, *args, **kwargs):
		"""Error handler"""
		print(f"! Unexpected Internal Error: (event) {event}, (args) {args}, (kwargs) {kwargs}.")

	@commands.Cog.listener("on_command_error")
	async def get_command_error(self, ctx: commands.Context, error: commands.CommandError):
		"""Command Error handler
		doc: https://discordpy.readthedocs.io/en/master/ext/commands/api.html#exception-hierarchy
		"""
		try:
			if ctx.interaction: # HybridCommand Support
				await self.__respond_to_interaction(ctx.interaction)
				edit = ctx.interaction.edit_original_message
				if isinstance(error, commands.HybridCommandError):
					error = error.original # Access to the original error
			else:
				discord_message = await ctx.send(self.default_error_message)
				edit = discord_message.edit

			raise error

		# ConversionError
		except commands.ConversionError as d_error:
			await edit(content=f"🕳️ {d_error}")
		# UserInputError
		except commands.MissingRequiredArgument as d_error:
			await edit(content=f"🕳️ Something is missing. `{ctx.clean_prefix}{ctx.command.name} <{'> <'.join(ctx.command.clean_params)}>`")
		# UserInputError -> BadArgument
		except commands.MemberNotFound or commands.UserNotFound as d_error:
			await edit(content=f"🕳️ Member `{str(d_error).split(' ')[1]}` not found ! Don't hesitate to ping the requested member.")
		# UserInputError -> BadUnionArgument | BadLiteralArgument | ArgumentParsingError
		except commands.BadArgument or commands.BadUnionArgument or commands.BadLiteralArgument or commands.ArgumentParsingError as d_error:
			await edit(content=f"🕳️ {d_error}")
		# CommandNotFound
		except commands.CommandNotFound as d_error:
			await edit(content=f"🕳️ Command `{str(d_error).split(' ')[1]}` not found !")
		# CheckFailure
		except commands.PrivateMessageOnly:
			await edit(content="🕳️ This command canno't be used in a guild, try in direct message.")
		except commands.NoPrivateMessage:
			await edit(content="🕳️ This is not working as excpected.")
		except commands.NotOwner:
			await edit(content="🕳️ You must own this bot to run this command.")
		except commands.MissingPermissions as d_error:
			await edit(content=f"🕳️ Your account require the following permissions: {'` `'.join(d_error.missing_permissions)}.")
		except commands.BotMissingPermissions as d_error:
			if not "send_messages" in d_error.missing_permissions:
				await edit(content=f"🕳️ The bot require the following permissions: {'` `'.join(d_error.missing_permissions)}.")
		except commands.CheckAnyFailure or commands.MissingRole or commands.BotMissingRole or commands.MissingAnyRole or commands.BotMissingAnyRole as d_error:
			await edit(content=f"🕳️ {d_error}")
		except commands.NSFWChannelRequired:
			await edit(content="🕳️ This command require an NSFW channel.")
		# DisabledCommand
		except commands.DisabledCommand:
			await edit(content="🕳️ Sorry this command is disabled.")
		# CommandInvokeError
		except commands.CommandInvokeError as d_error:
			await edit(content=f"🕳️ {d_error.original}")
		# CommandOnCooldown
		except commands.CommandOnCooldown as d_error:
			await edit(content=f"🕳️ Command is on cooldown, wait `{str(d_error).split(' ')[7]}` !")
		# MaxConcurrencyReached
		except commands.MaxConcurrencyReached as d_error:
			await edit(content=f"🕳️ Max concurrency reached. Maximum number of concurrent invokers allowed: `{d_error.number}`, per `{d_error.per}`.")
		# HybridCommandError
		except commands.HybridCommandError as d_error:
			await self.get_app_command_error(ctx.interaction, error)
		except Exception as e:
			self.trace_error("get_command_error", e)

	@commands.Cog.listener("on_app_command_error")
	async def get_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
		"""App command Error Handler
		doc: https://discordpy.readthedocs.io/en/master/interactions/api.html#exception-hierarchy
		"""
		try:
			await self.__respond_to_interaction(interaction)
			edit = interaction.edit_original_message

			raise error
		except app_commands.CommandInvokeError as d_error:
			if isinstance(d_error.original, discord.errors.InteractionResponded):
				await edit(content=f"🕳️ {d_error.original}")
			elif isinstance(d_error.original, discord.errors.Forbidden):
				await edit(content=f"🕳️ `{type(d_error.original).__name__}` : {d_error.original.text}")
			else:
				await edit(content=f"🕳️ `{type(d_error.original).__name__}` : {d_error.original}")
		except app_commands.CheckFailure as d_error:
			if isinstance(d_error, app_commands.errors.CommandOnCooldown):
				await edit(content=f"🕳️ Command is on cooldown, wait `{str(d_error).split(' ')[7]}` !")
			else:
				await edit(content=f"🕳️ `{type(d_error).__name__}` : {d_error}")
		except app_commands.CommandNotFound:
			await edit(content=f"🕳️ Command was not found.. Seems to be a discord bug, probably due to desynchronization.\nMaybe there is multiple commands with the same name, you should try the other one.")
		except Exception as e: 
			"""
			Caught here:
			app_commands.TransformerError
			app_commands.CommandLimitReached
			app_commands.CommandAlreadyRegistered
			app_commands.CommandSignatureMismatch
			"""

			self.trace_error("get_app_command_error", e)

	@commands.Cog.listener("on_view_error")
	async def get_view_error(self, interaction: discord.Interaction, error: Exception, item: any):
		"""View Error Handler"""
		try:
			raise error
		except discord.errors.Forbidden:
			pass
		except Exception as e:
			self.trace_error("get_view_error", e)

async def setup(bot):
	await bot.add_cog(Errors(bot))