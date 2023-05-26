import logging

from discord.ext import commands
from config.config import prefix

logger = logging.getLogger("discord")


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Message when the bot is ready to be operated
    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"Logged in as {self.bot.user} ({self.bot.user.id})")

    # Command log
    @commands.Cog.listener()
    async def on_command(self, ctx):
        logger.info(
            "\n".join(
                [
                    "Command was run:",
                    f"   User: {ctx.author} ({ctx.author.id})",
                    f"  {f'Guild: {ctx.guild} ({ctx.guild.id}){chr(10)}Channel: {ctx.channel} ({ctx.channel.id})' if ctx.guild else 'Guild: DM'}",
                    f"Command: {ctx.message.content.lstrip(prefix)}",
                ]
            ),
        )

    # Listen for message edits
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.bot.process_commands(after)

    # Respond to messages with uppercase "LOL"
    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot or msg.author == self.bot.user:
            return
        elif any(trigger in msg.content for trigger in ("LOL", "LMAO")):
            await msg.channel.send("Haha. That was so funny.")


async def setup(bot):
    await bot.add_cog(Events(bot))
