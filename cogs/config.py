import discord

from discord.ext import commands

# List of UIDs allowed to run administrator commands
allowed_IDs = [598847267377643530]
#              Majixed#0586
allowed_IDs_admin = [469851141438701569, 220148284168077312, 408905098312548362, 830760441209815090, 617680848346677268, 911170538255294524, 424380116039237642, 470675453980573706, 726324233696968814]
#                    plante#0126         leothelion#0001     JetRaidz#3498       Slurp#0155          BlaiiZong#2378      Tasmav#3911         Stain#2724          SUFF3R#9581         Danielle#3134

# Colors
red = 0xff5555
green = 0x55ff55
blue = 0x5555ff
white = 0xffffff
black = 0x000000
light_gray = 0xcccccc

# Custom emojis
emo_del = "<:delete:962038961432322128>"
emo_left = "<:page_left:963100801717403718>"
emo_right = "<:page_right:963100747787026433>"

# The value of timeout
react_timeout = 180.0

# Common shorthands
embed_noowner = discord.Embed(description="You must be a bot owner to use this command.", color=red)
embed_noarg = discord.Embed(description="Missing required argument(s).", color=red)
embed_badarg = discord.Embed(description="Bad argument(s).", color=red)
embed_nocmd = discord.Embed(description="Command not found.", color=red)
embed_shutdown = discord.Embed(description="Shutting down, goodbye.", color=green)
