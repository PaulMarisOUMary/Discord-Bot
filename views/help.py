import discord
from discord import interactions

class Dropdown(discord.ui.Select):
	def __init__(self, bot, ctx, homeembed):
		self.bot = bot
		self.ctx = ctx
		self.home = homeembed
		self.invoker = ctx.author

		options = []
		options.append(discord.SelectOption(label="Home", description="Show the home page.", emoji='👋'))
		cogs = []
		for cog in self.bot.extensions:
			cogs.append(cog)
		for cog in cogs:
			norm_cog = self.bot.get_cog(cog[5:len(cog)])
			if "help_custom" in dir(norm_cog):
				emoji, label, description = norm_cog.help_custom()
				options.append(discord.SelectOption(label=label, description=description, emoji=emoji))

		super().__init__(placeholder='Select a category...', min_values=1, max_values=1, options=options)

	async def callback(self, interaction: discord.Interaction):
		if self.invoker == interaction.user:
			if not self.values[0].lower() == "home":
				cog = self.bot.cogs[self.values[0].lower().replace(' ', '')]
				embed = discord.Embed(title = "Help · "+str(self.values[0]),description='`'+str(cog.__doc__)+'`', url='https://github.com/PaulMarisOUMary/Algosup-Discord')
				embed.set_footer(text="Remind : Hooks such as <> must not be used when executing commands.", icon_url=self.ctx.message.author.display_avatar.url)

				for command in cog.get_commands():
					params = ""
					for param in command.clean_params: params += " <"+str(param)+">"
					embed.add_field(name=str(command.name)+str(params), value=str(command.help)+"\n\u200b", inline=False)
			else:
				embed = self.home

			await interaction.response.edit_message(embed=embed, view=self.view)
		else:
			await interaction.response.send_message("❌ Hey it's not your session !", ephemeral=True)

class Buttons(discord.ui.Button):
	def __init__(self, command, ctx, label : str, style : discord.ButtonStyle):
		super().__init__(label=label, style=style)
		self.command = command
		self.invoker = ctx.author

	async def callback(self, interaction: discord.Interaction):
		if self.invoker == interaction.user:
			await self.command(self, interaction)
		else:
			await interaction.response.send_message("❌ Hey it's not your session !", ephemeral=True)

class View(discord.ui.View):
	def __init__(self, bot : discord.ext.commands.bot.Bot, ctx : discord.ext.commands.context.Context, homeembed : discord.embeds.Embed):
		super().__init__()
		self.ctx = ctx
		self.index = 0
		self.add_item(Dropdown(bot = bot, ctx = ctx, homeembed = homeembed))
		buttons = [
			# {"label": "<<", "style": discord.ButtonStyle.grey, "command": self.toggle},
			# {"label": "Back", "style": discord.ButtonStyle.blurple, "command": self.toggle},
			{"label": "Next", "style": discord.ButtonStyle.blurple, "command": self.to_page},
			# {"label": ">>", "style": discord.ButtonStyle.grey, "command": self.toggle},
			{"label": "Quit", "style": discord.ButtonStyle.red, "command": self.quit}
		]
		for button in buttons:
			self.add_item(Buttons(label = button['label'], style = button['style'], command = button['command'], ctx = ctx))

	async def quit(self, button : discord.ui.Button, interaction : discord.Interaction):
		await interaction.response.defer()
		await interaction.delete_original_message()
		await self.ctx.message.add_reaction("<a:checkmark_a:842800730049871892>")

	async def toggle(self, button : discord.ui.Button, interaction : discord.Interaction):
		button.disabled = not button.disabled
		await interaction.response.edit_message(view=self)

		return button.disabled

	async def to_page(self, button : discord.ui.Button, interaction : discord.Interaction):
		self.index += 1
		await self.toggle(button, interaction)
		await self.ctx.send("Psst.. Work in progress :wink:")