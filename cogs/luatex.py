import os
import json
import codecs
import discord
import asyncio
import subprocess

from typing import Union
from discord.ext import commands
from conf.func import is_admin
from conf.var import (
    emo_del,
    light_gray,
    green,
    red,
    react_timeout,
)


class LuaTeX(commands.Cog, description="The LuaTeX command suite"):
    def __init__(self, bot):
        self.bot = bot

    # Compile LuaLaTeX
    @commands.command(
        name="luatex", aliases=["lualatex"], brief="Compile LuaLaTeX code"
    )
    @commands.check_any(commands.is_owner(), is_admin)
    async def luatex_(self, ctx, *, code):
        """Compiles LuaLaTeX, takes the code as an argument"""

        async with ctx.typing():
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
            subprocess.call(f"sh tex/scripts/runluatex.sh {ctx.author.id}")
        embed_err = discord.Embed(title="", description="", color=red)
        embed_err.add_field(
            name="Compilation error",
            value=f"```\n{subprocess.getoutput(f'grep -A 10 ^! -m 2 tex/staging/{ctx.author.id}/{ctx.author.id}.log')[:1016]}\n```",
            inline=False,
        )
        embed_err.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        if not subprocess.getoutput(
            f"grep -A 10 ^! -m 2 tex/staging/{ctx.author.id}/{ctx.author.id}.log"
        ):
            pass
        else:
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
                    await out_img.clear_reactions()
                    break
                else:
                    break

    # Upload your LuaLaTeX preamble
    @commands.command(
        name="luapreamble", brief="Upload your own or another user's LuaLaTeX preamble"
    )
    @commands.check_any(commands.is_owner(), is_admin)
    async def luapreamble_(self, ctx, *, user: Union[int, discord.User] = None):
        """Uploads your own or another user's LuaLaTeX preamble to the current channel, takes the user ID as an optional argument"""

        if not user:
            try:
                p_own = await ctx.send(
                    "Your `lualatex` preamble",
                    file=discord.File(f"tex/luapreamble/{ctx.author.id}.tex"),
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
                            await p_own.clear_reactions()
                            break
                        else:
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
                    f"{username}'s `lualatex` preamble",
                    file=discord.File(f"tex/luapreamble/{userid}.tex"),
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
                            await p_usr.clear_reactions()
                            break
                        else:
                            break
            except FileNotFoundError:
                await ctx.send(
                    embed=discord.Embed(
                        description="This user does not have a custom preamble.",
                        color=red,
                    )
                )

    # Replace your LuaLaTeX preamble
    @commands.command(
        name="replaceluapreamble",
        brief="Replace your LuaLaTeX preamble with an input file or code",
    )
    @commands.check_any(commands.is_owner(), is_admin)
    async def replaceluapreamble_(self, ctx, *, code=None):
        """Replaces your LuaLaTeX preamble, takes either an input file or code as an argument"""

        if not code and ctx.message.attachments:
            if ctx.message.attachments[0].size >= 250000:
                return await ctx.send(
                    embed=discord.Embed(
                        description="Attached file is too large (over `250KB`).",
                        color=red,
                    )
                )
            else:
                await ctx.message.attachments[0].save(
                    f"tex/luapreamble/tmp/{ctx.author.id}.pre"
                )
                try:
                    c = codecs.open(
                        f"tex/luapreamble/tmp/{ctx.author.id}.pre",
                        encoding="utf-8",
                        errors="strict",
                    )
                    for line in c:
                        pass
                except UnicodeDecodeError:
                    subprocess.call(f"rm -f tex/luapreamble/tmp/{ctx.author.id}.pre")
                    await ctx.send(
                        embed=discord.Embed(
                            description="Could not decode attached file, please ensure it is encoded in `utf-8`.",
                            color=red,
                        )
                    )
                else:
                    subprocess.call(
                        f"mv tex/luapreamble/tmp/{ctx.author.id}.pre tex/luapreamble/{ctx.author.id}.tex"
                    )
                    await ctx.send(
                        embed=discord.Embed(
                            description=f"Your preamble has been updated. View it with `{ctx.prefix}luapreamble`.",
                            color=green,
                        )
                    )
        elif not code and not ctx.message.attachments:
            return await ctx.send(
                embed=discord.Embed(
                    description="You need to attach the file containing your preamble or enter the replacement text.",
                    color=red,
                )
            )
        else:
            with open(f"tex/luapreamble/{ctx.author.id}.tex", "w") as r:
                r.write(code)
            await ctx.send(
                embed=discord.Embed(
                    description=f"Your preamble has been updated. View it with `{ctx.prefix}luapreamble`.",
                    color=green,
                )
            )

    # Reset your LuaLaTeX preamble
    @commands.command(
        name="resetluapreamble", brief="Reset your LuaLaTeX preamble to the default"
    )
    @commands.check_any(commands.is_owner(), is_admin)
    async def resetluapreamble_(self, ctx):
        """Resets your LuaLaTeX preamble to the default, takes no arguments"""

        if os.path.isfile(f"tex/luapreamble/{ctx.author.id}.tex"):
            subprocess.call(f"rm -f tex/luapreamble/{ctx.author.id}.tex")
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

    # Append to your LuaLaTeX preamble
    @commands.command(
        name="appendluapreamble", brief="Append lines to your LuaLaTeX preamble"
    )
    @commands.check_any(commands.is_owner(), is_admin)
    async def appendluapreamble_(self, ctx, *, code):
        """Appends lines to your LuaLaTeX preamble, takes the code as an argument"""

        if os.path.isfile(f"tex/luapreamble/{ctx.author.id}.tex"):
            with open(f"tex/luapreamble/{ctx.author.id}.tex", "a") as fc:
                fc.write(f"\n{code}")
        else:
            subprocess.call(
                f"cp tex/luapreamble/default/default.tex tex/luapreamble/{ctx.author.id}.tex"
            )
            with open(f"tex/luapreamble/{ctx.author.id}.tex", "a") as fd:
                fd.write(f"\n{code}")
        await ctx.send(
            embed=discord.Embed(
                description=f"Your preamble has been updated. View it with `{ctx.prefix}luapreamble`.",
                color=green,
            )
        )


async def setup(bot):
    await bot.add_cog(LuaTeX(bot))
