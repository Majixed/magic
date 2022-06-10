import sys
import discord
import traceback

from discord.ext import commands
from conf.var import red

class ErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Basic error handler implementation
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, "on_error"):
            return

        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(embed=discord.Embed(description="This command is currently disabled, try again later", color=red))

        elif isinstance(error, commands.NotOwner):
            await ctx.send(embed=discord.Embed(description="You must be a bot owner to use this command", color=red))

        elif isinstance(error, commands.MessageNotFound):
            await ctx.send(embed=discord.Embed(description="Couldn't find the requested message in that channel", color=red))

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(embed=discord.Embed(description="Couldn't find the requested member", color=red))

        elif isinstance(error, commands.GuildNotFound):
            await ctx.send(embed=discord.Embed(description="Couldn't find the requested guild", color=red))

        elif isinstance(error, commands.UserNotFound):
            await ctx.send(embed=discord.Embed(description="Couldn't find the requested user", color=red))

        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send(embed=discord.Embed(description="Couldn't find the requested channel", color=red))

        elif isinstance(error, commands.ChannelNotReadable):
            await ctx.send(embed=discord.Embed(description="Unable to view the requested channel, please check my permissions", color=red))

        elif isinstance(error, commands.CheckAnyFailure):
            await ctx.send(embed=discord.Embed(description="You must be a bot admin to run this command", color=red))

        elif isinstance(error, commands.MissingRequiredArgument):

            if ctx.command.qualified_name in ["tex", "luatex", "python", "javascript", "clang"]:
                await ctx.send(embed=discord.Embed(description="Couldn't find any code to process", color=red))

            elif ctx.command.qualified_name in ["appendpreamble", "appendluapreamble"]:
                await ctx.send(embed=discord.Embed(description="Couldn't find any code that I can add to your preamble", color=red))

            elif ctx.command.qualified_name == "sh":
                await ctx.send(embed=discord.Embed(description="Couldn't find any commands to process", color=red))

            elif ctx.command.qualified_name == "calc":
                await ctx.send(embed=discord.Embed(description="Couldn't find an expression to calculate", color=red))

        else:
            embed=discord.Embed(color=red)
            embed.add_field(name="An error occurred", value=f"```\n{error}\n```", inline=False)
            await ctx.send(embed=embed)
            print("Ignoring exception in command {}:".format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
