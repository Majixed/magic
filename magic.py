import os
import asyncio
import discord

from discord.ext import commands
from pretty_help import DefaultMenu, PrettyHelp
from config.config import prefix, light_gray

currpath = os.getcwd()
currdir = os.path.basename(currpath)

if currdir != "magic":
    print(f"Fatal error: Current directory is not named 'magic', is named '{currdir}'. Aborting launch...")
    exit()

intents = discord.Intents.all()

bot = commands.Bot(
    activity = discord.Game(name=f"{prefix}help"),
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
menu = DefaultMenu(
        page_left=":page_left:963100801717403718",
        page_right=":page_right:963100747787026433",
        remove=":delete:962038961432322128",
        active_time=180
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
