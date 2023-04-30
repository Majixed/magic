import os
import ast
import json
import asyncio
import discord
import inspect
import datetime
import subprocess

from typing import Union
from discord.ext import commands
from conf.var import emo_del, light_gray, green, red, react_timeout


# Helper function for eval command
def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class Utility(commands.Cog, description="Utility commands (admin only)"):
    def __init__(self, bot):
        self.bot = bot

    # Upload a file
    @commands.command(name="upload", brief="Upload a file to discord")
    @commands.is_owner()
    async def upload_(self, ctx, *, filename):
        """Uploads a file to the current discord channel, takes the path to the file as an argument"""

        await ctx.send(file=discord.File(filename))

    # Delete a message by ID
    @commands.command(name="delete", brief="Delete a message by its ID")
    @commands.is_owner()
    async def delete_(self, ctx, channel_id: int, message_id: int):
        """Deletes a specific message, takes the channel ID and the message ID as arguments"""

        channel = self.bot.get_channel(channel_id)
        msg = await channel.fetch_message(message_id)
        await msg.delete()
        await ctx.send(
            embed=discord.Embed(
                description="The requested message has been deleted", color=green
            ),
            delete_after=5,
        )

    # Send a message to a specific channel
    @commands.command(name="send", brief="Send a message to a specific channel")
    @commands.is_owner()
    async def send_(self, ctx, channel_id: int, *, message):
        """Sends a message to a specific channel, takes the channel ID and message content as arguments"""

        channel = self.bot.get_channel(channel_id)
        await channel.send(message)
        await ctx.send(
            embed=discord.Embed(description="Your message has been sent", color=green)
        )

    # Evaluate a python expression
    @commands.command(name="eval", brief="Evaluate a python expression")
    @commands.is_owner()
    async def eval_(self, ctx, *, code):
        """Evaluates a python expression, takes a code as an argument"""

        fn_name = "_eval_expr"

        code = code.strip("` ")
        code = "\n".join(f"    {i}" for i in code.splitlines())

        body = f"async def {fn_name}():\n{code}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        insert_returns(body)

        env = {
            "bot": ctx.bot,
            "discord": discord,
            "commands": commands,
            "ctx": ctx,
            "__import__": __import__,
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        result = await eval(f"{fn_name}()", env)
        await ctx.send(f"```\n{result}\n```")

    # Run shell commands
    @commands.command(
        name="shell",
        aliases=["sh", "bash"],
        brief="Send commands to the shell for execution",
    )
    @commands.is_owner()
    async def shell_(self, ctx, *, command):
        """Sends commands to the shell for execution, takes a string of commands as an argument"""

        with subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            executable="/bin/bash",
        ) as p:
            out = p.communicate()[0].decode("utf-8")
            err = p.communicate()[1].decode("utf-8")
            ret = p.returncode

            sh_color = light_gray if ret == 0 else red
            embed_sh = discord.Embed(color=sh_color)
            embed_sh.add_field(
                name="stdin", value=f"```sh\n{command}\n```", inline=False
            )
            embed_sh.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            if out:
                embed_sh.add_field(
                    name="stdout", value=f"```\n{out[:1016]}\n```", inline=False
                )
            if err:
                embed_sh.add_field(
                    name="stderr", value=f"```\n{err[:1016]}\n```", inline=False
                )
            embed_sh.set_footer(text=f"process returned with exit status {ret}")
        sh_out = await ctx.send(embed=embed_sh)
        await sh_out.add_reaction(emo_del)

        def check(reaction, user):
            return reaction.message.id == sh_out.id and user == ctx.author

        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=react_timeout, check=check
                )

                if str(reaction.emoji) == emo_del:
                    await sh_out.delete()
                    break

            except asyncio.TimeoutError:
                if ctx.channel.type != discord.ChannelType.private:
                    try:
                        await sh_out.clear_reactions()
                    except discord.Forbidden:
                        pass
                break

    # Load an extension
    @commands.command(name="load", brief="Load an extension")
    @commands.is_owner()
    async def load_(self, ctx, *, extension):
        """Loads an extension (module) of the bot, takes the extension name as an argument"""

        await self.bot.load_extension(f"cogs.{extension}")
        await ctx.send(
            embed=discord.Embed(
                description=f"Extension `{extension}` successfully loaded", color=green
            )
        )

    # Unload an extension
    @commands.command(name="unload", brief="Unload an extension")
    @commands.is_owner()
    async def unload_(self, ctx, *, extension):
        """Unloads an extension (module) of the bot, takes the extension name as an argument"""

        await self.bot.unload_extension(f"cogs.{extension}")
        await ctx.send(
            embed=discord.Embed(
                description=f"Extension `{extension}` successfully unloaded",
                color=green,
            )
        )

    # Reload an extension
    @commands.command(name="reload", brief="Reload an extension")
    @commands.is_owner()
    async def reload_(self, ctx, *, extension):
        """Reloads an extension (module) of the bot, takes the extension name as an argument"""

        await self.bot.reload_extension(f"cogs.{extension}")
        await ctx.send(
            embed=discord.Embed(
                description=f"Extension `{extension}` successfully reloaded",
                color=green,
            )
        )

    # Reload all extensions
    @commands.command(name="reboot", brief="Reload all extensions")
    @commands.is_owner()
    async def reboot_(self, ctx):
        """Reloads all extensions (modules) of the bot, takes no arguments"""

        for filename in os.listdir("cogs"):
            if filename.endswith(".py"):
                await self.bot.reload_extension(f"cogs.{filename[:-3]}")
        await ctx.send(
            embed=discord.Embed(
                description="All extensions successfully reloaded", color=green
            )
        )

    # Add a bot administrator
    @commands.command(name="addadmin", brief="Add a bot administrator")
    @commands.is_owner()
    async def addadmin_(self, ctx, user: Union[int, discord.User]):
        """Adds a user to the bot administrators, takes the user ID as an argument"""

        if isinstance(user, int):
            userid = user
        elif isinstance(user, discord.User):
            userid = user.id
        username = self.bot.get_user(userid)

        with open("admins.json", "r") as json_read:
            admin_data = json.load(json_read)
        if userid in admin_data["botAdmin"]:
            return await ctx.send(
                embed=discord.Embed(
                    description=f"{username} is already an admin", color=red
                )
            )
        admin_data["botAdmin"] += [userid]

        with open("admins.json", "w") as json_write:
            json.dump(admin_data, json_write, indent=4)

        await ctx.send(
            embed=discord.Embed(description=f"{username} is now an admin", color=green)
        )

    # Remove a bot administrator
    @commands.command(name="removeadmin", brief="Remove a bot administrator")
    @commands.is_owner()
    async def removeadmin_(self, ctx, user: Union[int, discord.User]):
        """Removes a user from the bot administrators, takes the user ID as an argument"""

        if isinstance(user, int):
            userid = user
        elif isinstance(user, discord.User):
            userid = user.id
        username = self.bot.get_user(userid)
        with open("admins.json", "r") as json_read:
            admin_data = json.load(json_read)
        if userid not in admin_data["botAdmin"]:
            return await ctx.send(
                embed=discord.Embed(
                    description=f"{username} is not already an admin", color=red
                )
            )
        admin_data["botAdmin"].remove(userid)

        with open("admins.json", "w") as json_write:
            json.dump(admin_data, json_write, indent=4)

        await ctx.send(
            embed=discord.Embed(
                description=f"{username} is no longer an admin", color=green
            )
        )

    # Get a list of all the guilds the bot is in
    @commands.command(
        name="showguilds", brief="Show all guilds where the bot is present"
    )
    @commands.is_owner()
    async def showguilds_(self, ctx):
        """Lists all the guilds the bot is present in, takes no arguments"""

        g_list = []
        for guild in self.bot.guilds:
            g_list.append(guild.name)
        maxlen = int(len(max(g_list, key=len, default="")))

        g_disp = []
        for guild in self.bot.guilds:
            g_disp.append(f"{guild.name:<{maxlen}} ({guild.id})")
        g_out = "\n".join(g_disp)
        await ctx.send(
            embed=discord.Embed(
                title="List of my guilds",
                description=f"```\n{g_out}\n```",
                color=light_gray,
            )
        )

    # Make the bot leave a guild
    @commands.command(name="leaveguild", brief="Leave the specified guild")
    @commands.is_owner()
    async def leaveguild_(self, ctx, guildid: int):
        """Leaves the specified guild, takes the guild ID as an argument"""

        guild = self.bot.get_guild(guildid)
        await guild.leave()
        await ctx.send(
            embed=discord.Embed(description=f"Left guild {guild}", color=green)
        )

    # Shut down the bot
    @commands.command(
        name="shutdown", aliases=["poweroff", "halt"], brief="Shut down the bot"
    )
    @commands.is_owner()
    async def shutdown_(self, ctx):
        """Disconnects the bot from discord, takes no arguments"""

        await ctx.send(
            embed=discord.Embed(description="Shutting down, goodbye", color=green)
        )
        print(
            f"\n{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Connection closed"
        )
        await self.bot.close()


async def setup(bot):
    await bot.add_cog(Utility(bot))
