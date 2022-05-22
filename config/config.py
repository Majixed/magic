import discord

# List of UIDs allowed to run administrator commands
# Replace this with your own user ID
bot_owner = [598847267377643530]

# The bot's prefix
prefix = "&"

# Colors
red = 0xff5555
green = 0x55ff55
blue = 0x5555ff
white = 0xffffff
black = 0x000000
light_gray = 0x2f3136

# Custom emojis
# Replace these with your own custom emojis
emo_del = "<:delete:962038961432322128>"
emo_left = "<:page_left:963100801717403718>"
emo_right = "<:page_right:963100747787026433>"

# Timeout value
react_timeout = 180.0

# Commonly used variables
embed_noowner = discord.Embed(description="You must be a bot owner to use this command", color=red)
