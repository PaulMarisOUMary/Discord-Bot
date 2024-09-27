import discord
import requests
import re

from datetime import datetime
from discord.ext import commands
from discord import app_commands
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageSequence
from typing import Union

from classes.database import MixedTypes
from classes.discordbot import DiscordBot

@app_commands.guild_only()
class Croissants(commands.GroupCog, name="croissants", group_name="croissants", group_description="Commands related to croissants."):
	"""
		Don't leave your computer unlocked !
		A private joke to raise awareness against the risk of leaving your PC unlocked.
		
		Require intents: 
			- message_content
		
		Require bot permission:
			- read_messages
			- send_messages
			- attach_files
	"""
	def __init__(self, bot: DiscordBot) -> None:
		self.bot = bot

		self.EMOJI = '🥐'
		self.REGEX = re.compile("^(J[e']? ?pa[iy]e? ?(les)? ?(crois|🥐))", re.IGNORECASE)

		self.cooldown : dict = {} #{key=user_id : value=datetime}

		self.subconfig_data: dict = self.bot.config["cogs"][self.__cog_name__.lower()]

	def help_custom(self) -> tuple[str, str, str]:
		emoji = self.EMOJI
		label = "Croissants"
		description = "For when someone left their computer unlocked."
		return emoji, label, description

	@commands.Cog.listener("on_message")
	async def on_receive_message(self, message: discord.Message) -> None:
		if not message.author.bot and self.REGEX.match(message.content):
			if not self.__is_on_cooldown(message.author):
				self.cooldown[message.author.id] = datetime.now()
				await self.__send_croissants(message)
			else: await message.channel.send(f"{self.EMOJI} Respect the croissants don't despise them! ||No spam||")

	@app_commands.command(name="lore", description="Explain the lore of the croissants.")
	@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
	async def croissants_lore(self, interaction: discord.Interaction) -> None:
		"""Explain the lore of the croissants."""

		embed = discord.Embed(title="Lore of Croissants", color=0xD3A779)
		embed.add_field(name=f"{self.EMOJI} When", value="Born in October 2020. During the break time.")
		embed.add_field(name=f"{self.EMOJI} Where", value="In computer science, at the school.")
		embed.add_field(name=f"{self.EMOJI} What", value="Croissants were a joke made by Franck on a student's computers.")
		embed.add_field(name=f"{self.EMOJI} Why", value="Croissants are a sweet way to give awareness for students about their individual responsibility in an IT company/organisation.\nIf you leave your computer unlocked, it means someone else could use it for malicious purposes.")
		embed.add_field(name=":arrow_right: Recap", value="Don't forget to **lock** your computer when you're not using it.\nSome company/school reset your computer when you leaves it unlocked, because it could leads to a security breach.")

		await interaction.response.send_message(embed=embed, ephemeral=True)

	@app_commands.command(name="show", description="Show how many croissants a user paid.")
	@app_commands.describe(user="The user to show the croissants of.")
	@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
	async def croissants_show(self, interaction: discord.Interaction, user: discord.Member) -> None:
		"""Show how many croissants a user paid."""
		response = await self.bot.database.lookup(self.subconfig_data["table"], "user_count", {"user_id": str(user.id)})

		if response:
			text = f"{user.mention} have `{response[0][0]}` croissants {self.EMOJI} !"
		else:
			text = f"Good job, {user.mention} have no croissants {self.EMOJI} ||[yet](<https://youtu.be/S2t59dPf9K0>)||."

		await interaction.response.send_message(content=text, ephemeral=True)

	@app_commands.command(name="rank", description="Get the global croissants rank.")
	@app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
	async def croissants_rank(self, interaction: discord.Interaction) -> None:
		"""Get the global croissants rank."""
		response = await self.bot.database.select(self.subconfig_data["table"], "*", order="user_count DESC", limit="10")
		
		embed = discord.Embed(title=f"🏆 Croissants rank {self.EMOJI}", color=0xD3A779)
		for rank, data in enumerate(response, start=1):
			user_id, user_count = data
			embed.add_field(name=f"Top {self.__rank_emoji(rank)} `{user_count} {self.EMOJI}`", value=f"<@{user_id}>", inline=rank <= 3)

		await interaction.response.send_message(embed=embed)

	async def __send_croissants(self, message: discord.Message) -> None:
		answer_message = await message.reply(
			content=f"{message.author.mention} took out the credit card! {self.EMOJI}",
			file=self.__get_screenshot(message.author, message.content)
		)

		count = await self.__increment_croissants_counter(message.author.id)
		await answer_message.edit(content=f"{message.author.mention} took out the credit card ! And this is the `{count}` time, he's so generous! {self.EMOJI}")

	async def __increment_croissants_counter(self, user_id: int) -> int:
		await self.bot.database.insert_onduplicate(self.subconfig_data["table"], {"user_id": user_id, "user_count": MixedTypes("COALESCE(user_count, 0) + 1")})

		response = await self.bot.database.lookup(self.subconfig_data["table"], "user_count", {"user_id": str(user_id)})
		return response[0][0]

	def __get_screenshot(self, author: Union[discord.User, discord.Member], content: str) -> discord.File:
		name_font = ImageFont.truetype("fonts/Whitney-Medium.ttf", 24)
		timestamp_font = ImageFont.truetype("fonts/Whitney-Medium.ttf", 18)
		content_font = ImageFont.truetype("fonts/Whitney-Book.ttf", 24)

		name_color = tuple(int(str(author.color)[i+1:i+3], 16) for i in (0, 2, 4))
		timestamp_color = (114, 118, 125)
		content_color = (220, 221, 222)
		bg_color = (54, 57, 63)
		pfp_size = (60, 60)

		pfp_content = Image.open(BytesIO(requests.get(author.display_avatar.url).content))
		images_sequence, duration_array = [], []
		for frame in ImageSequence.Iterator(pfp_content):
			try: 
				duration_array.append(frame.info["duration"])
			except: 
				duration_array.append(0)

			img = Image.new("RGBA", size=(500, 100), color=bg_color)
			resized_pfp = frame.resize(pfp_size)
			pfp = resized_pfp.convert("RGBA")

			mask = Image.new("L", pfp_size, 0)
			ImageDraw.Draw(mask).ellipse((0, 0) + pfp_size, fill=255)
			pfp.putalpha(mask)
			img.paste(pfp, (16, 16), pfp)

			draw = ImageDraw.Draw(img)
			draw.text(xy=(100, 15), text=author.display_name, fill=name_color, font=name_font) # type: ignore
			offset = draw.textlength(text=author.display_name, font=name_font) + 110
			draw.text((offset, 20), datetime.now().strftime("Today at %I:%M %p").replace(" 0", " "), timestamp_color, timestamp_font)
			draw.text((99, 48), content, content_color, content_font)

			images_sequence.append(img)

		image = images_sequence[0]
		duration_array.insert(0, duration_array[0])
		with BytesIO() as img_bin:
			image.save(img_bin, save_all=True, append_images=images_sequence, optimize=False, format="GIF", loop=0, duration= duration_array)
			img_bin.seek(0)
			file = discord.File(img_bin, "croissants.gif")
		return file

	def __is_on_cooldown(self, user: Union[discord.User, discord.Member]) -> bool:
		return user.id in self.cooldown and datetime.now().timestamp() - self.cooldown[user.id].timestamp() < self.subconfig_data["cooldown"]

	def __rank_emoji(self, rank: int) -> str:
		return {1:'🥇', 2:'🥈', 3:'🥉'}.get(rank, str(rank))



async def setup(bot: DiscordBot) -> None:
	await bot.add_cog(Croissants(bot))