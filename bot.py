import discord

from logging import DEBUG, INFO

from utils.basebot import DiscordBot
from utils.helper import load_configs, load_envs, set_logging

if __name__ == "__main__":
    bot = DiscordBot(
        activity = discord.CustomActivity(name="Booting...", emoji='⚙️'),
        allowed_mentions = discord.AllowedMentions(everyone=False),
        case_insensitive = True,
        config = load_configs(folder="./config"),
        env = load_envs(files=["./config/.env"]),
        intents = discord.Intents(
            emojis=True,
            guilds=True,
            invites=True,
            members=True,
            message_content=True,
            messages=True,
            presences=True,
            reactions=True,
            voice_states=True,
        ),
        max_messages = 2500,
        status = discord.Status.idle,
    )

    bot.logger, stream_handler = set_logging(file_level=INFO, console_level=INFO, filename="discord.log")

    bot.run(
        bot.config["env"]["BOT_TOKEN"],
        reconnect = True,
        log_handler = stream_handler,
        log_level = DEBUG,
    )