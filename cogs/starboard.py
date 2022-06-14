import discord

from discord.ext import commands
from discord import app_commands
from classes.discordbot import DiscordBot


@app_commands.guild_only()
class Starboard(commands.Cog, name="starboard"):
	"""
		stars commands.
		
		Require intents: 
			- Intents.reactions
		
		Require bot permission:
			- send_messages
			- view_channel
	"""
	def __init__(self, bot: DiscordBot) -> None:
		self.bot = bot

		self.subconfig_data: dict = self.bot.config["cogs"][self.__cog_name__.lower()]

		self.star_emoji = '⭐'
		self.stars: list = ['⭐', '💫', '✨']

	def help_custom(self) -> tuple[str, str, str]:
		emoji = '⭐'
		label = "Starboard"
		description = "Allows users to star messages."
		return emoji, label, description

	@commands.Cog.listener("on_reaction_add")
	async def on_reaction_add(self, reaction: discord.Reaction, _: discord.User):
		if reaction.emoji == self.star_emoji:
			message = await reaction.message.channel.fetch_message(reaction.message.id)

			embed = discord.Embed(description=message.content, color=0x00ff00)
			embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
			embed.add_field(name="Original", value=f"[Jump !]({message.jump_url})")
			embed.timestamp = message.created_at

			if message.attachments:
				file = message.attachments[0]
				spoiler = file.is_spoiler()
				if file.url.lower().endswith(("png", "jpg", "jpeg", "gif", "webp")):
					embed.set_image(url=file.url)
				elif spoiler:
					embed.add_field(name="Attachment", value=f"||[{file.filename}]({file.url})||", inline=False)
				else:
					embed.add_field(name="Attachment", value=f"[{file.filename}]({file.url})", inline=False)

			ref = message.reference
			if ref and isinstance(ref.resolved, discord.Message):
				embed.add_field(name="Replying to...", value=f"[{ref.resolved.author}]({ref.resolved.jump_url})", inline=False)

			guild = reaction.message.guild
			star_count = reaction.emoji.count(self.star_emoji)
			channel_name = "starboard"
			for i in enumerate(guild.text_channels):
				if i[1].name.lower() == channel_name:
					channel = i[1]
					break
			await channel.send(content=f"{self.star_emoji} **{star_count}** {message.channel.mention} ID: {message.id}", embed=embed)
			reference_message = message.id
			display_message = channel.last_message.id

			await self.bot.database.insert_onduplicate(self.subconfig_data["table"], {"reference_message": reference_message, "display_message": display_message, "star_count": star_count})

	# @commands.Cog.listener("on_reaction_remove")
	# async def on_raw_reaction_remove(self , reaction: discord.RawReactionActionEvent):
	# 	guild = self.bot.get_guild(message.guild.id)
	# 	if guild:
	# 		channel = guild.get_channel(984100935649345606)
	# 		display_message = channel.last_message.id
	# 	await display_message.delete()
	# 	await self.bot.database.delete(self.subconfig_data["table"], {"display_message": display_message})

	@commands.Cog.listener("on_message_delete")
	async def on_raw_message_delete(self , message: discord.Message):
		guild = self.bot.get_guild(953311718275153941)
		if guild:
			channel = guild.get_channel(984100935649345606)
			display_message = channel.last_message
		await self.bot.database.delete(self.subconfig_data["table"], f"display_message = {display_message.id}")
		await channel.delete_messages([display_message])


async def setup(bot: DiscordBot):
	await bot.add_cog(Starboard(bot))
