from logging import INFO
from pathlib import Path

import discord

from utils.bot import DiscordBot
from utils.config import load_config
from utils.logger import setup_logging

root_dir = Path(__file__).parent

config_dir = root_dir / "config"
env_path = config_dir / ".env"
log_dir = root_dir / "logs"

setup_logging(log_dir, INFO, INFO)


if __name__ == "__main__":
    bot = DiscordBot(
        root_dir=root_dir,
        config = load_config(config_dir, env_path),
        activity = discord.CustomActivity(name="Booting...", emoji='⚙️'),
        allowed_mentions = discord.AllowedMentions(everyone=False),
        case_insensitive = True,
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

    bot.run(
        bot.config.env.bot_token,
        reconnect = True,
        log_handler = None,
    )