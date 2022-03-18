import discord
import requests
import re

from datetime import datetime
from discord.ext import commands
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageSequence

class Croissants(commands.Cog, name="croissants", command_attrs=dict(hidden=True)):
	"""Don't leave your computer unlocked!"""
	def __init__(self, bot):
		self.bot = bot

		self.EMOJI = '🥐'
		self.REGEX = re.compile("^(J[e']? ?pa[iy]e? ?(les)? ?(crois|🥐))", re.IGNORECASE)

		self.cooldown : dict = {} #{key=user_id : value=datetime}

		self.croissants_data = self.bot.database_data["croissants"]

	def help_custom(self):
		emoji = self.EMOJI
		label = "Croissants"
		description = "For when someone left their computer unlocked."
		return emoji, label, description

	@commands.Cog.listener("on_message")
	async def on_receive_message(self, message : discord.Message):
		if not message.author.bot and self.REGEX.match(message.content):
			if not self.__is_on_cooldown(message.author):
				self.cooldown[message.author.id] = datetime.now()
				await self.__send_croissants(message)
			else: await message.channel.send(f"{self.EMOJI} Respect the croissants don't despise them! ||No spam||")

	@commands.command(name="croissants", aliases=["rankcroissants", "croissantsrank", "rc"])
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def croissants_rank(self, ctx):
		"""Get the global croissants rank."""
		response = await self.bot.database.select(self.croissants_data["table"], "*", order="user_count DESC", limit=10)
		
		embed = discord.Embed(title=f"🏆 Croissants rank {self.EMOJI}", color=0xD3A779)
		for rank, data in enumerate(response, start=1):
			user_id, user_count = data
			embed.add_field(name=f"Top {self.__rank_emoji(rank)} `{user_count} {self.EMOJI}`", value=f"<@{user_id}>", inline=rank <= 3)

		await ctx.send(embed=embed)

	async def __send_croissants(self, message) -> None:
		answer_message = await message.reply(
			content=f"{message.author.mention} took out the credit card! {self.EMOJI}",
			file=self.__get_screenshot(message.author, message.content)
		)

		count = await self.__increment_croissants_counter(message.author.id)
		await answer_message.edit(content=f"{message.author.mention} took out the credit card ! And this is the `{count}` time, he's so generous! {self.EMOJI}")

	async def __increment_croissants_counter(self, user_id : int) -> int:
		exist = await self.bot.database.exist(self.croissants_data["table"], "*", f"user_id={user_id}")
		if exist:
			response = await self.bot.database.select(self.croissants_data["table"], "user_count", f"user_id={user_id}")
			count = response[0][0] + 1
			await self.bot.database.update(self.croissants_data["table"], "user_count", count, f"user_id={user_id}")
			return count
		else:
			await self.bot.database.insert(self.croissants_data["table"], {"user_id": user_id, "user_count": 1})
			return 1

	def __get_screenshot(self, author : discord.Member, content : str) -> discord.File:
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
			try: duration_array.append(frame.info["duration"])
			except: duration_array.append(0)

			img = Image.new("RGBA", size=(500, 100), color=bg_color)
			resized_pfp = frame.resize(pfp_size)
			pfp = resized_pfp.convert("RGBA")

			mask = Image.new("L", pfp_size, 0)
			ImageDraw.Draw(mask).ellipse((0, 0) + pfp_size, fill=255)
			pfp.putalpha(mask)
			img.paste(pfp, (16, 16), pfp)

			draw = ImageDraw.Draw(img)
			draw.text((100, 15), author.display_name, name_color, name_font)
			offset = draw.textsize(author.display_name, name_font)[0] + 110
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

	def __is_on_cooldown(self, user) -> bool:
		return user.id in self.cooldown and datetime.now().timestamp() - self.cooldown[user.id].timestamp() < self.bot.database_data["croissants"]["cooldown"]

	def __rank_emoji(self, rank):
		if rank == 1:
			return '🥇'
		elif rank == 2:
			return '🥈'
		elif rank == 3:
			return '🥉'
		else:
			return rank

def setup(bot):
	bot.add_cog(Croissants(bot))
