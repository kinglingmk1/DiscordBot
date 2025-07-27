import asyncio
from pathlib import Path
from typing import Optional
import discord
from discord.ext import commands, tasks

from util import getFFMPEGPath, getMP3Path, intgrated, removefileName


class MusicPlayer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.music_extensions = {".mp3", ".flac", ".m4a"}
        self._queue = {}
        self.bot.loop.create_task(self.check_voice_channels())

    def _check_bot_in_voice_channel(self, ctx: commands.Context) -> bool:
        """Check if the user is in a voice channel."""
        return ctx.guild.voice_client is not None
    
    async def _join_voice_channel(self, ctx: commands.Context) -> discord.VoiceClient:
        """Join the voice channel of the user."""
        if ctx.author.voice.channel is not None:
            ctx.voice_client.connect(channel=ctx.author.voice.channel, reconnect=True)
            return ctx.author.voice.channel
        raise commands.CommandError("User not in voice channel")

    async def _play_audio_source(
        self,
        ctx: commands.Context,
        vc: discord.VoiceClient,
        file_path: str,
        original_name: str | None = None,
    ):
        """Play an audio source and wait for completion."""
        audio_source = discord.FFmpegPCMAudio(
            executable=getFFMPEGPath(),
            source=file_path,
            options='-filter:a "volume=0.1"',
        )

        ctx.send(f"> Playing: {original_name or removefileName(file_path)}")
        vc.play(audio_source)

    async def _pause_audio_source(self, ctx: commands.Context):
        """Pause the currently playing audio source."""
        vc = ctx.guild.voice_client
        if vc.is_playing():
            vc.pause()
            await ctx.send("> Paused the current song.")
        elif vc.is_paused():
            await ctx.send("> The song is already paused.")
        else:
            await ctx.send("> No song is currently playing.")

    async def _resume_audio_source(self, ctx: commands.Context):
        """Pause the currently playing audio source."""
        vc = ctx.guild.voice_client
        if vc.is_paused():
            vc.resume()
            await ctx.send("> Paused the current song.")
        elif vc.is_playing():
            await ctx.send("> The song is already play.")
        else:
            await ctx.send("> No song is currently playing.")

    async def _stop_audio_source(self, ctx: commands.Context):
        """Stop the currently playing audio source."""
        vc = ctx.guild.voice_client
        if vc.is_playing():
            vc.stop()
            await ctx.send("> Stopped the current song.")
        else:
            await ctx.send("> No song is currently playing.")

    def queue(self, guild: discord.Guild) -> list[str]:
        return self._queue.setdefault(guild.id, [])
    
    @commands.command(name="play")
    async def play(self, ctx: commands.Context, *, arg: str):
        """Play a specific song by name."""
        # TODO: input parser

    @commands.command(name="pause")
    async def pause(self, ctx: commands.Context):
        """Stop the currently playing music."""
        self._pause_audio_source(ctx)

    @commands.command(name="resume")
    async def resume(self, ctx: commands.Context):
        """Resume the currently playing music."""
        self._resume_audio_source(ctx)

    @commands.command(name="stop")
    async def stop(self, ctx: commands.Context):
        """Stop the currently playing music."""
        self._stop_audio_source(ctx)

    @tasks.loop(seconds=1)
    async def check_bot_need_connect(self):
        for voice_client in self.bot.voice_clients:
            if not voice_client.is_connected():
                continue
            if len(voice_client.channel.members) > 1:
                continue
            if voice_client.is_playing():
                continue
            await voice_client.disconnect(force=True)

            guild = voice_client.client.get_guild()
            if guild is not None:
                self.queue(guild).clear()
