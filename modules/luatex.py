import os
import codecs
import shutil
import discord
import asyncio

from typing import Union
from discord.ext import commands
from config.functions import (
    detect_codeblock,
    compile_tex,
)
from config.config import (
    emo_del,
    green,
    red,
    react_timeout,
)


class LuaTeX(commands.Cog, description="The LuaTeX command suite"):
    def __init__(self, bot):
        self.bot = bot

    # Compile LuaLaTeX
    @commands.command(
        name="luatex", aliases=["lua", "lualatex", "="], brief="Compile LuaLaTeX code"
    )
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def luatex_(self, ctx, *, code):
        """Compiles LuaLaTeX, takes the code as an argument"""

        output = None

        code = detect_codeblock(code)

        if ctx.invoked_with == "=":
            code = "\\begin{gather*}\n" + code + "\n\\end{gather*}"

        result = await asyncio.gather(
            asyncio.to_thread(compile_tex, ctx.author.id, code, "runluatex")
        )
        compile_err = result[0]

        if compile_err:
            output = await ctx.reply(
                f"**Compilation error**\n```\n{compile_err[:1016]}\n```",
                file=discord.File(f"tex/staging/{ctx.author.id}/{ctx.author.id}.png"),
                mention_author=False,
            )
        else:
            output = await ctx.reply(
                file=discord.File(f"tex/staging/{ctx.author.id}/{ctx.author.id}.png"),
                mention_author=False,
            )
        await output.add_reaction(emo_del)

        def check(reaction, user):
            return (
                reaction.message.id == output.id
                and user == ctx.author
                and str(reaction.emoji) == emo_del
            )

        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=react_timeout, check=check
                )

                if str(reaction.emoji) == emo_del:
                    await output.delete()
                    break

            except asyncio.TimeoutError:
                await output.remove_reaction(emo_del, self.bot.user)
                break

    # Upload your LuaLaTeX preamble
    @commands.command(
        name="luapreamble", brief="Upload your own or another user's LuaLaTeX preamble"
    )
    async def luapreamble_(self, ctx, *, user: Union[int, discord.User] | None):
        """Uploads your own or another user's LuaLaTeX preamble to the current channel, takes a username or user ID as an optional argument"""

        if not user:
            try:
                preamble = await ctx.reply(
                    "Your custom `lualatex` preamble",
                    file=discord.File(f"tex/luapreamble/{ctx.author.id}.tex"),
                    mention_author=False,
                )
            except FileNotFoundError:
                preamble = await ctx.reply(
                    "No custom `lualatex` preamble found, showing the default",
                    file=discord.File("tex/luapreamble/default/default.tex"),
                    mention_author=False,
                )
        else:
            if isinstance(user, int):
                userid = user
            elif isinstance(user, discord.User):
                userid = user.id
            username = await self.bot.fetch_user(userid)
            try:
                preamble = await ctx.reply(
                    f"{username}'s custom `lualatex` preamble",
                    file=discord.File(f"tex/luapreamble/{userid}.tex"),
                    mention_author=False,
                )
            except FileNotFoundError:
                preamble = await ctx.reply(
                    f"No custom `lualatex` preamble found for {username}, showing the default",
                    file=discord.File("tex/luapreamble/default/default.tex"),
                    mention_author=False,
                )
        await preamble.add_reaction(emo_del)

        def check(reaction, user):
            return (
                reaction.message.id == preamble.id
                and user == ctx.author
                and str(reaction.emoji) == emo_del
            )

        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=react_timeout, check=check
                )

                if str(reaction.emoji) == emo_del:
                    await preamble.delete()
                    break

            except asyncio.TimeoutError:
                await preamble.remove_reaction(emo_del, self.bot.user)
                break

    # Replace your LuaLaTeX preamble
    @commands.command(
        name="replaceluapreamble",
        brief="Replace your LuaLaTeX preamble with an input file or code",
    )
    async def replaceluapreamble_(self, ctx, *, code=None):
        """Replaces your LuaLaTeX preamble, takes either an input file or code as an argument"""

        if not code and ctx.message.attachments:
            if ctx.message.attachments[0].size >= 250000:
                return await ctx.reply(
                    embed=discord.Embed(
                        description="Attached file is too large (over `250KB`).",
                        color=red,
                    ),
                    mention_author=False,
                )
            await ctx.message.attachments[0].save(
                f"tex/luapreamble/{ctx.author.id}.tmp"
            )
            try:
                codecs.open(
                    f"tex/luapreamble/{ctx.author.id}.tmp",
                    encoding="utf-8",
                    errors="strict",
                ).readlines()
            except UnicodeDecodeError:
                os.remove(f"tex/luapreamble/{ctx.author.id}.tmp")
                return await ctx.reply(
                    embed=discord.Embed(
                        description="Could not decode attached file, please ensure it is encoded in `utf-8`.",
                        color=red,
                    ),
                    mention_author=False,
                )
            shutil.move(f"tex/luapreamble/{ctx.author.id}.tmp", f"tex/luapreamble/{ctx.author.id}.tex")
            await ctx.reply(
                embed=discord.Embed(
                    description=f"Your preamble has been updated. View it with `{ctx.prefix}luapreamble`.",
                    color=green,
                ),
                mention_author=False,
            )
        elif code and ctx.message.attachments:
            return await ctx.reply(
                embed=discord.Embed(
                    description="Please send your code either as a message or in a file, not both.",
                    color=red,
                ),
                mention_author=False,
            )
        elif not code and not ctx.message.attachments:
            return await ctx.reply(
                embed=discord.Embed(
                    description="You need to attach the file containing your preamble or enter the replacement text.",
                    color=red,
                ),
                mention_author=False,
            )
        elif code and not ctx.message.attachments:
            with open(f"tex/luapreamble/{ctx.author.id}.tex", "w") as r:
                r.write(code)
            await ctx.reply(
                embed=discord.Embed(
                    description=f"Your preamble has been updated. View it with `{ctx.prefix}luapreamble`.",
                    color=green,
                ),
                mention_author=False,
            )

    # Reset your LuaLaTeX preamble
    @commands.command(
        name="resetluapreamble", brief="Reset your LuaLaTeX preamble to the default"
    )
    async def resetluapreamble_(self, ctx):
        """Resets your LuaLaTeX preamble to the default, takes no arguments"""

        if os.path.isfile(f"tex/luapreamble/{ctx.author.id}.tex"):
            os.remove(f"tex/luapreamble/{ctx.author.id}.tex")
            await ctx.reply(
                embed=discord.Embed(
                    description="Your preamble has been reset to the default.",
                    color=green,
                ),
                mention_author=False,
            )
        else:
            await ctx.reply(
                embed=discord.Embed(
                    description="You already have the default preamble.", color=red
                ),
                mention_author=False,
            )

    # Append to your LuaLaTeX preamble
    @commands.command(
        name="appendluapreamble", brief="Append lines to your LuaLaTeX preamble"
    )
    async def appendluapreamble_(self, ctx, *, code):
        """Appends lines to your LuaLaTeX preamble, takes the code as an argument"""

        if os.path.isfile(f"tex/luapreamble/{ctx.author.id}.tex"):
            with open(f"tex/luapreamble/{ctx.author.id}.tex", "a") as fc:
                fc.write(f"\n{code}")
        else:
            shutil.copyfile(
                f"tex/luapreamble/default/default.tex",
                f"tex/luapreamble/{ctx.author.id}.tex",
            )
            with open(f"tex/luapreamble/{ctx.author.id}.tex", "a") as fd:
                fd.write(f"\n{code}")
        await ctx.reply(
            embed=discord.Embed(
                description=f"Your preamble has been updated. View it with `{ctx.prefix}luapreamble`.",
                color=green,
            ),
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(LuaTeX(bot))
