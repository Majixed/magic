import discord
import datetime
import subprocess

from discord.ext import commands
from conf.var import (
        bot_owner,
        embed_noowner
        )

class Programming(commands.Cog, description="Compile code using various programming languages"):
    def __init__(self, bot):
        self.bot = bot

    # Compile Python code
    @commands.command(name="python", aliases=["py"], brief="Compile Python code")
    async def python_(self, ctx, *, code):
        """Compiles python code, takes a string of code as an argument"""

        if ctx.author.id not in bot_owner:
            return await ctx.send(embed=embed_noowner)
        async with ctx.typing():
            with open(f"prog/python/{ctx.author.id}.py", "w") as f:
                f.write(code)
            with subprocess.Popen(["python3", f"prog/python/{ctx.author.id}.py"], \
                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
                out = p.communicate()[0].decode("utf-8")
                await ctx.send(f"```\n{out}\n```")

    # Compile JavaScript code
    @commands.command(name="javascript", aliases=["js"], brief="Compile JavaScript code")
    async def javascript_(self, ctx, *, code):
        """Compiles JavaScript code, takes a string of code as an argument"""

        if ctx.author.id not in bot_owner:
            return await ctx.send(embed=embed_noowner)
        async with ctx.typing():
            with open(f"prog/javascript/{ctx.author.id}.js", "w") as f:
                f.write(code)
            with subprocess.Popen(["jsc", f"prog/javascript/{ctx.author.id}.js"], \
                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as p:
                out = p.communicate()[0].decode("utf-8")
                await ctx.send(f"```\n{out}\n```")

    # Compile C code
    @commands.command(name="clang", aliases=["cc"], brief="Compile C code")
    async def clang_(self, ctx, *, code):
        """Compiles C code, takes a string of code as an argument"""

        if ctx.author.id not in bot_owner:
            return await ctx.send(embed=embed_noowner)
        async with ctx.typing():
            subprocess.call(f"rm -rf prog/clang/{ctx.author.id}")
            subprocess.call(f"mkdir prog/clang/{ctx.author.id}")
            subprocess.call(f"cd prog/clang/{ctx.author.id}")
            with open(f"{ctx.author.id}.c", "w") as f:
                f.write(code)
            subprocess.call(f"clang -o {ctx.author.id}.out {ctx.author.id}.c > {ctx.author.id}.log 2>&1")
            await ctx.send(f"```\n{subprocess.getoutput(f'cat {ctx.author.id}.log')}\n\n{subprocess.getoutput(f'{ctx.author.id}.out')}\n```")
            subprocess.call(f"rm -f {ctx.author.id}.out")
            subprocess.call("cd ../../..")

async def setup(bot):
    await bot.add_cog(Programming(bot))
