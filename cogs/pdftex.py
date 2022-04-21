import os
import codecs
import discord
import asyncio
import datetime
import subprocess

from discord.ext import commands
from .config import *

class pdfTeX(commands.Cog, description="The pdfTeX command suite"):
    def __init__(self, bot):
        self.bot = bot

    # Compile pdfLaTeX
    @commands.command(aliases=["latex", "pdflatex", "pdftex"], brief="Compile pdfLaTeX code")
    async def tex(self, ctx, *, code):
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {ctx.author} ({ctx.author.id}) compiled pdflatex: {code}")
        if ctx.author.id in allowed_IDs or ctx.author.id in allowed_IDs_admin:
            async with ctx.typing():
                subprocess.call(f"rm -f ~group/{ctx.author.id}.*")
                subprocess.call(f"rm -rf ~/Documents/magic/tex/staging/{ctx.author.id}")
                subprocess.call(f"mkdir ~/Documents/magic/tex/staging/{ctx.author.id}")
                subprocess.call(f"cd ~/Documents/magic/tex/staging/{ctx.author.id}")
                with open(f"{ctx.author.id}.tex", "w") as f_docclass:
                    f_docclass.write("\\documentclass[preview, border=20pt, 12pt]{standalone}\n")
                    f_docclass.write("\\IfFileExists{eggs.sty}{\\usepackage{eggs}}{}\n")
                if os.path.isfile(f"../../preamble/{ctx.author.id}.tex"):
                    subprocess.call(f"cat ../../preamble/{ctx.author.id}.tex >> {ctx.author.id}.tex")
                else:
                    subprocess.call(f"cat ../../preamble/default/default.tex >> {ctx.author.id}.tex")
                with open(f"../../inputs/{ctx.author.id}.tmp", "w") as f_input:
                    f_input.write("\n\\begin{document}\n")
                    f_input.write(code)
                    f_input.write("\n\\end{document}\n")
                subprocess.call(f"cat ../../inputs/{ctx.author.id}.tmp >> {ctx.author.id}.tex")
                subprocess.call(f"pdflatex -jobname={ctx.author.id} -interaction=nonstopmode -no-shell-escape {ctx.author.id}.tex > ../../log/texout.log")
                subprocess.call(f"mv {ctx.author.id}.pdf ~group")
                subprocess.call(f"open 'shortcuts://run-shortcut?name=pdfpng3&input={ctx.author.id}.pdf'")
                subprocess.call("sleep 1.5")
                subprocess.call(f"mv ~group/{ctx.author.id}.png .")
                subprocess.call("cd ~/Documents/magic")
            embed_err = discord.Embed(title="", description="", color=red)
            embed_err.add_field(name="\u200b", value=f"```tex\n{code}\n```", inline=False)
            embed_err.add_field(name="Compilation error", value=f"```\n{subprocess.getoutput(f'grep -A 10 ^! -m 2 tex/staging/{ctx.author.id}/{ctx.author.id}.log')[:1016]}\n```", inline=False)
            embed_err.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
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
                            await out_img.delete()
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
                            await err_img.delete()
                            await err_msg.delete()
                            break

                    except asyncio.TimeoutError:
                        await err_img.clear_reactions()
                        break
        else:
            await ctx.send(embed=embed_noowner)

    # Upload your pdfLaTeX preamble
    @commands.command(brief="Upload your own or another user's pdfLaTeX preamble")
    async def preamble(self, ctx, *, userid=None):
        if ctx.author.id in allowed_IDs or ctx.author.id in allowed_IDs_admin:
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
        else:
            await ctx.send(embed=embed_noowner)

    # Replace your pdfLaTeX preamble
    @commands.command(brief="Replace your pdfLaTeX preamble with an input file or text")
    async def replacepreamble(self, ctx, *, code=None):
        if ctx.author.id in allowed_IDs or ctx.author.id in allowed_IDs_admin:
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
        else:
            ctx.send(embed=embed_noowner)

    # Reset your pdfLaTeX preamble
    @commands.command(brief="Reset your pdfLaTeX preamble to the default")
    async def resetpreamble(self, ctx):
        if ctx.author.id in allowed_IDs or ctx.author.id in allowed_IDs_admin:
            subprocess.call(f"rm -f tex/preamble/{ctx.author.id}.tex")
            await ctx.send(embed=discord.Embed(description="Your preamble has been reset to the default.", color=green))
        else:
            await ctx.send(embed=embed_noowner)

    # Append to your pdfLaTeX preamble
    @commands.command(brief="Append lines to your pdfLaTeX preamble")
    async def appendpreamble(self, ctx, *, code):
        if ctx.author.id in allowed_IDs or ctx.author.id in allowed_IDs_admin:
            if os.path.isfile(f"tex/preamble/{ctx.author.id}.tex"):
                with open(f"tex/preamble/{ctx.author.id}.tex", "a") as fc:
                    fc.write(f"\n{code}")
            else:
                subprocess.call(f"cp tex/preamble/default/default.tex tex/preamble/{ctx.author.id}.tex")
                with open(f"tex/preamble/{ctx.author.id}.tex", "a") as fd:
                    fd.write(f"\n{code}")
            await ctx.send(embed=discord.Embed(description=f"Your preamble has been updated. View it with `{ctx.prefix}preamble`.", color=green))
        else:
            await ctx.send(embed=embed_noowner)

def setup(bot):
    bot.add_cog(pdfTeX(bot))
