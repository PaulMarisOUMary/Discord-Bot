import discord

from discord.ext import commands
from discord.utils import get

class PrivateVocal(commands.Cog, name="privatevocal"):
	"""Create and manage private textual channels.
		Require intents.voice_states intent."""
	
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.tracker = dict()
		self.MAIN_NAME = bot.config["privatevocal"]["main_name"]
		self.PRIVATE_NAME = bot.config["privatevocal"]["private_name"

	def help_custom(self) -> tuple[str]:
		emoji = '💭'
		label = "Private Vocal"
		description = "Create and manage private vocals channels."
		return emoji, label, description

	def __update_tracker(self, channel: discord.VoiceChannel) -> None:
		"""Update the tracker by adding the main channel if needed."""
		if channel is None or channel.guild.id in self.tracker or channel.name != self.MAIN_NAME:
			return
		self.tracker[channel.guild.id] = [channel.id]

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
		"""Delete a private channel and rename the following ones."""
		guild_id = before_channel.guild.id
		guild_data = self.tracker[guild_id]
		start_index = guild_data.index(before_channel.id)

		guild_data.remove(before_channel.id)
		await before_channel.delete()
		for i, channel_id in enumerate(guild_data[start_index:], start=start_index):
			channel = self.bot.get_channel(channel_id)
			await channel.edit(name=self.PRIVATE_NAME.format(i))

	async def __on_connect(self, channel: discord.VoiceChannel) -> None:
		"""Create a private channel if needed."""
		if channel is not None and self.__is_private(channel) and len(channel.members) == 1:

			guild_data = self.tracker[channel.guild.id]
			name = self.PRIVATE_NAME.format(len(guild_data))
			root = channel.category or channel.guild
			new_channel = await root.create_voice_channel(name = name)
			guild_data.append(new_channel.id)
	
	async def __on_disconnect(self, channel: discord.VoiceChannel) -> None:
		"""Delete a private channel if needed."""
		if channel is not None and channel.guild.id in self.tracker and self.__is_private(channel) and len(channel.members) == 0:

			guild_data = self.tracker[channel.guild.id]
			if channel.id == guild_data[0]:
				channel = self.bot.get_channel(guild_data.pop())
				await channel.delete()
			else:
				await self.__move_privates(channel)

	@commands.Cog.listener("on_voice_state_update")
	async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
		"""Update privates channels when a member joins or leaves a channel."""
		self.__update_tracker(after.channel)
		await self.__on_connect(after.channel)
		await self.__on_disconnect(before.channel)



async def setup(bot):
	await bot.add_cog(PrivateVocal(bot))
