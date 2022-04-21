import discord
import datetime

from discord.ext import commands
from .config import *


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Message when the bot is ready to be operated
    @commands.Cog.listener()
    async def on_ready(self):
        print("--------------------------------------------")
        print("Logged in as {0.user} ({0.user.id})".format(self.bot))
        print("--------------------------------------------")

    # Basic error handling
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=embed_noarg)
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(embed=discord.Embed(description=f"Command `{ctx.invoked_with}` not found.", color=red))
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=embed_badarg)

    # Command log
    @commands.Cog.listener()
    async def on_command(self, ctx):
        channel = self.bot.get_channel(960503364871938068)

        embed_cmd_gld = discord.Embed(description=f"{ctx.author} ({ctx.author.id}) used command `{ctx.command}` in guild {ctx.guild}", color=light_gray)
        embed_cmd_gld.timestamp = datetime.datetime.utcnow()
        embed_cmd_dm = discord.Embed(description=f"{ctx.author} ({ctx.author.id}) used command `{ctx.command}` in DM", color=light_gray)
        embed_cmd_dm.timestamp = datetime.datetime.utcnow()
        if not ctx.guild:
            await channel.send(embed=embed_cmd_dm)
        else:
            await channel.send(embed=embed_cmd_gld)

    # Listen for message edits
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.bot.process_commands(after)

    # Respond to messages with uppercase "LOL"
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.author.bot:
            return
        elif "LOL" in message.content:
            await message.channel.send("Haha. That was so funny.")

def setup(bot):
    bot.add_cog(Events(bot))
