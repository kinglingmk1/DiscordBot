from logging import ERROR, log
import os
import asyncio
import re
import subprocess
import discord
from discord.ext import commands

from util import (
    clean_filename,
    decode_subprocess_output,
    getFFMPEGPath,
    getIMGPath,
    intgrated,
    mainPath,
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
    # --- Initial Checks ---
    if ctx.author.voice is None:
        await ctx.send("> You need to be in a voice channel to use this command.")
        return

    if ctx.voice_client is None:
        try:
            await ctx.author.voice.channel.connect()
        except Exception as e:
            await ctx.send(f"> Failed to connect to your voice channel: {e}")
            return

    if blacklist(url):
        await _send_blacklist_warning(ctx)
        return

    if not url.startswith(("https://www.youtube.com/watch", "https://youtu.be/")):
        await ctx.send("> Please provide a valid YouTube URL.")
        return

    # --- Determine yt-dlp Executable Path ---
    if os.name == "nt":  # Windows
        ytdlp_executable = os.path.join(mainPath(), "yt-dlp.exe")
    else:  # Linux/Unix
        ytdlp_executable = os.path.join(mainPath(), "yt-dlp_linux")

    # --- Handle Playlist ---
    if "list=" in url:
        await _handle_playlist(ctx, url, ytdlp_executable)
        return  # Exit after handling playlist

    # --- Handle Single Video ---
    await _handle_single_video(ctx, url, ytdlp_executable)


# --- Helper Functions ---


async def _send_blacklist_warning(ctx: commands.Context):
    """Sends the blacklist warning image."""
    try:
        img_path = os.path.join(getIMGPath(), "對健康不好喔_2-Cmch--Fa.webp")
        await ctx.send(file=discord.File(img_path))
    except Exception as e:
        log(ERROR, f"Error sending blacklist image: {e}")


async def _send_error(ctx: commands.Context, message: str, error_details: str = ""):
    """Sends a generic error message."""
    await ctx.send(message)
    if error_details:
        log(ERROR, error_details)  # Log details server-side


async def _run_ytdlp(executable: str, *args) -> tuple[str, str]:
    """Runs yt-dlp asynchronously and returns stdout and stderr decoded."""
    try:
        process = await asyncio.create_subprocess_exec(
            executable,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode, executable, output=stderr.decode()
            )

        return decode_subprocess_output(stdout), decode_subprocess_output(stderr)
    except Exception as e:
        raise e  # Re-raise for handling in calling function


async def _get_video_title(executable: str, url: str) -> str:
    """Fetches the title of a video/playlist item."""
    try:
        stdout, _ = await _run_ytdlp(executable, "--get-title", url)
        return stdout.strip()
    except Exception as e:
        log(ERROR,f"Error getting title for {url}: {e}")
        raise e


async def _play_audio(ctx: commands.Context, clean_title: str, display_title: str):
    """Handles the actual playback of an audio file."""
    try:
        # if hardresetState: # Check reset state before playing
        #     return

        # Stop any currently playing audio
        vc = ctx.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()

        # Wait for stop to complete if needed (usually quick)
        # while vc and vc.is_playing():
        #     await asyncio.sleep(0.1)

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


async def _download_video(
    executable: str, clean_title: str, url: str, playlist_item: str = None
):
    """Downloads a video or playlist item."""
    output_template = os.path.join(mainPath(), "music", f"{clean_title}.%(ext)s")
    format_option = "m4a"  # Preferred format

    args = ["-o", output_template, "-f", format_option, url]
    if playlist_item:
        args.extend(["--playlist-items", playlist_item])

    try:
        await _run_ytdlp(executable, *args)
    except subprocess.CalledProcessError as e:
        error_msg = f"> Download failed for '{clean_title}'!"
        details = f"Download failed (yt-dlp): {e}"
        if e.output:  # Check if stderr output exists
            details += f"\nDetails: {e.output}"
        raise Exception(error_msg) from e  # Re-raise with context
    except Exception as e:
        raise Exception(f"> An unexpected error occurred during download: {e}") from e


async def _handle_playlist(ctx: commands.Context, url: str, ytdlp_executable: str):
    """Handles the logic for playing a YouTube playlist."""
    try:
        # 1. Fetch Playlist Titles
        stdout, _ = await _run_ytdlp(
            ytdlp_executable, "--get-title", "--flat-playlist", url
        )
        video_titles = stdout.strip().split("\n")

        # 2. Check for Blacklisted Content in Titles
        combined_titles = "\n".join(video_titles)
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
            await ctx.send("> Playlist list is too long for a Discord message.")
        else:
            await ctx.send(message_content)

        # 4. Play Each Song in the Playlist
        music_dir = os.path.join(mainPath(), "music")
        os.makedirs(music_dir, exist_ok=True)  # Ensure music directory exists

        for i, title in enumerate(video_titles):
            # if hardresetState:
            #     return # Stop if reset is triggered

            clean_title = clean_filename(title)

            # Check if file already exists (mp3, flac, m4a)
            file_exists = any(
                os.path.exists(os.path.join(music_dir, f"{clean_title}.{ext}"))
                for ext in ["mp3", "flac", "m4a"]
            )

            if not file_exists:
                # Download the specific playlist item
                await _download_video(ytdlp_executable, clean_title, url, str(i + 1))

            # Play the audio
            await _play_audio(ctx, clean_title, title)

    except subprocess.CalledProcessError:
        await _send_error(
            ctx,
            "> Failed to process the playlist.",
            "Playlist processing failed (yt-dlp error).",
        )
    except Exception as e:
        await _send_error(
            ctx, f"> Error handling playlist: {e}", f"_handle_playlist error: {e}"
        )


async def _handle_single_video(ctx: commands.Context, url: str, ytdlp_executable: str):
    """Handles the logic for playing a single YouTube video."""
    try:
        # 1. Get Video Title
        video_title = await _get_video_title(ytdlp_executable, url)
        clean_title = clean_filename(video_title)

        # 2. Check for Blacklisted Content in Title
        if any(
            bl in video_title for bl in ["願榮光", "Glory to Hong Kong", "Glory to HK"]
        ):
            await _send_blacklist_warning(ctx)
            return

        music_dir = os.path.join(mainPath(), "music")
        os.makedirs(music_dir, exist_ok=True)  # Ensure music directory exists

        # 3. Check if File Exists
        file_exists = any(
            os.path.exists(os.path.join(music_dir, f"{clean_title}.{ext}"))
            for ext in ["mp3", "flac", "m4a"]
        )

        # 4. Download if Necessary
        if not file_exists:
            await _download_video(ytdlp_executable, clean_title, url)

        # 5. Play the Audio
        await _play_audio(ctx, clean_title, video_title)

    except subprocess.CalledProcessError:
        await _send_error(
            ctx,
            "> Failed to process the video.",
            "Single video processing failed (yt-dlp error).",
        )
    except Exception as e:
        await _send_error(
            ctx,
            f"> Error handling single video: {e}",
            f"_handle_single_video error: {e}",
        )
