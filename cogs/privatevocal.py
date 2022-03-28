import discord

from discord.ext import commands

class PrivateVocal(commands.Cog, name="privatevocal"):
	"""Create and manage private textual channels.
		Require intents.voice_states intent."""
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
		return channel.name == '➕' or channel.id in self.tracker[channel.guild.id]

	@commands.Cog.listener("on_voice_state_update")
	async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
		if not member.guild.id in self.tracker: 
			self.tracker[member.guild.id] = list()
		guild_data = self.tracker[member.guild.id]
		
		if after.channel is not None and before.channel is None: # Connect

				if self.__is_private(after.channel):
					print("Connect to private")

		elif after.channel is not None and before.channel is not None: # Switch in same guild
	
				if self.__is_private(after.channel) and self.__is_private(before.channel):
					print("Switch from private to private")

				elif self.__is_private(after.channel):
					print("Switch from public to private")

				elif self.__is_private(before.channel):
					print("Switch from private to public")
					
		elif after.channel is None and before.channel is not None: # Disconnect

				if self.__is_private(after.channel):
					print("Disconnect from private")

		print(guild_data)



async def setup(bot):
	await bot.add_cog(PrivateVocal(bot))