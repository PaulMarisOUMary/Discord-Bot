import discord
import functools

from discord.ext import commands
from views.view import View as Parent

class Dropdown(discord.ui.Select):
	def __init__(self, ctx, options):
		super().__init__(placeholder="Select a category...", min_values=1, max_values=1, options=options)
		self.invoker = ctx.author

	async def callback(self, interaction: discord.Interaction):
		if self.invoker == interaction.user:
			index = self.view.find_index_from_select(self.values[0])
			if not index: index = 0
			await self.view.set_page(index, interaction)
		else:
			await interaction.response.send_message("❌ Hey it's not your session !", ephemeral=True)

class Buttons(discord.ui.Button):
	def __init__(self, command, ctx, label : str, style : discord.ButtonStyle, args=None):
		disable = False
		if args == -1 or args == 0: disable = True
		super().__init__(label=label, style=style, disabled=disable)
		self.command = command
		self.invoker = ctx.author
		self.args = args

	async def callback(self, interaction: discord.Interaction):
		if self.invoker == interaction.user:
			if self.args or self.args == 0:
				func = functools.partial(self.command, self.args, interaction)
				await func()
			else:
				await self.command(interaction)
		else:
			await interaction.response.send_message("❌ Hey it's not your session !", ephemeral=True)

class View(Parent):
	def __init__(self, mapping: dict, ctx: commands.Context, homeembed: discord.embeds.Embed, ui: int):
		super().__init__()
		self.mapping, self.ctx, self.home = mapping, ctx, homeembed
		self.index, self.buttons = 0, None

		self.options, self.embeds = self.gen_embeds()
		
		if ui == 0: self.add_item(Dropdown(ctx = self.ctx, options = self.options))
		elif ui == 1: self.buttons = self.add_buttons()
		else: 
			self.add_item(Dropdown(ctx = self.ctx, options = self.options))
			self.buttons = self.add_buttons()

	def add_buttons(self):
		self.startB = Buttons(label="<<", style=discord.ButtonStyle.grey, command=self.set_page, args=0, ctx = self.ctx)
		self.backB = Buttons(label="Back", style=discord.ButtonStyle.blurple, command=self.to_page, args=-1, ctx = self.ctx)
		self.nextB = Buttons(label="Next", style=discord.ButtonStyle.blurple, command=self.to_page, args=+1, ctx = self.ctx)
		self.endB = Buttons(label=">>", style=discord.ButtonStyle.grey, command=self.set_page, args=len(self.options)-1, ctx = self.ctx)
		self.quitB = Buttons(label="Quit", style=discord.ButtonStyle.red, command=self.quit, ctx = self.ctx)
		buttons = [self.startB, self.backB, self.nextB, self.endB, self.quitB]
		for button in buttons: self.add_item(button)
		return buttons

	def find_index_from_select(self, value):
		i = 0
		for cog in self.get_cogs():
			if "help_custom" in dir(cog):
				_, label, _ = cog.help_custom()
				if label == value: return i+1
				i += 1

	def get_cogs(self):
		cogs = []
		for cog in self.mapping.keys():
			cogs.append(cog)
		return cogs

	def gen_embeds(self):
		options, embeds = [], []
		options.append(discord.SelectOption(label="Home", description="Show the home page.", emoji='👋'))
		embeds.append(self.home)
		for cog in self.get_cogs():
			if "help_custom" in dir(cog):
				emoji, label, description = cog.help_custom()
				options.append(discord.SelectOption(label=label, description=description, emoji=emoji))
				embed = discord.Embed(title = f"{emoji} Help · {label}", description=f"{cog.__doc__.lstrip(' ')}", url="https://github.com/PaulMarisOUMary/Discord-Bot")
				embed.set_footer(text="Remind : Hooks such as <> must not be used when executing commands.", icon_url=self.ctx.message.author.display_avatar.url)

				for command in cog.get_commands():
					params = ""
					for param in command.clean_params: params += f" <{param}>"
					embed.add_field(name=f"{command.name}{params}", value=f"{command.help}\n\u200b", inline=False)
				embeds.append(embed)
		return options, embeds

	async def quit(self, interaction : discord.Interaction):
		await interaction.response.defer()
		await interaction.delete_original_response()
		await self.ctx.message.add_reaction("<a:checkmark_a:842800730049871892>")

	async def to_page(self, page : int, interaction : discord.Interaction):
		if not self.index + page < 0 or not self.index + page > len(self.options):
			await self.set_index(page)
			embed = self.embeds[self.index]

			await interaction.response.edit_message(embed=embed, view=self)

	async def set_page(self, page : int, interaction : discord.Interaction):
		self.index = page
		await self.to_page(0, interaction)

	async def set_index(self, page):
		self.index += page
		if self.buttons:
			for button in self.buttons[0:-1]:
				button.disabled = False
			if self.index == 0: 
				self.backB.disabled = True
				self.startB.disabled = True
			elif self.index == len(self.options)-1: 
				self.nextB.disabled = True
				self.endB.disabled = True