import discord
import functools

class Dropdown(discord.ui.Select):
	def __init__(self, options, source, main, embed, placeholder : str, min_val : int, max_val : int):
		self.source = source
		self.main = main
		self.invoker = source.author
		self.embed = embed

		choices = []
		for option in options:
			if not option['emoji']:
				choices.append(discord.SelectOption(label=option['label'], description=option['description']))
			else:
				choices.append(discord.SelectOption(label=option['label'], description=option['description'], emoji=option['emoji']))

		super().__init__(placeholder = placeholder, min_values = min_val, max_values = max_val, options = choices)

	async def callback(self, interaction: discord.Interaction):
		if self.invoker == interaction.user:
			if self.values[0] in ["All", "Next", "When"]:
				embed =  {"All":functools.partial(self.main.all, self.source), "Next":functools.partial(self.main.next, self.source), "When":functools.partial(self.main.when, interaction.user)}.get(self.values[0], 0)()
				await interaction.response.edit_message(embed=embed, view=self.view)
			elif self.values[0] == "Home":
				await interaction.response.edit_message(embed=self.embed, view=self.view)
			else:
				embed = discord.Embed(color=0xf7346b, title = "⚙️ Fridaycake · Can I trust you ?", description = "`The main concept of the algorithm explained.`\n\u200b", url='https://github.com/PaulMarisOUMary/Algosup-Discord')
				embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/332696002144501760/800791318200188998/fridaycake.png")
				embed.add_field(name="How do you get the list of participants ?", value=f"There is a file named `participants.dat` in the `data/` folder.\nInside I have arranged each volunteers by promotion and then by alphabetical order.\n\u200b", inline=False)
				embed.add_field(name="How am I mixed up ?", value="I'm using a __seed__ to shuffle randomly the list of participants.\nThe point is, it doesn't matter on which computer or when the calculation is performed, it always return the same result as long we doesn't change the seed (it means also you can try at home it will return exactly the same result as Algobot).\n\u200b", inline=False)
				embed.add_field(name="How can I investigate ?", value="You can simply clone the repository with git from [Algosup-Discord](https://github.com/PaulMarisOUMary/Algosup-Discord) and try these functions :\n`get_participants('data/participants.dat')`\n`mix_participants(participants, seed, n_groups)`\n\u200b", inline=False)
				embed.add_field(name="Additional informations :", value=f"Number of participants : `{self.main.nparticipants}`\nCurrent seed : `{self.main.seed}`\n\nFeel free to contact me if you have any question.\nProject open source, have a look on [Github](https://github.com/PaulMarisOUMary/Algosup-Discord) !")

				await interaction.response.edit_message(embed=embed, view=self.view)
		else:
			await interaction.response.send_message("❌ Hey it's not your session !", ephemeral=True)

class Buttons(discord.ui.Button):
	def __init__(self, ctx, label, style):
		self.invoker = ctx.author
		self.ctx = ctx
		super().__init__(label=label, style=style)

	async def callback(self, interaction: discord.Interaction):
		if self.invoker == interaction.user:
			await interaction.response.defer()
			await interaction.delete_original_message()
			await self.ctx.message.add_reaction("<a:checkmark_a:842800730049871892>")
		else:
			await interaction.response.send_message("❌ Hey it's not your session !", ephemeral=True)

class View(discord.ui.View):
	"""Dropdown View"""
	def __init__(self, options, source, main, embed, placeholder = "Select..", min_val = 1, max_val = 1):
		super().__init__()

		self.add_item(Dropdown(options=options, placeholder=placeholder, min_val=min_val, max_val=max_val, source=source, main=main, embed=embed))
		self.add_item(Buttons(label="Quit", style=discord.ButtonStyle.red, ctx = source))