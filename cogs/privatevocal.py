import discord

from discord.ext import commands
from discord.utils import get

class PrivateVocal(commands.Cog, name="privatevocal"):
	"""Create and manage private textual channels.
		Require intents.voice_states intent."""

	MAIN_NAME = "➕"
	PRIVATE_NAME = "Private Vocal N°{}"
	
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.tracker = dict()

	def help_custom(self) -> tuple[str]:
		emoji = '💭'
		label = "Private Vocal"
		description = "Create and manage private vocals channels."
		return emoji, label, description

	def __is_private(self, channel: discord.VoiceChannel) -> bool:
		"""Check if the channel is private."""
		if channel is None:
			return False
		if channel.guild.id in self.tracker and channel.id in self.tracker[channel.guild.id]:
			return True
		if channel.name == self.MAIN_NAME:
			return channel.guild.id not in self.tracker or len(self.tracker[channel.guild.id]) == 0 # Only initialize one main channel
		return False

	async def __move_privates(self, before_channel: discord.VoiceChannel) -> None:
		"""Delete a private channel and rename the following ones"""
		guild_id = before_channel.guild.id
		guild_data = self.tracker[guild_id]
		start_index = guild_data.index(before_channel.id)

		guild_data.remove(before_channel.id)
		await before_channel.delete()
		for i, channel_id in enumerate(guild_data[start_index:], start=start_index):
			channel = self.bot.get_channel(channel_id)
			await channel.edit(name=self.PRIVATE_NAME.format(i))

	@commands.Cog.listener("on_voice_state_update")
	async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
		if not member.guild.id in self.tracker:
			if not self.__is_private(after.channel):
				return
			self.tracker[member.guild.id] = [after.channel.id]
		guild_data = self.tracker[member.guild.id]

		if after.channel is not None and self.__is_private(after.channel) and len(after.channel.members) == 1:

			name = self.PRIVATE_NAME.format(len(guild_data))
			channel = await after.channel.category.create_voice_channel(name = name)
			guild_data.append(channel.id)

		if before.channel is not None and self.__is_private(before.channel) and len(before.channel.members) == 0:

			if before.channel.id == guild_data[0]:
				channel = self.bot.get_channel(guild_data.pop())
				await channel.delete()
			else:
				await self.__move_privates(before.channel)



async def setup(bot):
	await bot.add_cog(PrivateVocal(bot))
