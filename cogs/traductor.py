import asyncio
import discord
import re

from discord.ext import commands
from googletrans import Translator #pip install googletrans==4.0.0-rc1

class Traductor(commands.Cog, name="traductor"):
	"""A Cog to translate each non-English messages"""
	def __init__(self, bot):
		self.bot = bot

	"""def help_custom(self):
		emoji = '<:Gtranslate:807986736663101440>'
		label = "Traductor"
		description = "Informations about the Traductor."
		return emoji, label, description"""

	@commands.Cog.listener("on_message")
	async def on_receive_message(self, message: discord.Message):
		convert_emoji = '🔀'
		converted_emoji = '⤵'

		mention_regex = re.compile(r"<@! *&*[0-9]+>") 	#@
		channel_regex = re.compile(r"<# [0-9]+>")		##
		emote_regex = re.compile(r"<: \w+: [0-9]+>") 	#::

		content = message.content
		if not message.author.bot and content != None and len(content.split(' ')) >= 3:
			try:
				analysis: str = Translator().detect(content).lang

				if not analysis == "en":
					translated = Translator().translate(content, dest="en", src=analysis).text
					flag_emoji = str(chr(127365 + (ord(analysis[0]))))+str(chr(127365 + (ord(analysis[1]))))
					
					for regex in [mention_regex, channel_regex, emote_regex]:
						targets = regex.findall(translated)
						if targets:
							for target in targets:
								translated = translated.replace(target, target.replace(' ', ''))

					await message.add_reaction(flag_emoji)
					await message.add_reaction(convert_emoji)

					try:
						def check(reaction, user) -> bool:
							return not user.bot and reaction.message.id == message.id and reaction.emoji == convert_emoji
						
						await self.bot.wait_for("reaction_add", timeout=25, check=check)
					except asyncio.exceptions.TimeoutError:
						await message.clear_reaction(convert_emoji)
					except: pass
					else:
						await message.reply(content=f"**`Translated from` {flag_emoji} `by` <:Gtranslate:807986736663101440> `:`** {translated}", mention_author=False)
						await message.clear_reaction(convert_emoji)
						await message.add_reaction(converted_emoji)

			except: pass



def setup(bot):
	bot.add_cog(Traductor(bot))
