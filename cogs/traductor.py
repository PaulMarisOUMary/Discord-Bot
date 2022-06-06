import asyncio
import discord
import re

from discord.ext import commands

from classes.discordbot import DiscordBot
from classes.translator import Translator

class Traductor(commands.Cog, name="traductor"):
	"""
		A Cog to translate each non-English messages (in english).

		Require intents:
			- message_content
		
		Require bot permission:
			- send_messages
			- add_reactions
	"""
	def __init__(self, bot: DiscordBot) -> None:
		self.bot = bot

	def help_custom(self) -> tuple[str, str, str]:
		emoji = "<:Gtranslate:807986736663101440>"
		label = "Traductor"
		description = "Informations about the Traductor."
		return emoji, label, description

	@commands.Cog.listener("on_message")
	async def on_receive_message(self, message: discord.Message):
		convert_emoji = '🔀'
		converted_emoji = '⤵'

		mention_regex = re.compile(r"<[@|@& ]*&*[0-9]+>") 	#@
		channel_regex = re.compile(r"<# [0-9]+>")		##
		emote_regex = re.compile(r"<: \w+: [0-9]+>") 	#::

		content = message.content
		if not message.author.bot and len(content.split(' ')) >= 3:
			try:
				analysis = Translator.detect(content)

				if not analysis == "en":
					flag_emoji = Translator.get_emoji(analysis)

					await message.add_reaction(flag_emoji)
					await message.add_reaction(convert_emoji)

					try:
						def check(reaction: discord.Reaction, user: discord.Member) -> bool:
							return not user.bot and reaction.message.id == message.id and reaction.emoji == convert_emoji
						
						await self.bot.wait_for("reaction_add", timeout=25, check=check)
					except asyncio.exceptions.TimeoutError or commands.EmojiNotFound:
						await message.clear_reaction(convert_emoji)
					else:
						translation = Translator.translate(content, dest="en", src=analysis)

						for regex in [mention_regex, channel_regex, emote_regex]:
							targets = regex.findall(translation)
							for target in targets:
								translation = translation.replace(target, target.replace(' ', ''))
						
						await message.reply(
							content = f"{flag_emoji} -> {Translator.get_emoji('en')} **:** {translation}", 
							mention_author = False, 
							allowed_mentions = discord.AllowedMentions.none(), 
							delete_after = 15
						)

						await message.clear_reaction(convert_emoji)
						await message.add_reaction(converted_emoji)
			except: 
				pass



async def setup(bot: DiscordBot):
	await bot.add_cog(Traductor(bot))
