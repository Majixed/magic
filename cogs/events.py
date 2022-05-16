import discord
import datetime

from discord.ext import commands
from config.config import *


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Message when the bot is ready to be operated
    @commands.Cog.listener()
    async def on_ready(self):
        print("")
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Logged in as {self.bot.user} ({self.bot.user.id})")
        print("------------------------------------------------------------------")
        print("")

    # Basic error handling
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            await ctx.send(f"```\n{error}\n```")

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
        try:
            if message.author == self.bot.user:
                return
            if message.author.bot:
                return
            elif "LOL" in message.content:
                await message.channel.send("Haha. That was so funny.")
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(Events(bot))
