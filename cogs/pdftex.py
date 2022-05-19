import os
import json
import codecs
import discord
import asyncio
import datetime
import subprocess

from discord.ext import commands
from config.config import *

class pdfTeX(commands.Cog, description="The pdfTeX command suite"):
    def __init__(self, bot):
        self.bot = bot

    # Compile pdfLaTeX
    @commands.command(name="tex", aliases=["latex", "pdflatex", "pdftex"], brief="Compile pdfLaTeX code")
    async def tex_(self, ctx, *, code):
        """Compiles pdfLaTeX, takes the code as an argument"""

        with open("admins.json", "r") as json_read:
            admin_data = json.load(json_read)
        bot_admin = admin_data["botAdmin"]

        if ctx.author.id not in bot_owner and ctx.author.id not in bot_admin:
            return await ctx.send(embed=embed_noowner)
        async with ctx.typing():
            err_msg=None
            err_img=None
            out_img=None
            with open(f"tex/inputs/{ctx.author.id}.tmp", "w") as f_input:
                f_input.write(code)
            subprocess.call(f"dash tex/scripts/runtex.sh {ctx.author.id}")
        embed_err = discord.Embed(title="", description="", color=red)
        embed_err.add_field(name="\u200b", value=f"```tex\n{code}\n```", inline=False)
        embed_err.add_field(name="Compilation error", value=f"```\n{subprocess.getoutput(f'grep -A 10 ^! -m 2 tex/staging/{ctx.author.id}/{ctx.author.id}.log')[:1016]}\n```", inline=False)
        embed_err.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        if not subprocess.getoutput(f"grep -A 10 ^! -m 2 tex/staging/{ctx.author.id}/{ctx.author.id}.log"):
            pass
        else:
            err_msg = await ctx.send(embed=embed_err)
        try:
            out_img = await ctx.send(file=discord.File(f"tex/staging/{ctx.author.id}/{ctx.author.id}.png"))
            await out_img.add_reaction(emo_del)

            def check(reaction, user):
                return reaction.message.id == out_img.id and user == ctx.author

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=react_timeout, check=check)

                    if str(reaction.emoji) == emo_del:
                        if out_img is not None:
                            await out_img.delete()
                        if err_msg is not None:
                            await err_msg.delete()
                        break

                except asyncio.TimeoutError:
                    await out_img.clear_reactions()
                    break
        except FileNotFoundError:
            err_img = await ctx.send(file=discord.File("tex/failed.png"))
            await err_img.add_reaction(emo_del)

            def check(reaction, user):
                return reaction.message.id == err_img.id and user == ctx.author

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=react_timeout, check=check)

                    if str(reaction.emoji) == emo_del:
                        if err_img is not None:
                            await err_img.delete()
                        if err_msg is not None:
                            await err_msg.delete()
                        break

                except asyncio.TimeoutError:
                    await err_img.clear_reactions()
                    break

    # Upload your pdfLaTeX preamble
    @commands.command(name="preamble", brief="Upload your own or another user's pdfLaTeX preamble")
    async def preamble_(self, ctx, *, userid=None):
        """Uploads your own or another user's pdfLaTeX preamble to the current channel, takes the user ID as an optional argument"""

        with open("admins.json", "r") as json_read:
            admin_data = json.load(json_read)
        bot_admin = admin_data["botAdmin"]

        if ctx.author.id not in bot_owner and ctx.author.id not in bot_admin:
            return await ctx.send(embed=embed_noowner)
        if userid is None:
            try:
                p_own = await ctx.send(file=discord.File(f"tex/preamble/{ctx.author.id}.tex"))
                await p_own.add_reaction(emo_del)

                def check(reaction, user):
                    return reaction.message.id == p_own.id and user == ctx.author

                while True:
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=react_timeout, check=check)

                        if str(reaction.emoji) == emo_del:
                            await p_own.delete()
                            break

                    except asyncio.TimeoutError:
                        await p_own.clear_reactions()
                        break
            except:
                await ctx.send(embed=discord.Embed(description="You haven't set a custom preamble.", color=red))
        else:
            try:
                p_usr = await ctx.send(file=discord.File(f"tex/preamble/{userid}.tex"))
                await p_usr.add_reaction(emo_del)

                def check(reaction, user):
                    return reaction.message.id == p_usr.id and user == ctx.author

                while True:
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=react_timeout, check=check)

                        if str(reaction.emoji) == emo_del:
                            await p_usr.delete()
                            break

                    except asyncio.TimeoutError:
                        await p_usr.clear_reactions()
                        break
            except:
                await ctx.send(embed=discord.Embed(description="This user does not have a custom preamble.", color=red))

    # Replace your pdfLaTeX preamble
    @commands.command(name="replacepreamble", brief="Replace your pdfLaTeX preamble with an input file or code")
    async def replacepreamble_(self, ctx, *, code=None):
        """Replaces your pdfLaTeX preamble, takes either an input file or code as an argument"""

        with open("admins.json", "r") as json_read:
            admin_data = json.load(json_read)
        bot_admin = admin_data["botAdmin"]

        if ctx.author.id not in bot_owner and ctx.author.id not in bot_admin:
            return await ctx.send(embed=embed_noowner)
        if code is None and ctx.message.attachments:
            if ctx.message.attachments[0].size >= 250000:
                return await ctx.send(embed=discord.Embed(description="Attached file is too large (over `250KB`).", color=red))
            else:
                await ctx.message.attachments[0].save(f"tex/preamble/tmp/{ctx.author.id}.pre")
                try:
                    c = codecs.open(f"tex/preamble/tmp/{ctx.author.id}.pre", encoding="utf-8", errors="strict")
                    for line in c:
                        pass
                except UnicodeDecodeError:
                    subprocess.call(f"rm -f tex/preamble/tmp/{ctx.author.id}.pre")
                    await ctx.send(embed=discord.Embed(description="Could not decode attached file, please ensure it is encoded in `utf-8`.", color=red))
                else:
                    subprocess.call(f"mv tex/preamble/tmp/{ctx.author.id}.pre tex/preamble/{ctx.author.id}.tex")
                    await ctx.send(embed=discord.Embed(description=f"Your preamble has been updated. View it with `{ctx.prefix}preamble`.", color=green))
        elif code is None and not ctx.message.attachments:
            return await ctx.send(embed=discord.Embed(description="You need to attach the file containing your preamble or enter the replacement text.", color=red))
        else:
            with open(f"tex/preamble/{ctx.author.id}.tex", "w") as r:
                r.write(code)
            await ctx.send(embed=discord.Embed(description=f"Your preamble has been updated. View it with `{ctx.prefix}preamble`.", color=green))

    # Reset your pdfLaTeX preamble
    @commands.command(name="resetpreamble", brief="Reset your pdfLaTeX preamble to the default")
    async def resetpreamble_(self, ctx):
        """Resets your pdfLaTeX preamble to the default, takes no arguments"""

        with open("admins.json", "r") as json_read:
            admin_data = json.load(json_read)
        bot_admin = admin_data["botAdmin"]

        if ctx.author.id not in bot_owner and ctx.author.id not in bot_admin:
            return await ctx.send(embed=embed_noowner)
        subprocess.call(f"rm -f tex/preamble/{ctx.author.id}.tex")
        await ctx.send(embed=discord.Embed(description="Your preamble has been reset to the default.", color=green))

    # Append to your pdfLaTeX preamble
    @commands.command(name="appendpreamble", brief="Append lines to your pdfLaTeX preamble")
    async def appendpreamble_(self, ctx, *, code):
        """Appends lines to your pdfLaTeX preamble, takes the code as an argument"""

        with open("admins.json", "r") as json_read:
            admin_data = json.load(json_read)
        bot_admin = admin_data["botAdmin"]

        if ctx.author.id not in bot_owner and ctx.author.id not in bot_admin:
            return await ctx.send(embed=embed_noowner)
        if os.path.isfile(f"tex/preamble/{ctx.author.id}.tex"):
            with open(f"tex/preamble/{ctx.author.id}.tex", "a") as fc:
                fc.write(f"\n{code}")
        else:
            subprocess.call(f"cp tex/preamble/default/default.tex tex/preamble/{ctx.author.id}.tex")
            with open(f"tex/preamble/{ctx.author.id}.tex", "a") as fd:
                fd.write(f"\n{code}")
        await ctx.send(embed=discord.Embed(description=f"Your preamble has been updated. View it with `{ctx.prefix}preamble`.", color=green))

async def setup(bot):
    await bot.add_cog(pdfTeX(bot))
