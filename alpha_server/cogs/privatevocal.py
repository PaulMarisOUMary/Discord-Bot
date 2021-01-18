import asyncio
import discord

from discord.ext import commands
from googletrans import Translator


class Loop(commands.Cog, name="Loop"):
	def __init__(self, bot):
		self.bot = bot
		self.bot.loop.create_task(self.loop_if_connected())

	async def loop_if_connected(self):
		GUILD, MAIN_CHANNEL = "Algosup Alpha", "General"
		await self.bot.wait_until_ready()
		guild = discord.utils.get(self.bot.guilds, name=GUILD)
		channel = discord.utils.get(guild.channels, name=MAIN_CHANNEL)
		category = discord.utils.get(guild.categories, id=channel.category_id)
		channels = [channel]

		def channelInfos():
			empty, used = len(channels), 0
			for ch in channels:
				if ch.members:
					used += 1
			empty -= used

			return empty, used

		while not self.bot.is_closed():
			emptyChannels, usedChannels = channelInfos()
			is_change = False
			
			if usedChannels == len(channels):
				a = await guild.create_voice_channel(name="Vocal", category=category, sync_permissions=True)
				channels.append(a)
				is_change = True

			elif emptyChannels > 1:
				count, lock = 0, False
				for ch in channels:
					if not ch.members and not ch.name == MAIN_CHANNEL and not lock:
						await ch.delete()
						del channels[count]
						lock = True
					count += 1
				is_change = True
			
			if is_change:
				for i, ch in enumerate(channels):
					if not ch.name == MAIN_CHANNEL:
						await ch.edit(name="Vocal "+str(i))

			await asyncio.sleep(0.1)

def setup(bot):
	bot.add_cog(Loop(bot))