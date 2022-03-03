import discord
import requests
import re

from datetime import datetime
from discord.ext import commands
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

class Croissants(commands.Cog, name="croissants", command_attrs=dict(hidden=True)):
	"""Don't leave your computer unlocked!"""
	def __init__(self, bot):
		self.bot = bot

		self.EMOJI = '🥐'
		self.REGEX = re.compile("^(J[e']? ?pa[iy]e? ?(les)? ?(crois|🥐))", re.IGNORECASE)

		self.croissants_data = self.bot.database_data["croissants"]

	def help_custom(self):
		emoji = '🥐'
		label = "Croissants"
		description = "For when someone left their computer unlocked."
		return emoji, label, description

	@commands.Cog.listener('on_message')
	async def on_receive_message(self, message : discord.Message):
		content = message.content
		author = message.author
		if not author.bot and self.REGEX.match(content):
			answer_message = await message.reply(
				content=f'{author.mention} took out the credit card! ' + self.EMOJI,
				file=self.__get_screenshot(author, content)
			)

			count = await self.__increment_croissants_counter(author.id)
			await answer_message.edit(content=f"{author.mention} took out the credit card ! And this is the `{count}` time, he's so generous! " + self.EMOJI)

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

		name_color = author.roles[-1].color.to_rgb()
		timestamp_color = (114, 118, 125)
		content_color = (220, 221, 222)
		bg_color = (54, 57, 63)

		img = Image.new("RGB", (500, 100), bg_color)
		pfp = Image.open(BytesIO(requests.get(author.display_avatar.url).content)).resize((60, 60))

		mask = Image.new('L', pfp.size, 0)
		ImageDraw.Draw(mask).ellipse((0, 0) + pfp.size, fill=255)
		pfp.putalpha(mask)
		img.paste(pfp, (16, 16), pfp)

		draw = ImageDraw.Draw(img)
		draw.text((100, 15), author.display_name, name_color, name_font)
		offset = draw.textsize(author.display_name, name_font)[0] + 110
		draw.text((offset, 20), datetime.now().strftime("Today at %I:%M %p").replace(" 0", " "), timestamp_color, timestamp_font)
		draw.text((99, 48), content, content_color, content_font)

		with BytesIO() as img_bin:
			img.save(img_bin, "PNG")
			img_bin.seek(0)
			file = discord.File(img_bin, "croissants.png")
		return file

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
