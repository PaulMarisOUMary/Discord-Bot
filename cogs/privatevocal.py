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

	def __update_tracker(self, guild_data: dict, channel: discord.VoiceChannel) -> None:
		"""Update the guild tracker data."""
		if not channel.id in guild_data:
			guild_data[channel.id] = list()
		guild_data[channel.id] = [member.id for member in channel.members]

	@commands.Cog.listener("on_voice_state_update")
	async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
		if not member.guild.id in self.tracker: 
			self.tracker[member.guild.id] = dict()
		guild_data = self.tracker[member.guild.id]
		
		if after.channel and not before.channel: # Connect

				print("Connect")

		elif (after.channel and before.channel) and not (after.channel == before.channel): # Switch in same guild
	
				print("Switch")
			
		elif not after.channel and before.channel: # Disconnect

				print("Disconnect")

		print(guild_data)



async def setup(bot):
	await bot.add_cog(PrivateVocal(bot))