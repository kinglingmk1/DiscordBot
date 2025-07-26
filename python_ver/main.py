from command.play import MusicPlayer
from command.upload import upload
from command.yt import yt
from config import DISCORD_TOKEN
import discord
import os
from discord.ext import commands

# Import the new message handler system
from message_rules import setup_message_handler
from util import (
    getIMGPath,
)

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents, help_command=None)
client.add_command(yt)
client.add_command(upload)

# Initialize message handler
message_handler = None


@client.event
async def on_ready():
    global message_handler
    # for cog in COGS:
    #    await client.add_cog(cog)

    # Initialize the message handler with required functions
    message_handler = setup_message_handler(client=client, img_path_func=getIMGPath)
    await client.add_cog(MusicPlayer(client))

    print(f"目前登入身份 --> {client.user}" + " 使用系統: " + os.name)


@client.command()
async def join(ctx):
    """Connects the bot to the user's voice channel."""
    if not ctx.author.voice:
        return

    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)


@client.command()
async def leave(ctx):
    if ctx.author.voice is None:
        return
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I'm not in a voice channel.")


@client.command()
async def getPermission(ctx):
    # Display a button on the text channel to get permission and assign a role
    class PermissionButton(discord.ui.View):
        @discord.ui.button(label="失業救助金", style=discord.ButtonStyle.primary)
        async def button_callback(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            role = discord.utils.get(
                ctx.guild.roles, name="失業人士"
            )  # 修改成你的目標身分組名稱
            if role:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    "You have been granted permission and assigned the role!",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    "Role not found!", ephemeral=True
                )

    await ctx.send("想失業就click: ", view=PermissionButton())


def cleanup_file(path):
    try:
        # os.remove(path)
        pass
    except PermissionError:
        # The file is still in use; you can log or retry later.
        print(f"PermissionError: Could not remove {path} because it is still in use.")
    except Exception as e:
        print(f"Error cleaning up file: {e}")


@client.command()
async def help(ctx):
    help_text = (
        "Available commands:\n"
        "> !join - Join your voice channel.\n"
        "> !leave - Leave the voice channel.\n"
        "> !play <filename> - Play a music file (without extension).\n"
        "> !upload [link] / insert a file - Upload a music file or download from a link.\n"
        "> !stop - Stop the currently playing music.\n"
        "> !list - List available music files.\n"
        "> !help - Show this help message.\n"
        "> !yt <YouTube URL> - Download and play a YouTube video.\n"
        ">>> !hardreset - Restart the bot completely.\n"
        ">>> !playAll - Play all music files in the music directory.\n"
        "   !stop - Stop current play all song list and skip to next song\n"
    )
    await ctx.send(f"{help_text}", ephemeral=True)


@client.event
async def on_message(message):
    """
    Streamlined message handler using the message handler interface.
    All message response logic is now centralized in the message_handler system.
    """
    if message.author == client.user:
        return

    # Try to handle the message with our rule-based system
    if message_handler and await message_handler.handle_message(message):
        return  # Message was handled by a rule

    # If no rule handled the message, process commands
    await client.process_commands(message)

client.run(DISCORD_TOKEN)
