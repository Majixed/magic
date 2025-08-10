import platform
import psutil
import discord
import aiohttp
import json
import sys

from re import fullmatch
from config.config import gray, red, green
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
        await ctx.reply(
            f"{resp}! `{round(self.bot.latency * 1000)} ms`", mention_author=False
        )

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
            await ctx.reply(
                "```\n{}\n```".format(result["error"]), mention_author=False
            )
            return
        await ctx.reply(
            "```\n{}\n```".format("\n".join(result["result"])), mention_author=False
        )

    # Translate between languages
    @commands.command(
        name="translate", aliases=["tr"], brief="Translate between different languages"
    )
    async def translate_(self, ctx, src, dest, *, content):
        """Translate between two languages using the Google Translate API, takes the input language, output language, and message content as arguments"""

        transl = Translator()
        result = transl.translate(content, src=src, dest=dest).text
        await ctx.reply(result, mention_author=False)

    # Change color of LaTeX output
    @commands.command(
        name="texcolor", aliases=["tc"], brief="Change the color of your LaTeX output"
    )
    async def texcolor_(self, ctx, fg_hex: str, bg_hex: str):
        """Change the color of your LaTeX output, takes the text color and page color hex codes as respective arguments"""

        pattern = "[a-fA-F0-9]*"

        fg_hex = fg_hex.strip("#")
        bg_hex = bg_hex.strip("#")

        trans_bg_hex = None

        if bg_hex == "trans":
            trans_bg_hex = bg_hex
            bg_hex = "000000"

        hex_check = bool(fullmatch(pattern, fg_hex) and fullmatch(pattern, bg_hex))

        if not hex_check or len(fg_hex) != 6 or len(bg_hex) != 6:
            return await ctx.reply(
                embed=discord.Embed(
                    description="Invalid hex, please recheck your hex values", color=red
                ),
                mention_author=False,
            )

        if trans_bg_hex:
            bg_hex = trans_bg_hex

        try:
            with open("tex/config/texconfig.json", "r") as cfg:
                config_data = json.load(cfg)
        except (FileNotFoundError, json.JSONDecodeError):
            config_data = {}

        user_id = str(ctx.author.id)

        if user_id not in config_data:
            config_data[user_id] = {}

        config_data[user_id]["bg"] = bg_hex
        config_data[user_id]["fg"] = fg_hex

        with open("tex/config/texconfig.json", "w") as cfg:
            json.dump(config_data, cfg, indent=4)

        await ctx.reply(
            embed=discord.Embed(
                description="LaTeX color settings saved\n```text: #{}\npage: {}```".format(
                    fg_hex, str("#" + bg_hex) if bg_hex != "trans" else bg_hex
                ),
                color=green,
            ),
            mention_author=False,
        )

    # Retrieve bot info
    @commands.command(name="about", brief="Retrieve information about the bot")
    async def about_(self, ctx):
        """Retrieves information about the bot, takes no arguments"""

        mem = psutil.virtual_memory()
        mem_str = "{0:.2f}GB used out of {1:.2f}GB ({mem.percent}%)".format(
            mem.used / (1024**3), mem.total / (1024**3), mem=mem
        )
        embed_info = discord.Embed(title="About", description="", color=gray)

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

        await ctx.reply(embed=embed_info, mention_author=False)


async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))
