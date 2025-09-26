import asyncio
import asyncpraw
import discord

from datetime import datetime, timezone
from discord.ext import commands

from utils.basebot import DiscordBot

class Reddit(commands.Cog, name="reddit"):
    """
        Connects Reddit and Discord.
        
        Require intents:
            - None

        Require bot permission:
            - attach_files
            - send_messages
            - use_external_emojis
    """
    def __init__(self, bot: DiscordBot) -> None:
        self.bot: DiscordBot = bot
        self.subconfig_data: dict = self.bot.config["cogs"][self.__cog_name__.lower()]

        self.reddit: asyncpraw.Reddit = None # type: ignore
        self.tasks: list[asyncio.Task] = []

    def help_custom(self) -> tuple[str, str, str]:
        emoji = '🟠'
        label = "Reddit"
        description = "Reddit goes brrrrrr"
        return emoji, label, description

    async def cog_load(self) -> None:
        self.reddit = self.create_reddit()
        self.tasks = []
        for connection in self.subconfig_data["connections"]:
            try:
                self.tasks.append(
                    asyncio.create_task(self.listen(**connection))
                )
            except Exception as e:
                self.bot.logger.error(e)

    async def cog_unload(self) -> None:
        for task in self.tasks:
            task.cancel()
        await self.reddit.close()

    async def listen(self, subreddit: str, channel: str) -> None:
        sub = await self.reddit.subreddit(subreddit)
        channels = []
        async for guild in self.bot.fetch_guilds():
            for chan in (await guild.fetch_channels()):
                if channel.lower() in chan.name.lower():
                    channels.append(chan)

        self.bot.logger.name = "discord.reddit"
        self.bot.logger.info("Listening on: r/"+subreddit)
        async for submission in sub.stream.submissions(skip_existing=True):
            try:
                # self.bot.logger.debug(f"r/{subreddit}: {submission.title}")
                await self.send(submission, channels)
            except Exception as e:
                self.bot.logger.error(e)

    async def send(self, submission: asyncpraw.reddit.Submission, channels: list[discord.TextChannel]) -> None:
        embed = discord.Embed(
            title=submission.title,
            url=submission.shortlink,
            color=0xFF4500,
            description=submission.selftext
        )
        await submission.author.load() # Load the author icon
        embed.set_author(name=submission.author.name, icon_url=submission.author.icon_img)
        embed.set_image(url=submission.url)
        embed.timestamp = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
        await submission.subreddit.load() # Load the sub name
        embed.set_footer(text="r/"+submission.subreddit.display_name)

        for channel in channels:
            try:
                await channel.send(embed=embed)
            except:
                pass # Missing permissions

    def create_reddit(self) -> asyncpraw.Reddit:
        reddit = asyncpraw.Reddit(**self.subconfig_data["client"])
        return reddit



async def setup(bot: DiscordBot) -> None:
    await bot.add_cog(Reddit(bot))