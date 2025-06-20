import os
import codecs
import shutil
import discord
import asyncio

from typing import Union
from discord.ext import commands
from .helper.util import (
    detect_codeblock,
    compile_tex,
    reaction_check,
    user_locks,
)
from config.config import (
    emo_del,
    green,
    red,
    react_timeout,
)


class pdfTeX(commands.Cog, description="The pdfTeX command suite"):
    def __init__(self, bot):
        self.bot = bot

    def get_user_lock(self, user_id):
        if user_id not in user_locks:
            user_locks[user_id] = asyncio.Lock()
        return user_locks[user_id]

    # Compile pdfLaTeX
    @commands.command(
        name="tex",
        aliases=["latex", "pdflatex", "pdftex", "-"],
        brief="Compile pdfLaTeX code",
    )
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def tex_(self, ctx, *, code):
        """Compiles pdfLaTeX, takes the code as an argument"""

        lock = self.get_user_lock(ctx.author.id)

        output = None

        code = detect_codeblock(code, ["", "tex", "latex"])

        if ctx.invoked_with == "-":
            code = "$\\begin{gathered}\n" + code + "\n\\end{gathered}$"

        async with lock:
            result = await asyncio.gather(
                asyncio.to_thread(compile_tex, ctx.author.id, code, "runtex", "texit")
            )
            compile_err = result[0]

            if compile_err:
                output = await ctx.reply(
                    f"**Compilation error**\n```\n{compile_err[:1016]}\n```",
                    file=discord.File(
                        f"tex/staging/{ctx.author.id}/{ctx.author.id}.png"
                    ),
                    mention_author=False,
                )
            else:
                output = await ctx.reply(
                    file=discord.File(
                        f"tex/staging/{ctx.author.id}/{ctx.author.id}.png"
                    ),
                    mention_author=False,
                )
        await output.add_reaction(emo_del)

        check = reaction_check(output.id, ctx.author, emo_del)

        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=react_timeout, check=check
                )

                if str(reaction.emoji) == emo_del:
                    await output.delete()
                    break

            except asyncio.TimeoutError:
                try:
                    await output.remove_reaction(emo_del, self.bot.user)
                except discord.NotFound:
                    pass
                break

    # Upload your pdfLaTeX preamble
    @commands.command(
        name="preamble", brief="Upload your own or another user's pdfLaTeX preamble"
    )
    async def preamble_(self, ctx, *, user: Union[int, discord.User] | None):
        """Uploads your own or another user's pdfLaTeX preamble to the current channel, takes a username or user ID as an optional argument"""

        if not user:
            try:
                preamble = await ctx.reply(
                    "Your custom `pdflatex` preamble",
                    file=discord.File(f"tex/preamble/{ctx.author.id}.tex"),
                    mention_author=False,
                )
            except FileNotFoundError:
                preamble = await ctx.reply(
                    "No custom `pdflatex` preamble found, showing the default",
                    file=discord.File("tex/preamble/default/default.tex"),
                    mention_author=False,
                )
        else:
            if isinstance(user, int):
                user_id = user
            elif isinstance(user, discord.User):
                user_id = user.id
            username = await self.bot.fetch_user(user_id)
            try:
                preamble = await ctx.reply(
                    f"{username}'s custom `pdflatex` preamble",
                    file=discord.File(f"tex/preamble/{user_id}.tex"),
                    mention_author=False,
                )
            except FileNotFoundError:
                preamble = await ctx.reply(
                    f"No custom `pdflatex` preamble found for {username}, showing the default",
                    file=discord.File("tex/preamble/default/default.tex"),
                    mention_author=False,
                )
        await preamble.add_reaction(emo_del)

        check = reaction_check(preamble.id, ctx.author, emo_del)

        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=react_timeout, check=check
                )

                if str(reaction.emoji) == emo_del:
                    await preamble.delete()
                    break

            except asyncio.TimeoutError:
                try:
                    await preamble.remove_reaction(emo_del, self.bot.user)
                except discord.NotFound:
                    pass
                break

    # Replace your pdfLaTeX preamble
    @commands.command(
        name="replacepreamble",
        brief="Replace your pdfLaTeX preamble with an input file or code",
    )
    async def replacepreamble_(self, ctx, *, code=None):
        """Replaces your pdfLaTeX preamble, takes either an input file or code as an argument"""

        if not code and ctx.message.attachments:
            if ctx.message.attachments[0].size >= 1048576:
                return await ctx.reply(
                    embed=discord.Embed(
                        description="Attached file is too large (over `1MB`).",
                        color=red,
                    ),
                    mention_author=False,
                )
            await ctx.message.attachments[0].save(f"tex/preamble/{ctx.author.id}.tmp")
            try:
                codecs.open(
                    f"tex/preamble/{ctx.author.id}.tmp",
                    encoding="utf-8",
                    errors="strict",
                ).readlines()
            except UnicodeDecodeError:
                os.remove(f"tex/preamble/{ctx.author.id}.tmp")
                return await ctx.reply(
                    embed=discord.Embed(
                        description="Could not decode attached file, please ensure it is encoded in `utf-8`.",
                        color=red,
                    ),
                    mention_author=False,
                )
            shutil.move(
                f"tex/preamble/{ctx.author.id}.tmp", f"tex/preamble/{ctx.author.id}.tex"
            )
            await ctx.reply(
                embed=discord.Embed(
                    description=f"Your preamble has been updated. View it with `{ctx.prefix}preamble`.",
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
            with open(f"tex/preamble/{ctx.author.id}.tex", "w") as r:
                r.write(code)
            await ctx.reply(
                embed=discord.Embed(
                    description=f"Your preamble has been updated. View it with `{ctx.prefix}preamble`.",
                    color=green,
                ),
                mention_author=False,
            )

    # Reset your pdfLaTeX preamble
    @commands.command(
        name="resetpreamble", brief="Reset your pdfLaTeX preamble to the default"
    )
    async def resetpreamble_(self, ctx):
        """Resets your pdfLaTeX preamble to the default, takes no arguments"""

        if os.path.isfile(f"tex/preamble/{ctx.author.id}.tex"):
            os.remove(f"tex/preamble/{ctx.author.id}.tex")
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
                "tex/preamble/default/default.tex", f"tex/preamble/{ctx.author.id}.tex"
            )
            with open(f"tex/preamble/{ctx.author.id}.tex", "a") as fd:
                fd.write(f"\n{code}")
        await ctx.reply(
            embed=discord.Embed(
                description=f"Your preamble has been updated. View it with `{ctx.prefix}preamble`.",
                color=green,
            ),
            mention_author=False,
        )


async def setup(bot):
    await bot.add_cog(pdfTeX(bot))
