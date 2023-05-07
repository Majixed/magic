import os
import codecs
import shutil
import discord
import asyncio
import subprocess

from typing import Union
from discord.ext import commands
from config.config import (
    emo_del,
    green,
    red,
    react_timeout,
)


class pdfTeX(commands.Cog, description="The pdfTeX command suite"):
    def __init__(self, bot):
        self.bot = bot

    # Compile pdfLaTeX
    @commands.command(
        name="tex",
        aliases=["latex", "pdflatex", "pdftex"],
        brief="Compile pdfLaTeX code",
    )
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def tex_(self, ctx, *, code):
        """Compiles pdfLaTeX, takes the code as an argument"""

        err_msg = None
        out_img = None
        if "```" in code:
            lines = code.splitlines()
            codeblock = False
            final_code = []
            for line in lines:
                if "```" in line:
                    splits = line.split("```")
                    for split in splits:
                        if codeblock and split not in ["", "tex", "latex"]:
                            final_code.append(f"{split}")
                        codeblock = not codeblock
                    if codeblock:
                        final_code.append("")
                    codeblock = not codeblock
                elif codeblock:
                    final_code.append(line)
            code = "\n".join(final_code).rstrip("\n")
        with open(f"tex/inputs/{ctx.author.id}.tmp", "w") as f_input:
            f_input.write(code)
        subprocess.run(f"tex/scripts/runtex.sh {ctx.author.id}", shell=True)
        if os.path.isfile(f"tex/staging/{ctx.author.id}/{ctx.author.id}.error"):
            with open(
                f"tex/staging/{ctx.author.id}/{ctx.author.id}.error", "r"
            ) as f_err:
                err_out = f_err.read()
            embed_err = discord.Embed(title="", description="", color=red)
            embed_err.add_field(
                name="Compilation error",
                value=f"```\n{err_out[:1016]}\n```",
                inline=False,
            )
            embed_err.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            err_msg = await ctx.send(embed=embed_err)
        out_img = await ctx.send(
            file=discord.File(f"tex/staging/{ctx.author.id}/{ctx.author.id}.png")
        )
        await out_img.add_reaction(emo_del)

        def check(reaction, user):
            return reaction.message.id == out_img.id and user == ctx.author

        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=react_timeout, check=check
                )

                if str(reaction.emoji) == emo_del:
                    if out_img:
                        await out_img.delete()
                    if err_msg:
                        await err_msg.delete()
                    break

            except asyncio.TimeoutError:
                if ctx.channel.type != discord.ChannelType.private:
                    try:
                        await out_img.clear_reactions()
                    except discord.Forbidden:
                        pass
                break

    # Upload your pdfLaTeX preamble
    @commands.command(
        name="preamble", brief="Upload your own or another user's pdfLaTeX preamble"
    )
    async def preamble_(self, ctx, *, user: Union[int, discord.User] | None):
        """Uploads your own or another user's pdfLaTeX preamble to the current channel, takes the user ID as an optional argument"""

        if not user:
            try:
                p_own = await ctx.send(
                    "Your `pdflatex` preamble",
                    file=discord.File(f"tex/preamble/{ctx.author.id}.tex"),
                )
                await p_own.add_reaction(emo_del)

                def check(reaction, user):
                    return reaction.message.id == p_own.id and user == ctx.author

                while True:
                    try:
                        reaction, user = await self.bot.wait_for(
                            "reaction_add", timeout=react_timeout, check=check
                        )

                        if str(reaction.emoji) == emo_del:
                            await p_own.delete()
                            break

                    except asyncio.TimeoutError:
                        if ctx.channel.type != discord.ChannelType.private:
                            try:
                                await p_own.clear_reactions()
                            except discord.Forbidden:
                                pass
                        break
            except FileNotFoundError:
                await ctx.send(
                    embed=discord.Embed(
                        description="You haven't set a custom preamble.", color=red
                    )
                )
        else:
            if isinstance(user, int):
                userid = user
            elif isinstance(user, discord.User):
                userid = user.id
            username = await self.bot.fetch_user(userid)
            try:
                p_usr = await ctx.send(
                    f"{username}'s `pdflatex` preamble",
                    file=discord.File(f"tex/preamble/{userid}.tex"),
                )
                await p_usr.add_reaction(emo_del)

                def check(reaction, user):
                    return reaction.message.id == p_usr.id and user == ctx.author

                while True:
                    try:
                        reaction, user = await self.bot.wait_for(
                            "reaction_add", timeout=react_timeout, check=check
                        )

                        if str(reaction.emoji) == emo_del:
                            await p_usr.delete()
                            break

                    except asyncio.TimeoutError:
                        if ctx.channel.type != discord.ChannelType.private:
                            try:
                                await p_usr.clear_reactions()
                            except discord.Forbidden:
                                pass
                        break
            except FileNotFoundError:
                await ctx.send(
                    embed=discord.Embed(
                        description="This user does not have a custom preamble.",
                        color=red,
                    )
                )

    # Replace your pdfLaTeX preamble
    @commands.command(
        name="replacepreamble",
        brief="Replace your pdfLaTeX preamble with an input file or code",
    )
    async def replacepreamble_(self, ctx, *, code=None):
        """Replaces your pdfLaTeX preamble, takes either an input file or code as an argument"""

        if not code and ctx.message.attachments:
            if ctx.message.attachments[0].size >= 250000:
                return await ctx.send(
                    embed=discord.Embed(
                        description="Attached file is too large (over `250KB`).",
                        color=red,
                    )
                )
            await ctx.message.attachments[0].save(f"tex/preamble/{ctx.author.id}.tex")
            try:
                codecs.open(
                    f"tex/preamble/{ctx.author.id}.tex",
                    encoding="utf-8",
                    errors="strict",
                ).readlines()
            except UnicodeDecodeError:
                os.remove(f"tex/preamble/{ctx.author.id}.tex")
                return await ctx.send(
                    embed=discord.Embed(
                        description="Could not decode attached file, please ensure it is encoded in `utf-8`.",
                        color=red,
                    )
                )
            await ctx.send(
                embed=discord.Embed(
                    description=f"Your preamble has been updated. View it with `{ctx.prefix}preamble`.",
                    color=green,
                )
            )
        elif code and ctx.message.attachments:
            return await ctx.send(
                embed=discord.Embed(
                    description="Please send your code either as a message or in a file, not both.",
                    color=red,
                )
            )
        elif not code and not ctx.message.attachments:
            return await ctx.send(
                embed=discord.Embed(
                    description="You need to attach the file containing your preamble or enter the replacement text.",
                    color=red,
                )
            )
        elif code and not ctx.message.attachments:
            with open(f"tex/preamble/{ctx.author.id}.tex", "w") as r:
                r.write(code)
            await ctx.send(
                embed=discord.Embed(
                    description=f"Your preamble has been updated. View it with `{ctx.prefix}preamble`.",
                    color=green,
                )
            )

    # Reset your pdfLaTeX preamble
    @commands.command(
        name="resetpreamble", brief="Reset your pdfLaTeX preamble to the default"
    )
    async def resetpreamble_(self, ctx):
        """Resets your pdfLaTeX preamble to the default, takes no arguments"""

        if os.path.isfile(f"tex/preamble/{ctx.author.id}.tex"):
            os.remove(f"tex/preamble/{ctx.author.id}.tex")
            await ctx.send(
                embed=discord.Embed(
                    description="Your preamble has been reset to the default.",
                    color=green,
                )
            )
        else:
            await ctx.send(
                embed=discord.Embed(
                    description="You already have the default preamble.", color=red
                )
            )

    # Append to your pdfLaTeX preamble
    @commands.command(
        name="appendpreamble", brief="Append lines to your pdfLaTeX preamble"
    )
    async def appendpreamble_(self, ctx, *, code):
        """Appends lines to your pdfLaTeX preamble, takes the code as an argument"""

        if os.path.isfile(f"tex/preamble/{ctx.author.id}.tex"):
            with open(f"tex/preamble/{ctx.author.id}.tex", "a") as fc:
                fc.write(f"\n{code}")
        else:
            shutil.copyfile(
                f"tex/preamble/default/default.tex", f"tex/preamble/{ctx.author.id}.tex"
            )
            with open(f"tex/preamble/{ctx.author.id}.tex", "a") as fd:
                fd.write(f"\n{code}")
        await ctx.send(
            embed=discord.Embed(
                description=f"Your preamble has been updated. View it with `{ctx.prefix}preamble`.",
                color=green,
            )
        )


async def setup(bot):
    await bot.add_cog(pdfTeX(bot))
