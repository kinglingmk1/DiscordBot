import discord
from discord import app_commands
from discord.ext import commands

class Join(commands.Cog):
    bot: commands.Bot

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx: commands.Context):
        channel = ctx.author.voice.channel
        await channel.connect()
        
    @commands.command()
    async def leave(self, ctx: commands.Context):
        if ctx.guild.voice_client is None:
            return await ctx.channel.send("I'm not in a voice channel")
        await ctx.guild.voice_client.disconnect()
        await ctx.channel.send("Leave the voice channel")