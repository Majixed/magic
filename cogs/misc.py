import discord
import aiohttp
import json

from discord.ext import commands
from googletrans import Translator
from config.config import *

class Miscellaneous(commands.Cog, description="Miscellaneous commands"):
    def __init__(self, bot):
        self.bot = bot

    # Echo author's message and delete source
    @commands.command(name="secho", brief="Echo your message and delete the source")
    async def secho_(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

    # Echo author's message
    @commands.command(name="echo", aliases=["say"], brief="Echo your message")
    async def echo_(self, ctx, *, message):
        await ctx.send(message)

    # Return bot latency
    @commands.command(name="ping", aliases=["pong"], brief="Retrieve bot latency")
    async def ping_(self, ctx):
        resp = "Pong" if ctx.invoked_with == "ping" else "Ping"
        await ctx.send(f"{resp}! `{round(self.bot.latency * 1000)} ms`")

    # Basic calculator
    @commands.command(name="calc", aliases=["calculate"], brief="Perform simple calculations")
    async def calc_(self, ctx, *, expression):
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

    # A translator?!
    @commands.command(name="translate", aliases=["tr"], brief="Translate between different languages")
    async def translate_(self, ctx, src: str, dest: str, *, content):
        transl = Translator()
        result = transl.translate(content, src=src, dest=dest).text
        await ctx.send(result)

def setup(bot):
    bot.add_cog(Miscellaneous(bot))
