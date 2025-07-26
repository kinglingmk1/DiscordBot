from discord.ext import commands

from message_handler import MessageHandler


class MyGoListener(commands.Cog):
    def __init__(self, bot, message_handler: MessageHandler):
        self.bot = bot
        self.message_handler = message_handler

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.message_handler.handle_message(message)
