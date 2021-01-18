import discord

from discord.ext import commands
from googletrans import Translator #pip install googletrans==4.0.0-rc1


class Traductor(commands.Cog, name="Traductor"):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='test', aliases=['t'])
	async def test(self, ctx):
		pass

	@commands.Cog.listener('on_message')
	async def on_receive_message(self, message):
		convert_emoji = '🔀'
		def check(reaction, user):
			return str(reaction.emoji) == convert_emoji and not user.bot

		content = message.content
		if not message.author.bot:
			analysis = Translator().detect(content).lang

			if not analysis == 'en' and len(content.split(' ')) >= 3:
				translated, flag_emoji = Translator().translate(content, dest='en', src=analysis).text, str(chr(127365 + (ord(analysis[0]))))+str(chr(127365 + (ord(analysis[1]))))
				await message.add_reaction(emoji=flag_emoji)
				await message.add_reaction(emoji=convert_emoji)
				try:
					reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=check)
				except: await message.clear_reaction(convert_emoji)
				mess, reactions = await message.channel.history(limit=1).flatten(), discord.utils.get(message.reactions, emoji=convert_emoji)
				if mess[0].content == content and reactions:
					await message.reply(content=flag_emoji+" `Translated :` "+translated, mention_author=False)
				else:
					await message.clear_reaction(convert_emoji)

def setup(bot):
	bot.add_cog(Traductor(bot))