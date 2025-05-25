import discord
import logging
import collections

from discord.ext import commands

logger = logging.getLogger("discord")


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.replies = collections.OrderedDict()
        self.MAX_TRACKED_MSGS = 1000

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
                    f"Command: {ctx.message.content}",
                ]
            ),
        )

    # Stuff to do when a user sends a message
    @commands.Cog.listener()
    async def on_message(self, msg):

        # Cache bot message replies for use in edited command reprocessing
        if msg.author != self.bot.user:
            return

        ref = msg.reference
        if not (ref and ref.message_id):
            return

        ref_id = ref.message_id

        if ref_id in self.replies:
            self.replies[ref_id].append(msg)
        else:
            if len(self.replies) >= self.MAX_TRACKED_MSGS:
                self.replies.popitem(last=False)
                print("  Cache: Messages cache full! Pruning objects...")
            self.replies[ref_id] = [msg]
        print(f"  Cache: {len(self.replies)} message objects cached")

    # Listen for message edits
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        # Delete bot's reply if original message was edited
        msg_id = before.id

        if msg_id in self.replies:
            to_remove = []
            for reply in self.replies[msg_id]:
                if reply.author == self.bot.user:
                    try:
                        await reply.delete()
                    except discord.NotFound:
                        pass
                    to_remove.append(reply)

            for r in to_remove:
                self.replies[msg_id].remove(r)

            if not self.replies[msg_id]:
                del self.replies[msg_id]

        await self.bot.process_commands(after)


async def setup(bot):
    await bot.add_cog(Events(bot))
