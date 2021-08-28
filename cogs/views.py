import discord

from discord.ext import commands
from views import bool
from views import dropdown
from views import link

class Views(commands.Cog, name="views"):
	"""Experimental cog, new features such buttons, dropdown or whispering"""
	def __init__(self, bot):
		self.bot = bot

	def help_custom(self):
		emoji = '🔘'
		label = "Views"
		description = "Demo : New discord features."
		return emoji, label, description

	@commands.command(name='bool')
	async def boo(self, ctx):
		"""Preview of buttons"""
		view = bool.View(flabel="Agree", slabel="Disagree", sstyle=discord.ButtonStyle.red, emojis = True, source=ctx)
		await ctx.send("Buttons demo right there !", view=view)

	@commands.command(name='dropdown')
	async def dro(self, ctx):
		"""Preview of the Dropdown menu"""
		options = [
			{'label':"Mandarin", 'description':"你好", 'emoji':"🇨🇳"},
			{'label':"Spanish", 'description':"Buenos dias", 'emoji':"🇪🇸"},
			{'label':"English", 'description':"Hello", 'emoji':"🇬🇧"},
			{'label':"Hindi", 'description':"नमस्ते", 'emoji':"🇮🇳"},
			{'label':"Arabic", 'description':"صباح الخير", 'emoji':"🇸🇦"},
			{'label':"Potuguese", 'description':"Olá", 'emoji':"🇵🇹"},
			{'label':"Bengali", 'description':"হ্যালো", 'emoji':"🇧🇩"},
			{'label':"Russian", 'description':"Привет", 'emoji':"🇷🇺"},
			{'label':"Japanese", 'description':"こんにちは", 'emoji':"🇯🇵"},
			{'label':"Turkish", 'description':"Merhaba", 'emoji':"🇹🇷"},
			{'label':"Korean", 'description':"안녕하십니까", 'emoji':"🇰🇷"},
			{'label':"French", 'description':"Bonjour", 'emoji':"🇫🇷"},
			{'label':"German", 'description':"Hallo", 'emoji':"🇩🇪"},
			{'label':"Vietnamese", 'description':"xin chào", 'emoji':"🇻🇳"},
			{'label':"Italian", 'description':"Buongiorno", 'emoji':"🇮🇹"},
			{'label':"Polish", 'description':"dzień dobry", 'emoji':"🇵🇱"},
			{'label':"Romanian", 'description':"Buna ziua", 'emoji':"🇷🇴"},
			{'label':"Dutch", 'description':"Hallo", 'emoji':"🇳🇱"},
			{'label':"Thai", 'description':"สวัสดี", 'emoji':"🇹🇭"},
			{'label':"Nepali", 'description':"नमस्कार", 'emoji':"🇳🇵"},
			{'label':"Greek", 'description':"γεια σας", 'emoji':"🇬🇷"},
			{'label':"Czech", 'description':"Ahoj", 'emoji':"🇨🇿"},
			{'label':"Persian", 'description':"سلام", 'emoji':"🇮🇷"}
		]
		view = dropdown.View(options=options, placeholder="Select your language(s)", min_val=1, max_val=9, source=ctx)
		await ctx.send("Dropdown demo right there !", view=view)

	@commands.command(name='link')
	async def lin(self, ctx):
		"""Preview of link button"""
		view = link.View(label="Source code on Github", url="https://github.com/PaulMarisOUMary/Algosup-Discord")
		await ctx.send("Find out what is behind Algobot !", view=view)

def setup(bot):
	bot.add_cog(Views(bot))