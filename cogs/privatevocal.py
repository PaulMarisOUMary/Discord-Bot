import discord

from datetime import datetime
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
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
		
		self.subconfig_data: dict = self.bot.config["cogs"][self.__cog_name__.lower()]

		self.tracker: dict[int, dict] = dict()
		self.MAIN_CHANNEL_NAME = self.subconfig_data["main_channel_name"]
		self.CHANNEL_NAME = self.subconfig_data["channel_name"]

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

	def __is_private_vocal(self, channel: discord.VoiceChannel, guild_channels: dict[int, int]) -> bool:
		return channel.id in guild_channels

	def __is_join_channel(self, channel: Union[discord.VoiceChannel, discord.StageChannel]) -> bool:
		return channel.user_limit == 1 and channel.name == self.MAIN_CHANNEL_NAME
	
	def __is_user_on_cooldown(self, user: discord.Member, guild_cooldown: dict) -> bool:
		return (user.id in guild_cooldown) and datetime.now().timestamp() - guild_cooldown[user.id].timestamp() < self.subconfig_data["cooldown"]

	@commands.Cog.listener("on_voice_state_update")
	async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
		self.__guild_in(member)
		guild_id = self.tracker[member.guild.id]
		guild_cooldown = guild_id["cooldown"]
		guild_channels = guild_id["channels"]

		if after.channel is not None and self.__is_join_channel(after.channel):
			if self.__is_user_on_cooldown(member, guild_cooldown):
				await member.move_to(None)
				remaining = self.subconfig_data["cooldown"] - (datetime.now() - guild_cooldown[member.id]).total_seconds()
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

	@commands.hybrid_command(name="userlimit", description="Limit the number of user(s) in your private channel.")
	@commands.cooldown(1, 10, commands.BucketType.user)
	@commands.bot_has_permissions(send_messages=True)
	@app_commands.choices(limit=[Choice(name=str(i), value=i) for i in range(1, 26)])
	@app_commands.describe(limit="The number of max user(s) in your private channel.")
	async def lock_private_vocal(self, ctx: commands.Context, limit: int = None):
		"""Limit the number of user(s) in your private channel."""
		voice = ctx.author.voice
		if not voice:
			await ctx.send("You're not in a voice channel.", ephemeral=True)
			return
		elif not self.__is_private_vocal(voice.channel, self.tracker[ctx.guild.id]["channels"]):
			await ctx.send("You're not in a private vocal channel.", ephemeral=True)
			return
		
		if not limit or limit < 1 or limit > 99:
			limit = len(voice.channel.members)

		await voice.channel.edit(user_limit=limit)
		await ctx.send(f"Vocal user-limit set to `{limit}`.", ephemeral=True)



async def setup(bot):
	await bot.add_cog(PrivateVocal(bot))