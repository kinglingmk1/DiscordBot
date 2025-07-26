import asyncio
from pathlib import Path
from typing import Optional
import discord
from discord.ext import commands

from util import getFFMPEGPath, getMP3Path, intgrated, removefileName


class MusicPlayer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.lock = asyncio.Lock()
        self.music_extensions = {".mp3", ".flac", ".m4a"}
        self.bot.loop.create_task(self.check_voice_channels())

    @commands.command(name="playAll")
    async def play_all(self, ctx: commands.Context):
        """Play all music files in the music directory."""
        music_dir = Path(getMP3Path())
        files = [
            f for f in music_dir.iterdir() if f.suffix.lower() in self.music_extensions
        ]

        if not files:
            await ctx.send("> No music files found.")
            return

        vc = await self._ensure_voice_connection(ctx)
        if vc is None:
            return

        async with self.lock:
            try:
                for file in files:
                    await self._play_single_file(ctx, vc, file)
                await ctx.send("> End playing all music files.")
            except Exception as e:
                await ctx.send(f"> Error occurred while playing: {e}")
                raise

    @commands.command(name="play")
    async def play(self, ctx: commands.Context, *, arg: str):
        """Play a specific song by name."""
        vc = await self._ensure_voice_connection(ctx)
        if vc is None:
            return

        arg_clean = arg.strip('"')
        file_path = intgrated(arg_clean)

        if file_path is None:
            await ctx.send("> No such song in storage.")
            return

        async with self.lock:
            try:
                await self._play_audio_source(ctx, vc, str(file_path), arg_clean)
            except Exception as e:
                await ctx.send(f"> Error playing song: {e}")
                raise

    @commands.command(name="stop")
    async def stop(self, ctx: commands.Context):
        """Stop the currently playing music."""
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await ctx.send("Stopped the music.")
        else:
            await ctx.send("No music is currently playing.")

    @commands.command(name="list")
    async def list_songs(self, ctx: commands.Context):
        """List all available music files."""
        music_dir = Path(getMP3Path())
        files = [
            f for f in music_dir.iterdir() if f.suffix.lower() in self.music_extensions
        ]
        names = [f.stem for f in files]

        if not names:
            await ctx.send("No music files found.")
            return

        numbered = [f"{i + 1}. {name}" for i, name in enumerate(names)]
        temp_file = Path("music_list.txt")

        try:
            temp_file.write_text("\n".join(numbered), encoding="utf-8")
            await ctx.send(file=discord.File(temp_file))
        finally:
            if temp_file.exists():
                temp_file.unlink()

    @commands.command(name="leave")
    async def leave(self, ctx: commands.Context):
        """Leave the voice channel."""
        if ctx.author.voice is None:
            await ctx.send("You need to be in a voice channel.")
            return

        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected from the voice channel.")
        else:
            await ctx.send("I'm not in a voice channel.")

    async def _ensure_voice_connection(
        self, ctx: commands.Context
    ) -> Optional[discord.VoiceClient]:
        """Ensure bot is connected to voice channel and return voice client."""
        if ctx.voice_client is not None:
            return ctx.voice_client

        if ctx.author.voice is None:
            await ctx.send("> You need to be in a voice channel.")
            return None

        return await ctx.author.voice.channel.connect()

    async def _play_single_file(
        self, ctx: commands.Context, vc: discord.VoiceClient, file_path: Path
    ):
        """Play a single music file from playAll command."""
        display_name = removefileName(file_path.name)
        await ctx.send(f"> Now playing: {display_name}")
        await self._play_audio_source(ctx, vc, str(file_path), file_path.name)

    async def _play_audio_source(
        self,
        ctx: commands.Context,
        vc: discord.VoiceClient,
        file_path: str,
        original_name: str,
    ):
        """Play an audio source and wait for completion."""
        audio_source = discord.FFmpegPCMAudio(
            executable=getFFMPEGPath(),
            source=file_path,
            options='-filter:a "volume=0.1"',
        )

        vc.play(audio_source)

        while vc.is_playing():
            await asyncio.sleep(1)

        # Check if channel is empty after playing
        await self._check_and_leave_empty_channel(vc)

    async def _check_and_leave_empty_channel(self, vc: discord.VoiceClient):
        """Leave voice channel if it's empty (only bot remains)."""
        if vc.channel and len(vc.channel.members) <= 1:
            await asyncio.sleep(2)  # Small delay to ensure playback fully stopped
            if not vc.is_playing():
                await vc.disconnect()

    async def check_voice_channels(self):
        """Background task to periodically check voice channels for emptiness."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for vc in self.bot.voice_clients:
                if isinstance(vc, discord.VoiceClient) and vc.channel:
                    # Only check if not currently playing
                    if not vc.is_playing() and len(vc.channel.members) <= 1:
                        await asyncio.sleep(5)  # Wait a bit to confirm
                        if not vc.is_playing() and len(vc.channel.members) <= 1:
                            await vc.disconnect()
            await asyncio.sleep(30)  # Check every 30 seconds
