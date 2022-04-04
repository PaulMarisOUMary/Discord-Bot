import discord

from typing import Optional, Union
from discord.ext import commands
from discord import app_commands

class Errors(commands.Cog, name="errors"):
	"""Errors handler."""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		bot.tree.error(self.get_app_command_error)

		self.default_error_message = "🕳️ There is an error."

	"""def help_custom(self):
		emoji = "<a:crossmark:842800737221607474>"
		label = "Error"
		description = "A custom errors handler. Nothing to see here."
		return emoji, label, description"""

	@commands.Cog.listener("on_error")
	async def get_error(self, event, *args, **kwargs):
		"""Error handler"""
		print(f"! Unexpected Internal Error: (event) {event}, (args) {args}, (kwargs) {kwargs}.")

	@commands.Cog.listener("on_command_error")
	async def get_command_error(self, ctx: commands.Context, error: commands.CommandError):
		"""Command Error handler"""
		try:
			try:
				raise error
			except commands.BotMissingPermissions as d_error:
				if not "send_messages" in d_error.missing_permissions:
					await ctx.send(f"🕳️ Missing permissions: `{'` `'.join(d_error.missing_permissions)}`")
			except commands.CommandNotFound as d_error:
				await ctx.send(f"🕳️ Command `{str(d_error).split(' ')[1]}` not found !")
			except commands.NotOwner:
				await ctx.send("🕳️ You must own this bot to run this command.")
			except commands.NoPrivateMessage:
				await ctx.send("🕳️ This command cannot be used in a private message.")
			except commands.CommandOnCooldown as d_error:
				await ctx.send(f"🕳️ Command is on cooldown, wait `{str(d_error).split(' ')[7]}` !")
			except commands.MissingRequiredArgument:
				await ctx.send(f"🕳️ Something is missing. `{ctx.clean_prefix}{ctx.command.name} <{'> <'.join(ctx.command.clean_params)}>`")
			except commands.DisabledCommand:
				await ctx.send("🕳️ This command is disabled.")
			except commands.MemberNotFound as d_error:
				await ctx.send(f"🕳️ Member `{str(d_error).split(' ')[1]}` not found ! Don't hesitate to ping the requested member.")
			except commands.MissingPermissions:
				await ctx.send("🕳️ This command require more permissions.")
			except commands.CommandInvokeError as d_error:
				await ctx.send(f"🕳️ {d_error.original}")
			except Exception as e:
				print(f"! Cogs.errors get_command_error (first level) : {type(error).__name__} : {error}\n! Internal Error : {e}\n")
		except discord.errors.Forbidden:
			pass
		except Exception as e:
			print(f"! Cogs.errors get_command_error : {type(error).__name__} : {error}\n! Internal Error : {e}\n")

	#@app_commands.Cog.listener("on_command_error") / @app_commands.Cog.listener("on_app_command_error") #still in dev, hopefully something like this
	async def get_app_command_error(self, interaction: discord.Interaction, command: Optional[Union[discord.app_commands.Command, discord.app_commands.ContextMenu]], error: discord.app_commands.AppCommandError):
		"""App command Error Handler
		doc: https://discordpy.readthedocs.io/en/master/interactions/api.html?highlight=commandnotfound#exception-hierarchy
		"""
		try:
			try:
				await interaction.response.send_message(self.default_error_message)
			except discord.errors.InteractionResponded:
				pass
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

			print(f"! Cogs.errors get_app_command_error : {type(error).__name__} : {error}\n! Internal Error : {e}\n")



async def setup(bot):
	await bot.add_cog(Errors(bot))