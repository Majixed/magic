import os
import discord

from discord.ext import commands
from pretty_help import DefaultMenu, PrettyHelp

currpath = os.getcwd()
currdir = os.path.basename(currpath)

if currdir != "magic":
    print(f"Fatal error: Current directory is not named 'magic', is named {currdir}. Aborting launch...")
    exit()

prefix = "&"

bot = commands.Bot(
    activity = discord.Game(name=f"{prefix}help"),
    command_prefix = commands.when_mentioned_or(f"{prefix}"),
    description = f"Hello there! I'm magic. My prefix is {prefix}, but you can also summon me with a mention.",
    case_insensitive = True
    )

# Prettify the help page
menu = DefaultMenu(
        page_left=":page_left:963100801717403718",
        page_right=":page_right:963100747787026433", 
        remove=":delete:962038961432322128", 
        active_time=180
        )
bot.help_command = PrettyHelp(menu=menu, color=0xcccccc)

# Load all extensions
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        try:
            bot.load_extension(f"cogs.{filename[:-3]}")
        except Exception as e:
            print(e)

# Start up the bot
if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))
