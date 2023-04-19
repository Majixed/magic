import platform
import psutil
import discord
import aiohttp
import json
import sys

from conf.var import light_gray
from discord.ext import commands
from googletrans import Translator


class Miscellaneous(commands.Cog, description="Miscellaneous commands"):
    def __init__(self, bot):
        self.bot = bot

    # Echo author's message and delete source
    @commands.command(name="secho", brief="Echo your message and delete the source")
    async def secho_(self, ctx, *, message):
        """Echoes the user's message and deletes the message sent by the user, takes the message content as an argument"""

        await ctx.message.delete()
        await ctx.send(message)

    # Echo author's message
    @commands.command(name="echo", aliases=["say"], brief="Echo your message")
    async def echo_(self, ctx, *, message):
        """Echoes the user's message, takes the message content as an argument"""

        await ctx.send(message)

    # Return bot latency
    @commands.command(name="ping", aliases=["pong"], brief="Retrieve bot latency")
    async def ping_(self, ctx):
        """Retrieves the bot's latency, takes no arguments"""

        resp = "Pong" if ctx.invoked_with == "ping" else "Ping"
        await ctx.send(f"{resp}! `{round(self.bot.latency * 1000)} ms`")

    # Basic calculator
    @commands.command(
        name="calc", aliases=["calculate"], brief="Perform simple calculations"
    )
    async def calc_(self, ctx, *, expression):
        """Queries the mathjs API to perform calculations on the given expression, takes the expression string as an argument"""

        addr = "https://api.mathjs.org/v4/"
        exprs = expression.split("\n")
        request = {"expr": exprs, "precision": 10}
        async with aiohttp.ClientSession() as session:
            async with session.post(addr, data=json.dumps(request)) as resp:
                result = await resp.json()
        if result["error"]:
            await ctx.send("```\n{}\n```".format(result["error"]))
            return
        await ctx.send("```\n{}\n```".format("\n".join(result["result"])))

    # Translate between languages
    @commands.command(
        name="translate", aliases=["tr"], brief="Translate between different languages"
    )
    async def translate_(self, ctx, src, dest, *, content):
        """Translate between two languages using the Google Translate API, takes the input language, output language, and message content as arguments"""

        transl = Translator()
        result = transl.translate(content, src=src, dest=dest).text
        await ctx.send(result)

    # Retrieve bot info
    @commands.command(name="about", brief="Retrieve information about the bot")
    async def about_(self, ctx):
        """Retrieves information about the bot, takes no arguments"""

        mem = psutil.virtual_memory()
        mem_str = "{0:.2f}GB used out of {1:.2f}GB ({mem.percent}%)".format(
            mem.used / (1024**3), mem.total / (1024**3), mem=mem
        )
        embed_info = discord.Embed(title="About", description="")

        embed_info.add_field(name="Guilds", value=len(ctx.bot.guilds), inline=False)
        embed_info.add_field(
            name="Members", value=len(list(ctx.bot.get_all_members())), inline=False
        )
        embed_info.add_field(
            name="Memory Usage",
            value=mem_str,
            inline=False,
        )
        embed_info.add_field(
            name="CPU Usage",
            value="{}%".format(psutil.cpu_percent()),
            inline=False,
        )
        embed_info.add_field(
            name="API Version",
            value="{} ({})".format(discord.__version__, discord.version_info[3]),
            inline=False,
        )
        embed_info.add_field(
            name="Python Version", value=sys.version.split("\n")[0], inline=False
        )
        embed_info.add_field(name="Platform", value=platform.platform(), inline=False)

        await ctx.send(embed=embed_info)


async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))
