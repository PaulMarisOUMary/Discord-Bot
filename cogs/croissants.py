import discord
import re
import requests

from datetime import datetime
from discord.ext import commands
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

class Croissants(commands.Cog, name="croissants", command_attrs=dict(hidden=True)):
	"""Don't leave your computer unlocked!"""

	EMOJI = '🥐'
	REGEX = re.compile("^(J[e']? ?pa[iy]e ?les ?(crois|🥐))|^🥐", re.IGNORECASE)

	def __init__(self, bot):
		self.bot = bot

	"""def help_custom(self):
		emoji = self.emoji
		label = "Croissants"
		description = "For when someone left their computer unlocked."
		return emoji, label, description"""

	@commands.Cog.listener('on_message')
	async def on_receive_message(self, message : discord.Message):
		content = message.content
		author = message.author
		if not author.bot and self.REGEX.match(content):
			await message.reply(
				content=f'Merci pour les croissants {author.mention}! ' + self.EMOJI,
				file=self.__get_screenshot(author, content)
			)

	@commands.command(name='croissants')
	async def croissants(self, ctx : commands.context.Context):
		author = ctx.message.author
		await ctx.send(
			content=author.mention + " paye les " + self.EMOJI,
			file=self.__get_screenshot(author, ctx.message.content)
		)

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

def setup(bot):
	bot.add_cog(Croissants(bot))
