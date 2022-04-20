import discord

from views.view import View as Parent

class Dropdown(discord.ui.Select):
    def __init__(self, options, source, placeholder : str, min_val : int, max_val : int):
        self.source = source
        self.invoker = source.author

        choices = []
        for option in options:
            if not option["emoji"]:
                choices.append(discord.SelectOption(label=option["label"], description=option["description"]))
            else:
                choices.append(discord.SelectOption(label=option["label"], description=option["description"], emoji=option["emoji"]))

        super().__init__(placeholder = placeholder, min_values = min_val, max_values = max_val, options = choices)

    async def callback(self, interaction: discord.Interaction):
        if self.invoker == interaction.user:
            message = "Selected languages : "
            for value in self.values:
                message += f"`{value}` "
            await interaction.response.defer()
            await interaction.delete_original_message()
            await self.source.reply(message)
        else:
            await interaction.response.send_message("❌ Hey it's not your session !", ephemeral=True)

class View(Parent):
    """Dropdown View"""
    def __init__(self, options, source, placeholder = "Select..", min_val = 1, max_val = 1):
        super().__init__()

        self.add_item(Dropdown(options=options, placeholder=placeholder, min_val=min_val, max_val=max_val, source=source))