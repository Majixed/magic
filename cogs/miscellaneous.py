import discord
import aiohttp
import json

from discord.ext import commands
from .config import *

class Miscellaneous(commands.Cog, description="Miscellaneous commands"):
    def __init__(self, bot):
        self.bot = bot

    # Echo author's message and delete source
    @commands.command(brief="Echo your message and delete the source")
    async def secho(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

    # Echo author's message
    @commands.command(aliases=["say"], brief="Echo your message")
    async def echo(self, ctx, *, message):
        await ctx.send(message)

    # Return bot latency
    @commands.command(aliases=["pong"], brief="Retrieve bot latency")
    async def ping(self, ctx):
        resp = "Pong" if ctx.invoked_with == "ping" else "Ping"
        await ctx.send(f"{resp}! `{round(self.bot.latency * 1000)} ms`")

    # Basic calculator
    @commands.command(aliases=["calculate"], brief="Perform simple calculations")
    async def calc(self, ctx, *, expression):
        addr = "https://api.mathjs.org/v4/"
        exprs = expression.split("\n")
        request = {"expr": exprs,
                   "precision": 10}
        async with aiohttp.ClientSession() as session:
            async with session.post(addr, data=json.dumps(request)) as resp:
                result = await resp.json()
        if result["error"]:
            await ctx.send("```\n{}\n```".format(result["error"]))
            return
        await ctx.send("```\n{}\n```".format("\n".join(result["result"])))

def setup(bot):
    bot.add_cog(Miscellaneous(bot))
