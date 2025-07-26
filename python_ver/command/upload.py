from logging import ERROR, log
import aiohttp
import discord
from discord.ext import commands

from util import getIMGPath, getMP3Path

# Constants for banned phrases
BANNED_PHRASES = {"願榮光", "Glory to Hong Kong", "Glory to HK"}
WARNING_IMAGE_PATH = getIMGPath() + "對健康不好喔_2-Cmch--Fa.webp"


@commands.command()
async def upload(ctx, link: str = None):
    if ctx.author.voice is None:
        return

    file_name = None
    save_path = None

    # Handle file attachment
    if ctx.message.attachments:
        file = ctx.message.attachments[0]
        file_name = file.filename
        save_path = getMP3Path() + file_name
        await file.save(save_path)

    # Handle link download
    elif link:
        file_name = link.split("/")[-1] or "downloaded_file.mp3"
        file_name = file_name.replace("%20", " ")

        # Check for banned phrases in filename
        if any(phrase in file_name for phrase in BANNED_PHRASES):
            await ctx.send(file=discord.File(WARNING_IMAGE_PATH))
            return

        await ctx.send("Downloading file from link...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(link) as response:
                    if response.status != 200:
                        await ctx.send(
                            "Failed to download the file from the provided link."
                        )
                        return
                    data = await response.read()
        except Exception as e:
            await ctx.send("An error occurred while downloading the file.")
            log(ERROR, f"Download failed: {e}")
            return

        save_path = getMP3Path() + file_name
        try:
            with open(save_path, "wb") as f:
                f.write(data)
        except Exception as e:
            await ctx.send("Failed to save the downloaded file.")
            log(ERROR, f"[ERROR] File save failed: {e}")
            return

    # No file or link provided
    else:
        await ctx.send(
            "Please attach an audio file or provide a download link to upload."
        )
        return
