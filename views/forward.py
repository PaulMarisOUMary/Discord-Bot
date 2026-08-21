from discord import (
    ChannelType,
    Interaction,
    Message,
    TextChannel,
    User,
    VoiceChannel,
    AllowedMentions,
)
from discord.ui import ChannelSelect, Label, Modal, TextInput


class Forward(Modal, title="Forward"):
    channel = Label(
        text="Channel",
        component=ChannelSelect(
            channel_types=[ChannelType.text, ChannelType.voice],
            min_values=1,
            max_values=1,
            required=True,
        ),
    )
    reason = TextInput(label="Reason", required=False)

    def __init__(self, message: Message, **kwargs) -> None:
        super().__init__(**kwargs)

        self.message = message

    async def on_submit(self, interaction: Interaction):
        selected_channel = self.channel.component.values[0]  # type: ignore

        if interaction.guild is None or isinstance(interaction.user, User):
            await interaction.response.send_message(
                "This command should only be used in a Guild.", ephemeral=True
            )
            return

        target_channel = interaction.guild.get_channel(selected_channel.id)

        if target_channel is None:
            target_channel = await interaction.guild.fetch_channel(selected_channel.id)

        if not isinstance(target_channel, (TextChannel, VoiceChannel)):
            return

        permissions = target_channel.permissions_for(interaction.user)

        if not permissions.view_channel or not permissions.send_messages:
            await interaction.response.send_message(
                "You don't have the required permissions in the selected channel.",
                ephemeral=True,
            )
            return

        try:
            await self.message.forward(target_channel)

            context = f"-# From: {self.message.author.mention}"

            if self.reason.value:
                context += f"\n-# Reason: {self.reason.value}"

            await target_channel.send(
                content=context,
                allowed_mentions=AllowedMentions(
                    everyone=False, roles=False, users=False
                ),
            )

            await interaction.response.send_message(
                "Message forwarded!", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Forward failed: {e}", ephemeral=True
            )
