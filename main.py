from logging import INFO

from discord import AllowedMentions, CustomActivity, Intents, Status

from utils.bot import DiscordBot
from utils.config import load_config
from utils.logger import setup_logging
from utils.paths import config_dir, env_path, log_dir

setup_logging(log_dir, INFO, INFO)


if __name__ == "__main__":
    bot = DiscordBot(
        config = load_config(config_dir, env_path),
        activity = CustomActivity(name="Booting...", emoji='⚙️'),
        allowed_mentions = AllowedMentions(everyone=False),
        case_insensitive = True,
        intents = Intents(
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
        status = Status.idle,
    )

    bot.run(
        bot.config.env.bot_token,
        reconnect = True,
        log_handler = None,
    )