import datetime

from discord.ext import commands
from conf.var import prefix


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Message when the bot is ready to be operated
    @commands.Cog.listener()
    async def on_ready(self):
        print(
            f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Logged in as {self.bot.user} ({self.bot.user.id})"
        )

    # Command log
    @commands.Cog.listener()
    async def on_command(self, ctx):
        print(
            "".join(
                [
                "\n",
                f"   Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
                f"   User: {ctx.author} ({ctx.author.id})\n",
                f"  {f'Guild: {ctx.guild} ({ctx.guild.id}){chr(10)}' if ctx.guild else f'Guild: DM{chr(10)}'}",
                f"{f'Channel: {ctx.channel} ({ctx.channel.id}){chr(10)}' if ctx.guild else ''}",
                f"Command: {ctx.message.content.lstrip(prefix)}\n"
                ]
            ),
            end=""
        )

    # Listen for message edits
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.bot.process_commands(after)

    # Respond to messages with uppercase "LOL"
    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author == self.bot.user:
                return
            if message.author.bot:
                return
            elif any(trigger in message.content for trigger in ("LOL", "LMAO")):
                await message.channel.send("Haha. That was so funny.")
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(Events(bot))
