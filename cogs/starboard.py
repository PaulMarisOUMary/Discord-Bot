import discord

from math import log
from typing import Optional

from discord.ext import commands

from utils.basebot import DiscordBot


@commands.guild_only()
class Starboard(commands.Cog, name="starboard"):
	"""
		Starboard.
		
		Require intents: 
			- Intents.messages
			- Intents.reactions
		
		Require bot permission:
			- send_messages
			- view_channel
	"""
	def __init__(self, bot: DiscordBot) -> None:
		self.bot = bot

		self.subconfig_data: dict = self.bot.config["cogs"][self.__cog_name__.lower()]

		self.star_emoji = '⭐'
		self.stars_emojis = ['⭐', '🌟', '✨', '💫', '☄️', '🎇', '🎆', '🌠', '💖', '🪄']

	def help_custom(self) -> tuple[str, str, str]:
		emoji = '⭐'
		label = "Starboard"
		description = "Allows users to star messages."
		return emoji, label, description

	def __star_emoji_upgrade(self, stars: int) -> Optional[str]:
		if not stars == 0:
			index = round(log(stars))
			return self.stars_emojis[index]
		return None

	def __star_gradient_colour(self, stars: int) -> int:
		p = stars / 13
		if p > 1.0:
			p = 1.0

		red = 255
		green = int((194 * p) + (253 * (1 - p)))
		blue = int((12 * p) + (247 * (1 - p)))
		return (red << 16) + (green << 8) + blue

	def __get_starboard_embeds(self, message: discord.Message, n_star: int) -> list[discord.Embed]:
		embed = discord.Embed(description=message.content, color=self.__star_gradient_colour(n_star), timestamp=message.created_at, url="https://youtu.be/L_jWHffIx5E?t=36")
		embeds = [embed]
		embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
		embed.add_field(name="Original", value=f"[Jump !]({message.jump_url})")

		reference = message.reference
		if reference and isinstance(reference.resolved, discord.Message):
			embed.add_field(name="Replying to...", value=f"[{reference.resolved.author}]({reference.resolved.jump_url})", inline=False)

		if message.attachments:
			images = [attachment.url for attachment in message.attachments if attachment.url.lower().endswith(("jpg", "jpeg", "png", "webp", "gif"))] # doc: https://discord.com/developers/docs/reference#editing-message-attachments-using-attachments-within-embeds
			for image_url in images:
				if not embed.image.url:
					embed.set_image(url=image_url)
				else:
					embeds.append(discord.Embed(url="https://youtu.be/L_jWHffIx5E?t=36").set_image(url=image_url))

		if message.stickers:
			for image_sticker in [sticker for sticker in message.stickers if sticker.format == discord.StickerFormatType.png or sticker.format == discord.StickerFormatType.apng]:
				if not embed.image.url:
					embed.set_image(url=image_sticker.url)
				else:
					embeds.append(discord.Embed(url="https://youtu.be/L_jWHffIx5E?t=36").set_image(url=image_sticker.url))

		return embeds

	async def __get_display_message(self, jump_url: str) -> Optional[discord.Message]:
		response = await self.bot.database.lookup(self.subconfig_data["table"], "display_message", {"reference_message": jump_url})
		if not response:
			return
		guild_id, channel_id, display_id = response[0][0].split('/')[-3:]

		channel = self.bot.get_guild(int(guild_id))
		display_channel = channel.get_channel(int(channel_id)) if channel else None
		if not display_channel:
			await self.bot.database.delete(self.subconfig_data["table"], f"display_message = {response[0][0]}")
			return

		if not isinstance(display_channel, discord.TextChannel):
			return None

		return await display_channel.fetch_message(int(display_id))

	async def __get_message_from_payload(self, payload: discord.RawReactionActionEvent) -> tuple[Optional[discord.Message], Optional[discord.Reaction]]:
		potential_message = [message for message in self.bot.cached_messages if message.id == payload.message_id]
		cached_message = potential_message[0] if len(potential_message) > 0 else None

		if cached_message:
			message = cached_message
		else:
			channel = self.bot.get_channel(payload.channel_id)
			if not channel or not isinstance(channel, discord.TextChannel):
				return None, None
			message = await channel.fetch_message(payload.message_id)

		try:
			reaction = [reaction for reaction in message.reactions if reaction.emoji == self.star_emoji][0]
		except IndexError:
			reaction = None

		return message, reaction

	@commands.Cog.listener("on_raw_reaction_add")
	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
		try:
			if str(payload.emoji) != self.star_emoji:
				return

			message, reaction = await self.__get_message_from_payload(payload)

			if not reaction or not message or not message.guild: # not a self.star_emoji
				return

			starboard_channel = None
			for text_channel in message.guild.text_channels:
				if "starboard" in text_channel.name:
					starboard_channel = text_channel
					break

			if not starboard_channel:
				return

			if starboard_channel.id == payload.channel_id:
				return

			if not isinstance(message.channel, discord.TextChannel):
				return

			n_star = reaction.count
			star_emoji =  self.__star_emoji_upgrade(n_star)

			if n_star == 1:
				embeds = self.__get_starboard_embeds(message, n_star)
				display_message = await starboard_channel.send(content=f"{star_emoji} **{n_star}** {message.channel.mention} ID: {message.id}", embeds=embeds)
				await self.bot.database.insert(self.subconfig_data["table"], {"reference_message": message.jump_url, "display_message": display_message.jump_url, "star_count": n_star})
			else:
				display_message = await self.__get_display_message(message.jump_url)
				if not display_message:
					return

				await display_message.edit(content=f"{star_emoji} **{n_star}** {message.channel.mention} ID: {message.id}", embeds=display_message.embeds)

				await self.bot.database.update(self.subconfig_data["table"], {"star_count": n_star}, f"display_message = '{display_message.jump_url}'")
		except discord.Forbidden or discord.NotFound:
			pass

	@commands.Cog.listener("on_raw_reaction_remove")
	async def on_raw_reaction_remove(self , payload: discord.RawReactionActionEvent) -> None:
		try:
			message, reaction = await self.__get_message_from_payload(payload)

			if not message:
				return

			if not isinstance(message.channel, discord.TextChannel):
				return

			if not reaction:
				n_star = 0
			else:
				n_star = reaction.count

			star_emoji =  self.__star_emoji_upgrade(n_star)

			display_message = await self.__get_display_message(message.jump_url)
			if not display_message:
				return

			if not reaction:
				await self.bot.database.delete(self.subconfig_data["table"], f"display_message = '{display_message.jump_url}'")
				await display_message.delete()
			else:
				await display_message.edit(content=f"{star_emoji} **{n_star}** {message.channel.mention} ID: {message.id}", embeds=display_message.embeds)
				await self.bot.database.update(self.subconfig_data["table"], {"star_count": reaction.count}, f"display_message = '{display_message.jump_url}'")
		except discord.Forbidden or discord.NotFound:
			pass

	@commands.Cog.listener("on_raw_message_delete")
	async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent) -> None:
		try:
			jump_url = f"https://discord.com/channels/{payload.guild_id}/{payload.channel_id}/{payload.message_id}"

			response = await self.bot.database.lookup(self.subconfig_data["table"], "display_message", {"reference_message": jump_url})

			if not response:
				return

			display_message = await self.__get_display_message(jump_url)

			if not display_message:
				return

			await self.bot.database.delete(self.subconfig_data["table"], f"display_message = '{display_message.jump_url}'")
			await display_message.delete()
		except discord.Forbidden or discord.NotFound:
			pass


async def setup(bot: DiscordBot) -> None:
	await bot.add_cog(Starboard(bot))