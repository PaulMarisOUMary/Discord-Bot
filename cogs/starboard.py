import discord

from typing import Optional

from discord.ext import commands
from discord import app_commands

from classes.discordbot import DiscordBot

@app_commands.guild_only()
class Starboard(commands.Cog, name="starboard"):
	"""
		Starboard.
		
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

	def help_custom(self) -> tuple[str, str, str]:
		emoji = '⭐'
		label = "Starboard"
		description = "Allows users to star messages."
		return emoji, label, description

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
			images = [attachment.url for attachment in message.attachments if attachment.url.lower().endswith(("png", "jpg", "jpeg", "gif", "webp"))]
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

	async def __get_display_message(self, message: discord.Message) -> Optional[discord.Message]:
		response = await self.bot.database.lookup(self.subconfig_data["table"], "display_message", {"reference_message": message.jump_url})
		if not response:
			return
		_, channel_id, display_id = response[0][0].split('/')[-3:]

		display_channel = message.guild.get_channel(int(channel_id))
		if not display_channel:
			await self.bot.database.delete(self.subconfig_data["table"], f"display_message = {response[0][0]}")
			return

		display_message = await display_channel.fetch_message(int(display_id))
		return display_message

	@commands.Cog.listener("on_reaction_add")
	async def on_reaction_add(self, reaction: discord.Reaction, _: discord.User):
		if not reaction.emoji == self.star_emoji:
			return

		message = reaction.message

		starboard_channel = None
		for text_channel in message.guild.text_channels:
			if "starboard" in text_channel.name:
				starboard_channel = text_channel
				break

		if not starboard_channel:
			return

		n_star = reaction.count

		if n_star == 1:
			embeds = self.__get_starboard_embeds(message, n_star)
			display_message = await starboard_channel.send(content=f"{self.star_emoji} **{n_star}** {message.channel.mention} ID: {message.id}", embeds=embeds)
			await self.bot.database.insert(self.subconfig_data["table"], {"reference_message": message.jump_url, "display_message": display_message.jump_url, "star_count": n_star})
		else:
			display_message = await self.__get_display_message(message)
			if not display_message:
				return

			await display_message.edit(content=f"{self.star_emoji} **{n_star}** {message.channel.mention} ID: {message.id}", embeds=display_message.embeds)

			await self.bot.database.update(self.subconfig_data["table"], {"star_count": n_star}, f"display_message = '{display_message.jump_url}'")

	@commands.Cog.listener("on_reaction_remove")
	async def on_reaction_remove(self , reaction: discord.Reaction, _: discord.User):
		if not reaction.emoji == self.star_emoji:
			return

		display_message = await self.__get_display_message(reaction.message)
		if not display_message:
			return

		if reaction.count == 0:
			await display_message.delete()
			await self.bot.database.delete(self.subconfig_data["table"], f"display_message = '{display_message.jump_url}'")
		else:
			message = reaction.message
			await display_message.edit(content=f"{self.star_emoji} **{reaction.count}** {message.channel.mention} ID: {message.id}", embeds=display_message.embeds)
			await self.bot.database.update(self.subconfig_data["table"], {"star_count": reaction.count}, f"display_message = '{display_message.jump_url}'")

	@commands.Cog.listener("on_message_delete")
	async def on_message_delete(self , message: discord.Message):
		if not self.star_emoji in [reaction.emoji for reaction in message.reactions]:
			return

		display_message = await self.__get_display_message(message)

		if not display_message:
			return

		await display_message.delete()
		await self.bot.database.delete(self.subconfig_data["table"], f"display_message = '{display_message.jump_url}'")


async def setup(bot: DiscordBot):
	await bot.add_cog(Starboard(bot))
