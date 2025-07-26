import logging
import os
import asyncio
import re
import subprocess
from tempfile import TemporaryFile
import discord
from discord.ext import commands
from yt_dlp import YoutubeDL

from util import (
    clean_filename,
    getFFMPEGPath,
    getIMGPath,
    getMP3Path,
    intgrated,
)


def blacklist(url):
    match = re.search(r"v=([^&]*)", url)
    return match and match.group(1) in {
        "jXZNOecZreY",
        "FXGoN6xBeD0",
        "Pe1gTPcWyds",
        "dY_hkbVQA20",
        "PmCtqVMlpgk",
    }


@commands.command()
async def yt(ctx: commands.Context, url: str):
    """
    Plays audio from a YouTube video or playlist URL in the user's voice channel.
    """
    if blacklist(url):
        await _send_blacklist_warning(ctx)
        return

    if not url.startswith(("https://www.youtube.com/watch", "https://youtu.be/")):
        await ctx.send("> Please provide a valid YouTube URL.")
        return

    # --- Handle Playlist ---
    if "list=" in url:
        await _handle_playlist(ctx, url)
        return  # Exit after handling playlist

    # --- Handle Single Video ---
    await _handle_single_video(ctx, url)


# --- Helper Functions ---


async def _send_blacklist_warning(ctx: commands.Context):
    """Sends the blacklist warning image."""
    try:
        img_path = os.path.join(getIMGPath(), "對健康不好喔_2-Cmch--Fa.webp")
        await ctx.send(file=discord.File(img_path))
    except Exception as e:
        logging.error(f"Error sending blacklist image: {e}")


async def _send_error(ctx: commands.Context, message: str, error_details: str = ""):
    """Sends a generic error message."""
    await ctx.send(message)
    if error_details:
        logging.error(error_details)  # Log details server-side

async def _get_video_title(url: str) -> str | None:
    return await asyncio.to_thread(_get_video_title_block, url)

def _get_video_title_block(url: str) -> str | None:
    """Fetches the title of a video/playlist item."""
    print(f"Fetching title for URL: {url}")
    try:
        ydl_opts = {
            "quiet": True,
            "extract_flat": True,  # Get only the title without downloading
            "force_generic_extractor": True,  # Use generic extractor for better compatibility
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get("title", None)
    except Exception as e:
        logging.error(f"Error getting title for {url}: {e}")
        raise e

async def _get_playlist_meta(url: str) -> list[tuple[str, str]]:
    return await asyncio.to_thread(_get_playlist_meta_block, url)

def _get_playlist_meta_block(url: str) -> list[tuple[str, str]]:
    """Fetches the list of video titles in a playlist."""
    try:
        ydl_opts = {
            "quiet": True,
            "extract_flat": True,  # Get only the titles without downloading
            "force_generic_extractor": True,  # Use generic extractor for better compatibility
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return [
                (video.get("title", "Unknown Title"), video.get("url", "Unknown URL"))
                for video in info.get("entries", [])
            ]
    except Exception as e:
        logging.error(f"Error getting video list for {url}: {e}")
        raise e


async def _play_audio(ctx: commands.Context, display_title: str):
    """Handles the actual playback of an audio file."""
    print(f"Playing audio for title: {display_title}")
    clean_title = clean_filename(display_title)  # Clean the title for file naming
    try:
        vc = ctx.guild.voice_client
        if vc is not None:
            # Stop any currently playing audio
            vc.stop()
        else:
            # Join the voice channel if not already connected
            if not ctx.author.voice:
                await ctx.send("> You need to be in a voice channel to play audio.")
                return
            channel = ctx.author.voice.channel
            await channel.connect()

        source_path = intgrated(clean_title)  # Get the correct file path
        ffmpeg_path = getFFMPEGPath()

        # Create and play the audio source
        audio_source = discord.FFmpegPCMAudio(
            executable=ffmpeg_path,
            source=source_path,
            options='-filter:a "volume=0.1"',  # Set volume
        )
        vc.play(audio_source)

        await ctx.send(f"> Now Playing: {display_title}")

        # Wait for the song to finish playing
        while vc and vc.is_playing():
            await asyncio.sleep(1)

    except Exception as e:
        await _send_error(
            ctx, f"> Error during playback: {e}", f"_play_audio error: {e}"
        )

async def _download_audio(url: str, title: str = None):
    return await asyncio.to_thread(_download_audio_block, url, title)

def _download_audio_block(url: str, title: str = None):
    """Downloads a video or playlist item."""

    print(f"Downloading video: {title} - {url}")
    ydl_opts = {
        "paths": {"home": getMP3Path()},
        "format": "m4a/bestaudio/best",
        "break_on_existing": True,
        "break_per_url": True,
        "writesubtitles": False,
        "outtmpl": f"{title or '%(title)s'}.%(ext)s",  # Save as title.ext
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        "postprocessors": [
            {  # Extract audio usicng ffmpeg
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }
        ],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # Download a single video
            ydl.download([url])
    except Exception as e:
        raise Exception(f"> An unexpected error occurred during download: {e}") from e


async def _handle_playlist(ctx: commands.Context, url: str):
    """Handles the logic for playing a YouTube playlist."""
    try:
        # 1. Fetch Playlist Titles
        video_metas = await _get_playlist_meta(url)
        video_titles = [meta[0] for meta in video_metas]

        # 2. Check for Blacklisted Content in Titles
        combined_titles = "\n".join()
        if any(
            bl in combined_titles
            for bl in ["願榮光", "Glory to Hong Kong", "Glory to HK"]
        ):
            await _send_blacklist_warning(ctx)
            return

        # 3. Format and Send Playlist List (if not too long)
        title_list = "\n".join(
            f"{i + 1}. {title}" for i, title in enumerate(video_titles)
        )
        message_content = f"```List of Songs:\n{title_list}\n```"
        if len(message_content) >= 2000:
            with TemporaryFile() as f:
                f.write(title_list)
                f.flush()
                await ctx.send(
                    file=discord.File(f, filename="wow ur playlist so long.txt")
                )
        else:
            await ctx.send(message_content)

        # 4. Play Each Song in the Playlist
        for [title, url] in video_metas:
            # if hardresetState:
            #     return # Stop if reset is triggered
            # Check if file already exists (mp3, flac, m4a)
            print(f"Processing: {title} - {url}")
            title = clean_filename(title)
            if any(
                os.path.exists(os.path.join(getMP3Path(), f"{title}.{ext}"))
                for ext in ["mp3", "flac", "m4a"]
            ):
                print(f"File already exists: {title}")
                continue
            await _download_audio(url, title)
            
            # Play the audio
            await _play_audio(ctx, title)
    except Exception as e:
        await _send_error(
            ctx, f"> Error handling playlist: {e}", f"_handle_playlist error: {e}"
        )


async def _handle_single_video(ctx: commands.Context, url: str):
    """Handles the logic for playing a single YouTube video."""
    try:
        # 1. Get Video Title
        video_title = await _get_video_title(url)

        # 2. Check for Blacklisted Content in Title
        if any(
            bl in video_title for bl in ["願榮光", "Glory to Hong Kong", "Glory to HK"]
        ):
            await _send_blacklist_warning(ctx)
            return

        print(f"Processing video: {video_title} - {url}")
        title = clean_filename(video_title)
        if not any(
            os.path.exists(os.path.join(getMP3Path(), f"{title}.{ext}"))
            for ext in ["mp3", "flac", "m4a"]
        ):
            await _download_audio(url, title)

        # 5. Play the Audio
        await _play_audio(ctx, video_title)
    except Exception as e:
        await _send_error(
            ctx,
            f"> Error handling single video: {e}",
            f"_handle_single_video error: {e}",
        )
