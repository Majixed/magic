import os
import json
import asyncio
import discord
import inspect
import datetime
import subprocess

from discord.ext import commands
from config.config import *

class Utility(commands.Cog, description="Utility commands (admin only)"):
    def __init__(self, bot):
        self.bot = bot

    # Upload a file
    @commands.command(name="upload", brief="Upload a file to discord")
    async def upload_(self, ctx, *, path_to_file):
        if ctx.author.id in bot_owner:
            try:
                await ctx.send(file=discord.File(f"{path_to_file}"))
            except:
                await ctx.send(embed=discord.Embed(description="I cannot find that file.", color=red))
        else:
            await ctx.send(embed=embed_noowner)

    # Delete a message by ID
    @commands.command(name="deletemsg", brief="Delete a message by its ID")
    async def deletemsg_(self, ctx, channel_id: int, message_id: int):
        if ctx.author.id in bot_owner:
            channel = self.bot.get_channel(channel_id)
            msg = await channel.fetch_message(message_id)
            await msg.delete()
        else:
            await ctx.send(embed=embed_noowner)

    # Evaluate a python expression
    @commands.command(name="eval", brief="Evaluate a python expression")
    async def eval_(self, ctx, *, command):
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {ctx.author} ({ctx.author.id}) evaluated: {command}")
        if ctx.author.id in bot_owner:
            result = eval(command)
            if inspect.isawaitable(result):
                await ctx.send(f"```\n{await result}\n```")
            else:
                await ctx.send(f"```\n{result}\n```")
        else:
            await ctx.send(embed=embed_noowner)

    # Run shell commands
    @commands.command(name="sh", brief="Send commands to the shell for execution")
    async def sh_(self, ctx, *, command):
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {ctx.author} ({ctx.author.id}) ran shell command: {command}")
        with open("admins.json", "r") as json_read:
            admin_data = json.load(json_read)
        bot_admin = admin_data["botAdmin"]

        if ctx.author.id in bot_owner or ctx.author.id in bot_admin:
            async with ctx.typing():
                with subprocess.Popen(command, \
                        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
                    out = p.communicate()[0].decode("utf-8")
                    err = p.communicate()[1].decode("utf-8")
                    ret = p.returncode

                    sh_color = light_gray if ret == 0 else red
                    embed_sh = discord.Embed(color=sh_color)
                    embed_sh.add_field(name="stdin", value=f"```sh\n{command}\n```", inline=False)
                    embed_sh.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                    if out:
                        embed_sh.add_field(name="stdout", value=f"```\n{out[:1016]}\n```", inline=False)
                    if err:
                        embed_sh.add_field(name="stderr", value=f"```\n{err[:1016]}\n```", inline=False)
                    if ret == 0:
                        embed_sh.set_footer(text=f"process completed with exit status {ret}")
                    else:
                        embed_sh.set_footer(text=f"process errored out with exit status {ret}")
            sh_out = await ctx.send(embed=embed_sh)
            await sh_out.add_reaction(emo_del)

            def check(reaction, user):
                return reaction.message.id == sh_out.id and user == ctx.author

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=react_timeout, check=check)

                    if str(reaction.emoji) == emo_del:
                        await sh_out.delete()
                        break

                except asyncio.TimeoutError:
                    await sh_out.clear_reactions()
                    break
        else:
            await ctx.send(embed=embed_noowner)

    # Run dash shell commands
    @commands.command(name="dash", brief="Send commands to the dash shell for execution")
    async def dash_(self, ctx, *, command):
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {ctx.author} ({ctx.author.id}) ran shell command (dash): {command}")
        with open("admins.json", "r") as json_read:
            admin_data = json.load(json_read)
        bot_admin = admin_data["botAdmin"]

        if ctx.author.id in bot_owner or ctx.author.id in bot_admin:
            async with ctx.typing():
                with subprocess.Popen(["dash", "-c", command], \
                        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
                    out = p.communicate()[0].decode("utf-8")
                    err = p.communicate()[1].decode("utf-8")
                    ret = p.returncode

                    sh_color = light_gray if ret == 0 else red
                    embed_sh = discord.Embed(color=sh_color)
                    embed_sh.add_field(name="stdin", value=f"```sh\n{command}\n```", inline=False)
                    embed_sh.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                    if out:
                        embed_sh.add_field(name="stdout", value=f"```\n{out[:1016]}\n```", inline=False)
                    if err:
                        embed_sh.add_field(name="stderr", value=f"```\n{err[:1016]}\n```", inline=False)
                    if ret == 0:
                        embed_sh.set_footer(text=f"process completed with exit status {ret}")
                    else:
                        embed_sh.set_footer(text=f"process errored out with exit status {ret}")
            sh_out = await ctx.send(embed=embed_sh)
            await sh_out.add_reaction(emo_del)

            def check(reaction, user):
                return reaction.message.id == sh_out.id and user == ctx.author

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=react_timeout, check=check)

                    if str(reaction.emoji) == emo_del:
                        await sh_out.delete()
                        break

                except asyncio.TimeoutError:
                    await sh_out.clear_reactions()
                    break
        else:
            await ctx.send(embed=embed_noowner)

    # Load an extension
    @commands.command(name="load", brief="Load an extension")
    async def load_(self, ctx, *, extension):
        if ctx.author.id in bot_owner:
            try:
                self.bot.load_extension(f"cogs.{extension}")
                await ctx.send(embed=discord.Embed(description=f"Extension `{extension}` successfully loaded", color=green))
            except Exception as e:
                embed_ext_err = discord.Embed(color=red)
                embed_ext_err.add_field(name="Error", value=f"```\n{e}\n```", inline=False)
                await ctx.send(embed=embed_ext_err)
        else:
            await ctx.send(embed=embed_noowner)

    # Unload an extension
    @commands.command(name="unload", brief="Unload an extension")
    async def unload_(self, ctx, *, extension):
        if ctx.author.id in bot_owner:
            try:
                self.bot.unload_extension(f"cogs.{extension}")
                await ctx.send(embed=discord.Embed(description=f"Extension `{extension}` successfully unloaded", color=green))
            except Exception as e:
                embed_ext_err = discord.Embed(color=red)
                embed_ext_err.add_field(name="Error", value=f"```\n{e}\n```", inline=False)
                await ctx.send(embed=embed_ext_err)
        else:
            await ctx.send(embed=embed_noowner)

    # Reload an extension
    @commands.command(name="reload", brief="Reload an extension")
    async def reload_(self, ctx, *, extension):
        if ctx.author.id in bot_owner:
            try:
                self.bot.reload_extension(f"cogs.{extension}")
                await ctx.send(embed=discord.Embed(description=f"Extension `{extension}` successfully reloaded", color=green))
            except Exception as e:
                embed_ext_err = discord.Embed(color=red)
                embed_ext_err.add_field(name="Error", value=f"```\n{e}\n```", inline=False)
                await ctx.send(embed=embed_ext_err)
        else:
            await ctx.send(embed=embed_noowner)

    # Reload all extensions
    @commands.command(name="reboot", brief="Reload all extensions")
    async def reboot_(self, ctx):
        if ctx.author.id in bot_owner:
            try:
                for filename in os.listdir("./cogs"):
                    if filename.endswith(".py"):
                        self.bot.reload_extension(f"cogs.{filename[:-3]}")
            except Exception as e:
                await ctx.send(f"```\n{e}\n```")
            else:
                await ctx.send(embed=discord.Embed(description="All extensions successfully reloaded", color=green))
        else:
            await ctx.send(embed=embed_noowner)

    # Add a bot administrator
    @commands.command(name="addadmin", brief="Add a bot administrator")
    async def addadmin_(self, ctx, userid: int):
        if ctx.author.id in bot_owner:
            try:
                username = await self.bot.fetch_user(userid)
            except Exception as e:
                return await ctx.send(f"```\n{e}\n```")
            try:
                with open("admins.json", "r") as json_read:
                    admin_data = json.load(json_read)
            except Exception as e:
                print(e)
                await ctx.send(f"```\n{e}\n```")
            try:
                if userid in admin_data["botAdmin"]:
                    return await ctx.send(embed=discord.Embed(description="This user is already an admin", color=red))
                admin_data["botAdmin"] += [userid]

                with open("admins.json", "w") as json_write:
                    json.dump(admin_data, json_write, indent=4)

                await ctx.send(embed=discord.Embed(description=f"{username} (`{userid}`) is now an admin", color=green))
            except Exception as e:
                print(e)
                await ctx.send(f"```\n{e}\n```")
        else:
            await ctx.send(embed=embed_noowner)

    # Remove a bot administrator
    @commands.command(name="removeadmin", brief="Remove a bot administrator")
    async def removeadmin_(self, ctx, userid: int):
        if ctx.author.id in bot_owner:
            try:
                username = await self.bot.fetch_user(userid)
            except Exception as e:
                return await ctx.send(f"```\n{e}\n```")
            try:
                with open("admins.json", "r") as json_read:
                    admin_data = json.load(json_read)
            except Exception as e:
                print(e)
                await ctx.send(f"```\n{e}\n```")
            try:
                if userid not in admin_data["botAdmin"]:
                    return await ctx.send(embed=discord.Embed(description="This user is not already an admin", color=red))
                admin_data["botAdmin"].remove(userid)

                with open("admins.json", "w") as json_write:
                    json.dump(admin_data, json_write, indent=4)

                await ctx.send(embed=discord.Embed(description=f"{username} (`{userid}`) is no longer an admin", color=green))
            except Exception as e:
                print(e)
                await ctx.send(f"```\n{e}\n```")
        else:
            await ctx.send(embed=embed_noowner)

    # Get a list of all the guilds the bot is in
    @commands.command(name="showguilds", brief="Show all guilds where the bot is present")
    async def showguilds_(self, ctx):
        if ctx.author.id in bot_owner:
            glist = ""
            for guild in self.bot.guilds:
                glist += f"{guild.name} ({guild.id})\n"
            await ctx.send(embed=discord.Embed(title="List of my guilds", description=f"```\n{glist}\n```", color=light_gray))
        else:
            await ctx.send(embed=embed_noowner)

    # Shut down the bot
    @commands.command(name="shutdown", aliases=["poweroff", "halt"], brief="Shut down the bot completely")
    async def shutdown_(self, ctx):
        if ctx.author.id in bot_owner:
            await ctx.send(embed=embed_shutdown)
            await self.bot.close()
            print("")
            print("-----------------")
            print("Connection closed")
        else:
            await ctx.send(embed=embed_noowner)

def setup(bot):
    bot.add_cog(Utility(bot))
