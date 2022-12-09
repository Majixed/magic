import os
import asyncio
import discord

from discord.ext import commands
from dotenv import load_dotenv
from pretty_help import EmojiMenu, PrettyHelp
from conf.var import (
        emo_del,
        emo_left,
        emo_right,
        prefix,
        light_gray,
        react_timeout
        )

load_dotenv()

intents = discord.Intents.all()

bot = commands.Bot(
    activity = discord.Activity(type=discord.ActivityType.listening, name=f"{prefix}help"),
    command_prefix = commands.when_mentioned_or(prefix),
    description = f"Hello there! I'm magic. My prefix is {prefix}, but you can also summon me with a mention.",
    case_insensitive = True,
    intents=intents
    )

# Check if admins.json exists, if not, create it.
if not os.path.isfile("admins.json"):
    with open("admins.json", "w") as json_new:
        json_new.write("""
{
    "botAdmin": [
    ]
}
""")

# Prettify the help page
menu = EmojiMenu(
        page_left=emo_left.strip("<>"),
        page_right=emo_right.strip("<>"),
        remove=emo_del.strip("<>"),
        active_time=react_timeout
        )
bot.help_command = PrettyHelp(menu=menu, color=light_gray)

# Load all extensions
async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
            except Exception as e:
                print(e)

# Start up the bot
async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.getenv('TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())
