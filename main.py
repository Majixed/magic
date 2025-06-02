import os
import sys
import asyncio
import discord
import logging

from discord.ext import commands
from dotenv import load_dotenv
from pretty_help import EmojiMenu, PrettyHelp
from config.config import (
    emo_del,
    emo_left,
    emo_right,
    prefix,
    gray,
    react_timeout,
)

load_dotenv()

bot = commands.Bot(
    activity=discord.Activity(
        type=discord.ActivityType.listening, name=f"{prefix}help"
    ),
    command_prefix=commands.when_mentioned_or(prefix),
    description=f"Hello there! I'm magic. My prefix is {prefix}, but you can also summon me with a mention.",
    case_insensitive=True,
    intents=~discord.Intents(presences=True),
)


# Create required directories if they don't exist
req_dirs = [
    "tex/inputs",
    "tex/staging",
    "tex/log",
    "tex/config",
]

for dir in req_dirs:
    os.makedirs(dir, exist_ok=True)

# Logging
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler(filename="magic.log", encoding="utf-8", mode="a")

dt_fmt = "%Y-%m-%d %H:%M:%S"
file_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
)

console_handler.setFormatter(discord.utils._ColourFormatter())
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Prettify the help page
menu = EmojiMenu(
    page_left=emo_left.strip("<>"),
    page_right=emo_right.strip("<>"),
    remove=emo_del.strip("<>"),
    active_time=react_timeout,
)
bot.help_command = PrettyHelp(menu=menu, color=gray, send_typing=False)


# Load all extensions
async def load_extensions():
    for filename in os.listdir("./modules"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"modules.{filename[:-3]}")
            except Exception as e:
                print(e)


# Start up the bot
async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.getenv("TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
