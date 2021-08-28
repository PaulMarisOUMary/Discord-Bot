import discord
import functools

class Dropdown(discord.ui.Select):
	def __init__(self, bot, ctx, homeembed, options):
		self.bot = bot
		self.ctx = ctx
		self.home = homeembed
		self.invoker = ctx.author

		super().__init__(placeholder='Select a category...', min_values=1, max_values=1, options=options)

	async def callback(self, interaction: discord.Interaction):
		if self.invoker == interaction.user:
			if not self.values[0].lower() == "home":
				cog = self.bot.cogs[self.values[0].lower().replace(' ', '')]
				embed = self.view.gen_embed(cog, self.values[0])
			else:
				embed = self.home

			await interaction.response.edit_message(embed=embed, view=self.view)
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
				func = functools.partial(self.command, self.args, self, interaction)
				await func()
			else:
				await self.command(self, interaction)
		else:
			await interaction.response.send_message("❌ Hey it's not your session !", ephemeral=True)

class View(discord.ui.View):
	def __init__(self, bot : discord.ext.commands.bot.Bot, ctx : discord.ext.commands.context.Context, homeembed : discord.embeds.Embed):
		super().__init__()
		self.ctx = ctx
		self.bot = bot
		self.home = homeembed
		self.index = 0
		
		self.options = self.add_dropdown()
		self.add_buttons()

	def add_dropdown(self):
		options = []
		options.append(discord.SelectOption(label="Home", description="Show the home page.", emoji='👋'))
		for cog in self.get_cogs():
			if "help_custom" in dir(cog):
				emoji, label, description = cog.help_custom()
				options.append(discord.SelectOption(label=label, description=description, emoji=emoji))
		self.add_item(Dropdown(bot = self.bot, ctx = self.ctx, homeembed = self.home, options = options))
		return options

	def add_buttons(self):
		self.startB = Buttons(label="<<", style=discord.ButtonStyle.grey, command=self.set_page, args=0, ctx = self.ctx)
		self.backB = Buttons(label="Back", style=discord.ButtonStyle.blurple, command=self.to_page, args=-1, ctx = self.ctx)
		self.nextB = Buttons(label="Next", style=discord.ButtonStyle.blurple, command=self.to_page, args=+1, ctx = self.ctx)
		self.endB = Buttons(label=">>", style=discord.ButtonStyle.grey, command=self.set_page, args=len(self.options)-1, ctx = self.ctx)
		self.quitB = Buttons(label="Quit", style=discord.ButtonStyle.red, command=self.quit, ctx = self.ctx)
		
		for button in [self.startB, self.backB, self.nextB, self.endB, self.quitB]: self.add_item(button)

	def get_cogs(self):
		cogs = []
		for cog in self.bot.extensions:
			cogs.append(self.bot.get_cog(cog[5:len(cog)]))
		return cogs

	def gen_embed(self, cog, name):
		emoji, label, description = cog.help_custom()
		embed = discord.Embed(title = str(emoji)+" Help · "+str(name),description='`'+str(cog.__doc__)+'`', url='https://github.com/PaulMarisOUMary/Algosup-Discord')
		embed.set_footer(text="Remind : Hooks such as <> must not be used when executing commands.", icon_url=self.ctx.message.author.display_avatar.url)

		for command in cog.get_commands():
			params = ""
			for param in command.clean_params: params += " <"+str(param)+">"
			embed.add_field(name=str(command.name)+str(params), value=str(command.help)+"\n\u200b", inline=False)
		return embed

	async def quit(self, button : discord.ui.Button, interaction : discord.Interaction):
		await interaction.response.defer()
		await interaction.delete_original_message()
		await self.ctx.message.add_reaction("<a:checkmark_a:842800730049871892>")

	async def toggle(self, button : discord.ui.Button, interaction : discord.Interaction):
		button.disabled = not button.disabled
		await interaction.response.edit_message(view=self)

		return button.disabled

	async def to_page(self, page : int, button : discord.ui.Button, interaction : discord.Interaction):
		if not self.index + page < 0 or not self.index + page > len(self.options):
			self.set_index(page)

			if self.index > 0: embed = self.gen_embed(cog=self.bot.cogs[self.options[self.index].label.lower().replace(' ', '')], name=self.options[self.index].label)
			else: embed = self.home

			await interaction.response.edit_message(embed=embed, view=self)

	async def set_page(self, page : int, button : discord.ui.Button, interaction : discord.Interaction):
		self.index = page
		await self.to_page(0, button, interaction)

	def set_index(self, page):
		self.index += page
		self.backB.disabled = False
		self.nextB.disabled = False
		self.startB.disabled = False
		self.endB.disabled = False
		if self.index == 0: 
			self.backB.disabled = True
			self.startB.disabled = True
		elif self.index == len(self.options)-1: 
			self.nextB.disabled = True
			self.endB.disabled = True