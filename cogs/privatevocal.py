import asyncio
import discord

from discord.ext import commands


class PrivateVocal(commands.Cog, name="privatevocal"):
	"""Vocal description"""
	def __init__(self, bot):
		self.bot = bot
		self.task_if_connected = self.bot.loop.create_task(self.loop_if_connected())

	def return_loop_task(self):
		return self.task_if_connected

	async def loop_if_connected(self):
		data = {}
		MAIN_CHANNEL = "General"
		await self.bot.wait_until_ready()

		def enumServers(servers=[]):
			for guild in self.bot.guilds:
				servers.append(guild)
			return servers

		def channelInfos(channels):
			empty, used = len(channels), 0
			for ch in channels:
				if ch.members:
					used += 1
			empty -= used
			return empty, used

		while not self.bot.is_closed():
			for guild in enumServers():
				channel = discord.utils.get(guild.channels, name=MAIN_CHANNEL)
				if channel :
					if not guild.id in data: data[guild.id] = [channel]
					category = discord.utils.get(guild.categories, id=channel.category_id)
					emptyChannels, usedChannels = channelInfos(data[guild.id])
					is_change = False

					if usedChannels == len(data[guild.id]):
						a = await guild.create_voice_channel(name="Vocal", category=category, sync_permissions=True)
						data[guild.id].append(a)
						is_change = True

					elif emptyChannels > 1:
						count, lock = 0, False
						for ch in data[guild.id]:
							if not ch.members and not ch.name == MAIN_CHANNEL and not lock:
								await ch.delete()
								del data[guild.id][count]
								lock = True
							count += 1
						is_change = True

					if is_change:
						for i, ch in enumerate(data[guild.id]):
							if not ch.name == MAIN_CHANNEL:
								await ch.edit(name="Vocal "+str(i))

			await asyncio.sleep(0.5)

def setup(bot):
	bot.add_cog(PrivateVocal(bot))
