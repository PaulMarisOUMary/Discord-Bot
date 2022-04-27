import discord

from datetime import datetime
from discord.ext import commands
from typing import Union

class PrivateVocal(commands.Cog, name="privatevocal"):
	"""
		Create and manage private vocal channels.
	
		Require intents:
			- voice_states
		
		Require bot permission:
			- manage_channels
			- manage_permissions
			- move_members
	"""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		self.private_config = bot.config["bot"]["private_vocal"]

		self.tracker: dict[int, dict] = dict()
		self.MAIN_CHANNEL_NAME = self.private_config["main_channel_name"]
		self.CHANNEL_NAME = self.private_config["channel_name"]

	def help_custom(self) -> tuple[str, str, str]:
		emoji = '💭'
		label = "Private Vocal"
		description = "Create a private vocal channel."
		return emoji, label, description

	def __guild_in(self, member: discord.Member) -> None:
		if not member.guild.id in self.tracker: 
				self.tracker[member.guild.id] = dict()
				self.tracker[member.guild.id]["cooldown"] = dict()
				self.tracker[member.guild.id]["channels"] = dict()

	def __is_join_channel(self, channel: Union[discord.VoiceChannel, discord.StageChannel]) -> bool:
		return channel.user_limit == 1 and channel.name == self.MAIN_CHANNEL_NAME
	
	def __is_user_on_cooldown(self, user: discord.Member, guild_cooldown: dict) -> bool:
		return (user.id in guild_cooldown) and datetime.now().timestamp() - guild_cooldown[user.id].timestamp() < self.private_config["cooldown"]

	@commands.Cog.listener("on_voice_state_update")
	async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
		self.__guild_in(member)
		guild_id = self.tracker[member.guild.id]
		guild_cooldown = guild_id["cooldown"]
		guild_channels = guild_id["channels"]

		if after.channel is not None and self.__is_join_channel(after.channel):
			if self.__is_user_on_cooldown(member, guild_cooldown):
				await member.move_to(None)
				remaining = self.private_config["cooldown"] - (datetime.now() - guild_cooldown[member.id]).total_seconds()
				await member.send(f"Sorry you're on cooldown, time remaining: `{round(remaining)}` seconds.")
			
			else:
				private_vocal = await member.guild.create_voice_channel(self.CHANNEL_NAME.format(user = member), category=after.channel.category)
				await member.move_to(private_vocal)
				guild_cooldown[member.id] = datetime.now()
				guild_channels[private_vocal.id] = member.id

		if before.channel is not None and before.channel.id in guild_channels:
			if members := before.channel.members:
				user = members[0]
				guild_channels[before.channel.id] = user.id
				await before.channel.edit(name=self.CHANNEL_NAME.format(user = user))
			
			else:
				del guild_id["channels"][before.channel.id]
				await before.channel.delete()



async def setup(bot):
	await bot.add_cog(PrivateVocal(bot))