import discord
import os
import glob
from discord.ext import commands
from datetime import datetime
import aiohttp
#from command.join import Join
import socket
import random
import asyncio
import subprocess
import re
import sys
import torch
import asyncio
import queue
from concurrent.futures import ThreadPoolExecutor
from Qwen import ask
executor = ThreadPoolExecutor(max_workers=2)

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents, help_command=None)
#COGS = [Join(client)]
isGo = True
video_title = ""
hardresetState = False
def mainPath():
    return os.path.dirname(os.path.abspath(__file__))
def getMP3(input):
    music_dir = getMP3Path()
    mp3_path = os.path.join(music_dir, input + ".mp3")
    flac_path = os.path.join(music_dir, input + ".flac")
    m4a_path = os.path.join(music_dir, input + ".m4a")
    if os.path.exists(mp3_path):
        return mp3_path
    elif os.path.exists(flac_path):
        return flac_path
    elif os.path.exists(m4a_path):
        return m4a_path
    else:
        files = glob.glob(os.path.join(music_dir, '*.mp3')) + glob.glob(os.path.join(music_dir, '*.flac') ) + glob.glob(os.path.join(music_dir, '*.m4a'))
        for file in files:
            if input.lower() in os.path.basename(file).lower():
                return file
    return None

def getFFMPEGPath():
    # 根據操作系統返回正確的 FFmpeg 路徑
    if os.name == 'nt':  # Windows
        return mainPath() + "\\ffmpeg.exe"
    else:  # Linux/Unix
        return mainPath() + "/ffmpeg"  # 使用系統路徑中的 ffmpeg

def getMP3Path():
    if os.name == 'nt':
        return mainPath() + "\\music\\"
    else:
        return mainPath() + "/music/"

def getIMGPath():
    if os.name == 'nt':
        return mainPath() + "\\img\\"
    else:
        return mainPath() + "/img/"

def removePath(input):
    if input.startswith(getMP3Path()):
        return input[len(getMP3Path()):]
    else:
        return input
def intgrated(input):
    return getMP3Path() + removePath(getMP3(input))
def removefileName(input):
    if input.endswith('.mp3'):
        input = input[:-4]
    elif input.endswith('.flac'):
        input = input[:-5]
    elif input.endswith('.m4a'):
        input = input[:-4]
    return input

def blacklist(input):
    match input:
        case 'https://www.youtube.com/watch?v=jXZNOecZreY':
            return True
        case 'https://www.youtube.com/watch?v=FXGoN6xBeD0':
            return True
        case 'https://www.youtube.com/watch?v=Pe1gTPcWyds':
            return True
        case 'https://www.youtube.com/watch?v=dY_hkbVQA20':
            return True
        case 'https://www.youtube.com/watch?v=PmCtqVMlpgk':
            return True
    return False

@client.event
async def on_ready():
    await client.tree.sync()
    print(f"目前登入身份 --> {client.user}" + " 使用系統: " + os.name)

@client.command()
async def hardreset(ctx):
    global hardresetState
    hardresetState = True
    """Totally shutdown the bot and restart it"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    await client.close()
    abs_path = os.path.abspath(__file__)
    if os.name == 'nt':
        subprocess.Popen([os.path.join(os.path.dirname(abs_path), '..', 'run.bat')], shell=True)
    else:
        subprocess.Popen(['bash', os.path.join(os.path.dirname(abs_path), '..', 'run.sh')])
    os._exit(0)

@client.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
        else:
            await ctx.voice_client.move_to(channel)
    else:
        return
def clean_filename(filename):
    """清理檔案名稱，移除或替換特殊字元"""
    # 移除或替換有問題的字元
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)  # 移除 Windows 不允許的字元
    filename = re.sub(r'[【】「」／\\]', '', filename)  # 移除日文括號和斜線
    filename = filename.replace('！', '!')  # 替換全形驚嘆號
    filename = filename.strip()  # 移除首尾空白
    return filename

def decode_subprocess_output(output_bytes):
    """嘗試使用不同編碼解碼subprocess輸出，優先處理日文編碼"""
    # 優先嘗試日文編碼，特別是Shift_JIS和CP932
    encodings = ['shift_jis', 'cp932', 'utf-8', 'euc-jp', 'iso-2022-jp', 'cp1252', 'cp437', 'gbk', 'big5']
    
    for encoding in encodings:
        try:
            decoded = output_bytes.decode(encoding).strip()
            
            # 嘗試處理Unicode轉義序列
            try:
                # 如果包含\u轉義序列，嘗試解碼
                if '\\u' in decoded:
                    decoded = decoded.encode().decode('unicode_escape')
            except:
                pass  # 如果Unicode解碼失敗，繼續使用原始解碼結果
            
            # 檢查是否包含日文字符來驗證解碼是否正確
            if any('\u3040' <= char <= '\u309F' or  # Hiragana
                   '\u30A0' <= char <= '\u30FF' or  # Katakana  
                   '\u4E00' <= char <= '\u9FAF'     # Kanji
                   for char in decoded):
                return decoded
            # 如果沒有日文字符但解碼成功，也返回結果
            elif encoding in ['utf-8', 'shift_jis', 'cp932']:
                return decoded
        except UnicodeDecodeError:
            continue
    
    # 如果所有編碼都失敗，使用shift_jis並忽略錯誤
    result = output_bytes.decode('shift_jis', errors='ignore').strip()
    
    # 最後嘗試Unicode轉義解碼
    try:
        if '\\u' in result:
            result = result.encode().decode('unicode_escape')
    except:
        pass
    
    return result
@client.command()
async def checkytdlp(ctx):
    nt_ver = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
    linux_ver = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux"
    try:
        if os.name == 'nt':  # Windows
            #check yt-dlp exists
            if os.path.exists(mainPath() + '/yt-dlp.exe'):
                os.remove(mainPath() + '/yt-dlp.exe')
                #download latest version
                subprocess.run(['curl', '-L', nt_ver, '-o', mainPath() + '/yt-dlp.exe'], check=True)
                version_result = subprocess.run([mainPath() + '/yt-dlp.exe', '--version'], capture_output=True, text=True, check=True)
                version = version_result.stdout.strip()
        else:  # Linux/Unix
            if os.path.exists(mainPath() + '/yt-dlp_linux'):
                os.remove(mainPath() + '/yt-dlp_linux')
                #download latest version
                subprocess.run(['curl', '-L', linux_ver, '-o', mainPath() + '/yt-dlp_linux'], check=True)
                #make it executable
                os.chmod(mainPath() + '/yt-dlp_linux', 0o755)
                version_result = subprocess.run([mainPath() + '/yt-dlp_linux', '--version'], capture_output=True, text=True, check=True)
                version = version_result.stdout.strip()
    except subprocess.CalledProcessError:
        await ctx.send("> yt-dlp is not installed or not found.")
        if os.name == 'nt':
            os.remove(mainPath() + '/yt-dlp.exe')
            #download latest version
            subprocess.run(['curl', '-L', nt_ver, '-o', mainPath() + '/yt-dlp.exe'], check=True)
            version_result = subprocess.run([mainPath() + '/yt-dlp.exe', '--version'], capture_output=True, text=True, check=True)
            version = version_result.stdout.strip()
        elif os.name != 'nt':
            os.remove(mainPath() + '/yt-dlp_linux')
            #download latest version
            subprocess.run(['curl', '-L', linux_ver, '-o', mainPath() + '/yt-dlp_linux'], check=True)
            #make it executable
            os.chmod(mainPath() + '/yt-dlp_linux', 0o755)
            version_result = subprocess.run([mainPath() + '/yt-dlp_linux', '--version'], capture_output=True, text=True, check=True)
            version = version_result.stdout.strip()
    await ctx.send(f"> yt-dlp is up to date. Current version: {version}")

    

@client.command()
async def play(ctx, url: str):
    if ctx.author.voice is None:
        await ctx.send(file=discord.File(getIMGPath() + "幹嘛-CStDUUrz.webp"))
        await ctx.send("> You need to be in a voice channel.")
        return
    if not url.startswith("https://www.youtube.com/watch") and not url.startswith("https://youtu.be/"):
        await playList(ctx,arg=url)
    else:
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
        if blacklist(url):
            await ctx.send(file=discord.File(getIMGPath() + "對健康不好喔_2-Cmch--Fa.webp"))
            return
        if url.__contains__("list="): 
            try:
                if os.name == 'nt':  # Windows
                    process = await asyncio.create_subprocess_exec(
                        mainPath() + '/yt-dlp.exe',
                        '--get-title',
                        '--flat-playlist',
                        url,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                else:  # Linux/Unix
                    process = await asyncio.create_subprocess_exec(
                        mainPath() + '/yt-dlp_linux',
                        '--get-title',
                        '--flat-playlist',
                        url,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                stdout, stderr = await process.communicate()
                if process.returncode != 0:
                    if os.name == 'nt':  # Windows
                        raise subprocess.CalledProcessError(process.returncode, 'yt-dlp')
                    else:  # Linux/Unix
                        raise subprocess.CalledProcessError(process.returncode, 'yt-dlp_linux')
                
                video_title = decode_subprocess_output(stdout)
                #use array to store the title
                video_titles = video_title.split('\n')
                titleName = ""
                for i, title in enumerate(video_titles):
                    titleName += str(i + 1) + ". " + title + "\n"
                titleName += "```"

                if("願榮光" in titleName or "Glory to Hong Kong" in titleName or "Glory to HK" in titleName):
                    await ctx.send(file=discord.File(getIMGPath() + "對健康不好喔_2-Cmch--Fa.webp"))
                    return
                if(len(titleName) >= 2000):
                    await ctx.send(f"> List too long out of discord message limit")
                else:
                    await ctx.send(f"```List of Song:\n{titleName}")

                # 逐一播放每首歌
                for i, title in enumerate(video_titles):
                    clean = clean_filename(title)
                    
                    #檢查檔案是否已存在
                    if os.path.exists(mainPath() + '/music/' + clean + '.mp3') or \
                    os.path.exists(mainPath() + '/music/' + clean + '.flac') or \
                    os.path.exists(mainPath() + '/music/' + clean + '.m4a'):
                        if(hardresetState):
                            return
                        await ctx.send(f"> Now Playing: {title}")
                        vc = ctx.guild.voice_client
                        if vc.is_playing():
                            vc.stop()
                        while vc.is_playing():
                            await asyncio.sleep(1)
                        playMSG = "正在播放: " + title
                        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=playMSG))
                        vc.play(discord.FFmpegPCMAudio(executable=getFFMPEGPath(), source=intgrated(clean), options='-filter:a "volume=0.1"'))
                    else:
                        # 下載影片
                        if os.name == 'nt':  # Windows
                            process = await asyncio.create_subprocess_exec(
                                mainPath() + '/yt-dlp.exe',
                                '-o', mainPath() + '/music/' + clean + '.%(ext)s',
                                '-f', 'm4a',
                                url,
                                '--playlist-items', str(i+1),
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE
                            )
                        else:  # Linux/Unix
                            process = await asyncio.create_subprocess_exec(
                                mainPath() + '/yt-dlp_linux',
                                '-o', mainPath() + '/music/' + clean + '.%(ext)s',
                                '-f', 'm4a',
                                url,
                                '--playlist-items', str(i+1),
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE
                            )
                        stdout, stderr = await process.communicate()
                        if process.returncode != 0:
                            if os.name == 'nt':  # Windows
                                raise subprocess.CalledProcessError(process.returncode, 'yt-dlp.exe')
                            else:  # Linux/Unix
                                raise subprocess.CalledProcessError(process.returncode, 'yt-dlp_linux')
                        if(hardresetState):
                            return
                        await ctx.send(f"> Now Playing: {title}")
                        vc = ctx.guild.voice_client
                        if vc.is_playing():
                            vc.stop()
                        while vc.is_playing():
                            await asyncio.sleep(1)
                        playMSG = "正在播放: " + title
                        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=playMSG))
                        vc.play(discord.FFmpegPCMAudio(executable=getFFMPEGPath(), source=intgrated(clean), options='-filter:a "volume=0.1"'))
                    
                    # 等待當前歌曲播放完畢
                    while vc.is_playing():
                        await asyncio.sleep(1)

            except subprocess.CalledProcessError:
                print("> Download failed!")
            except Exception as e:
                await ctx.send(f"> How the fuck u make this???? : {e}")
            return
        try:
            # 先獲取影片標題
            if(os.name == 'nt'):  # Windows
                result = subprocess.run([
                    mainPath() + '/yt-dlp.exe',
                    '--get-title',
                    url
                ], capture_output=True, text=True, check=True)
            else:  # Linux/Unix
                result = subprocess.run([
                    mainPath() + '/yt-dlp_linux',
                    '--get-title',
                    url
                ], capture_output=True, text=True, check=True)
            video_title = result.stdout.strip()
            clean = clean_filename(video_title)

            if("願榮光" in clean or "Glory to Hong Kong" in clean or "Glory to HK" in clean):
                await ctx.send(file=discord.File(getIMGPath() + "對健康不好喔_2-Cmch--Fa.webp"))
                return

            #檢查檔案是否已存在
            if os.path.exists(mainPath() + '/music/' + clean + '.mp3') or \
            os.path.exists(mainPath() + '/music/' + clean + '.flac') or \
            os.path.exists(mainPath() + '/music/' + clean + '.m4a'):
                if(hardresetState):
                    return
                await ctx.send(f"> Now Playing: {video_title}")
                vc = ctx.guild.voice_client
                if vc.is_playing():
                    vc.stop()
                playMSG = "正在播放: " + video_title
                await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=playMSG))
                vc.play(discord.FFmpegPCMAudio(executable=getFFMPEGPath(), source=intgrated(clean), options='-filter:a "volume=0.1"'))
                return

            # 下載影片
            if os.name == 'nt':  # Windows
                process = await asyncio.create_subprocess_exec(
                    mainPath() + '/yt-dlp.exe',
                    '-o', mainPath() + '/music/' + clean + '.%(ext)s',
                    '-f', 'm4a',
                    url,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            else:  # Linux/Unix
                process = await asyncio.create_subprocess_exec(
                    mainPath() + '/yt-dlp_linux',
                    '-o', mainPath() + '/music/' + clean + '.%(ext)s',
                    '-f', 'm4a',
                    url,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                if os.name == 'nt':  # Windows
                    raise subprocess.CalledProcessError(process.returncode, 'yt-dlp.exe')
                else:  # Linux/Unix
                    raise subprocess.CalledProcessError(process.returncode, 'yt-dlp_linux')
            if(hardresetState):
                return
            await ctx.send(f"> Now playing: [{video_title}]({url})")
            vc = ctx.guild.voice_client
            #check is playing
            if vc.is_playing():
                vc.stop()
            while vc.is_playing():
                await asyncio.sleep(1)
            playMSG = "正在播放: " + video_title
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=playMSG))
            vc.play(discord.FFmpegPCMAudio(executable=getFFMPEGPath(),source=intgrated(clean),options='-filter:a "volume=0.1"'))
            
        except subprocess.CalledProcessError as e:
            await ctx.send("> Failed to play")
            # 檢查是否有 stderr 輸出
            if hasattr(e, 'stderr') and e.stderr:
                print(f"> Download failed! because: {e.stderr}")
            else:
                print(f"> Download failed! Return code: {e.returncode}")
        except Exception as e:
            print(f"> An error occurred: {e}")
            await ctx.send(f"> How the fuck u make this???? : {e}")

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
async def playList(ctx, *, arg):
    # Accept the entire argument, including spaces
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
    else:
        await ctx.send(file=discord.File(getIMGPath() + "幹嘛-CStDUUrz.webp"))
        await ctx.send("> You need to be in a voice channel.")
        return

    vc = ctx.guild.voice_client
    # Remove quotes, clean up filename
    arg_clean = arg.strip('"')
    if(intgrated(arg_clean) is None):
        await ctx.send("> No such that song in storage.")
        return
    playingMSG = "正在播放: " + arg_clean
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=playingMSG))
    vc.play(discord.FFmpegPCMAudio(executable=getFFMPEGPath(), source=intgrated(arg_clean), options='-filter:a "volume=0.1"'))
    await ctx.channel.send("> Now playing: " + removefileName(removePath(getMP3(arg_clean)))
    )
@client.command()
async def getPermission(ctx):
    # Display a button on the text channel to get permission and assign a role
    class PermissionButton(discord.ui.View):
        @discord.ui.button(label="失業救助金", style=discord.ButtonStyle.primary)
        async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
            role = discord.utils.get(ctx.guild.roles, name="失業人士")  # 修改成你的目標身分組名稱
            if role:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("You have been granted permission and assigned the role!", ephemeral=True)
            else:
                await interaction.response.send_message("Role not found!", ephemeral=True)

    await ctx.send("想失業就click: ", view=PermissionButton())


@client.command()
async def upload(ctx, link: str = None):
    if ctx.author.voice is None:
        return
    if ctx.message.attachments:
        file = ctx.message.attachments[0]
        file_name = file.filename
        save_path = getMP3Path() + file_name
        await file.save(save_path)
    # If no attachment, check for a link argument.
    elif link is not None:
        await ctx.send("Downloading file from link...")
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                if response.status == 200:
                    data = await response.read()
                    file_name = link.split("/")[-1] or "downloaded_file.mp3"
                    # Replace %20 with space in file name
                    file_name = file_name.replace("%20", " ")
                    if("願榮光" in file_name or "Glory to Hong Kong" in file_name or "Glory to HK" in file_name):
                        await ctx.send(file=discord.File(getIMGPath() + "對健康不好喔_2-Cmch--Fa.webp"))
                        return
                    save_path = getMP3Path() + file_name
                    with open(save_path, "wb") as f:
                        f.write(data)
                else:
                    await ctx.send("Failed to download the file from the provided link.")
                    return
    else:
        await ctx.send("Please attach an audio file or provide a download link to upload.")
        return

    # Ensure the bot is in a voice channel.
    if ctx.voice_client is None:
        if ctx.author.voice is None:
            await ctx.send("You need to be in a voice channel.")
            return
        await ctx.author.voice.channel.connect()
        
    vc = ctx.guild.voice_client
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=save_path))
    vc.play(discord.FFmpegPCMAudio(
        executable=getFFMPEGPath(),
        source=save_path,
        options='-filter:a "volume=0.1"'
    ), after=lambda e: cleanup_file(save_path))
    
    await ctx.send(f"> Now playing: {removefileName(file_name)}")

def cleanup_file(path):
    try:
        #os.remove(path)
        pass
    except PermissionError:
        # The file is still in use; you can log or retry later.
        print(f"PermissionError: Could not remove {path} because it is still in use.")
    except Exception as e:
        print(f"Error cleaning up file: {e}")

@client.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Stopped the music.")
    else:
        await ctx.send("No music is currently playing.")

@client.command()
async def playAll(ctx):
    music_dir = getMP3Path()
    files = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.flac', '.m4a'))]
    if not files:
        await ctx.send("> No music files found.")
        return

    if ctx.voice_client is None:
        if ctx.author.voice is None:
            await ctx.send("> You need to be in a voice channel.")
            return
        await ctx.author.voice.channel.connect()

    vc = ctx.guild.voice_client
    for file in files:
        file_path = os.path.join(music_dir, file)
        await ctx.send("> Now playing: " + removefileName(file))
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=removefileName(file)))
        vc.play(discord.FFmpegPCMAudio(executable=getFFMPEGPath(), source=file_path, options='-filter:a "volume=0.1"'))
        while vc.is_playing():
            await asyncio.sleep(1)
    await ctx.send("> End playing all music files.")


@client.command()
async def list(ctx):
    music_dir = getMP3Path()
    files = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.flac', '.m4a'))]
    names = [os.path.splitext(f)[0] for f in files]
    if names:
        numbered = [f"{i+1}. {name}" for i, name in enumerate(names)]
        #send as txt file
        #if len(numbered) >= 1950:
        with open("music_list.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(numbered))
        await ctx.send(file=discord.File("music_list.txt"))
            # Clean up the file after sending
        os.remove("music_list.txt")
        #else:
            #await ctx.send("```Song List:\n" + "\n".join(numbered)+ "```")
    else:
        await ctx.send("No music files found.")

@client.command()
async def help(ctx):
    help_text = (
        "Available commands:\n"
        "> !join - Join your voice channel.\n"
        "> !leave - Leave the voice channel.\n"
        "> !playList <filename> - Play a music file (without extension).\n"
        "> !upload [link] / insert a file - Upload a music file or download from a link.\n"
        "> !stop - Stop the currently playing music.\n"
        "> !list - List available music files.\n"
        "> !help - Show this help message.\n"
        "> !play <YouTube URL> - Download and play a YouTube video.\n"
        "> /ai <any string> - Ask a question to the AI.\n"
        ">>> !hardreset - Restart the bot completely.\n"
        ">>> !playAll - Play all music files in the music directory.\n"
        "   !stop - Stop current play all song list and skip to next song\n"
    )
    await ctx.send(f"{help_text}", ephemeral=True)

# Replace the queue initialization
AIqueue = []  # Change from queue.Queue() to list
isqueue = False
@client.tree.command(name="luckydraw", description="Draw a lucky stuff with customized options")
async def luckydraw_slash(interaction: discord.Interaction, username: str,options: str):
    #if options is > username add Empty option
    option_list = options.split(",")
    username_list = username.split(",")
    while len(option_list) <= len(username_list):
        option_list.append("Empty")
    results = []
    for user in username_list:
        while True:
            choice = random.choice(option_list).strip()
            if choice != "Empty":
                results.append(f"{user.strip()} got: {choice}")
                option_list.remove(choice)
                break
            else:
                results.append(f"{user.strip()} got: Nothing")
                option_list.remove(choice)
                break
    await interaction.response.send_message("🎉 Draw Results:\n" + "\n".join(results), ephemeral=True)


@client.tree.command(name="ai", description="Ask a question to the AI")
async def ai_slash(interaction: discord.Interaction, question: str):
    global isqueue, AIqueue
    
    # Defer the response as ephemeral
    await interaction.response.defer(ephemeral=True)
    
    # Add to queue - store as dictionary
    AIqueue.append({"interaction": interaction, "question": question})
    
    # Calculate initial position (queue size when added)
    initial_position = len(AIqueue)
    
    # Send initial ephemeral message
    await interaction.followup.send(f"Initializing... (Position in queue: {initial_position})", ephemeral=True)
    
    # Wait in queue - keep checking position
    last_position = initial_position
    while True:
        # Find this interaction's position in the queue
        try:
            my_position = next(i + 1 for i, item in enumerate(AIqueue) if item["interaction"].id == interaction.id)
            
            # If we're first in queue and nothing is processing, break
            if my_position == 1 and not isqueue:
                break
            
            # Update position display if changed
            if my_position != last_position:
                await interaction.edit_original_response(content=f"⏳ You're in queue position {my_position}")
                last_position = my_position
                
        except StopIteration:
            # Not in queue anymore (shouldn't happen, but just in case)
            break
            
        await asyncio.sleep(1)
    
    # Get from queue and start processing (remove first item)
    item = AIqueue.pop(0)
    isqueue = True
    
    await interaction.edit_original_response(content=f"聞著我那又熱又香脆的{torch.cuda.get_device_name(0)}思考中...")
    
    try:
        # Run the blocking AI function in a separate thread
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            executor, 
            ask, 
            "/nothink /Response as traditional chinese /Response as much as possible less word but not force to do| Here is the input chat: " + item["question"]
        )
        await interaction.edit_original_response(content=f"{response}")
    except Exception as e:
        await interaction.edit_original_response(content=f"❌ Error: {e}")
    finally:
        isqueue = False


@client.command()
async def isServerDown(ctx):
    #check net.kinglingmk1.com and pve.kinglingmk1.com status
    def check_server(host, port):
        try:
            with socket.create_connection((host, port), timeout=5):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False
    servers = {
        "net.kinglingmk1.com": 443,
        "pve.kinglingmk1.com": 8006
    }
    name = ["Headscale", "PVE"]
    status_messages = []
    i=0
    for server, port in servers.items():
        status = ":green_circle:  Online" if check_server(server, port) else ":red_circle: Offline"
        status_messages.append(f"{name[i]}: {status}")
        i += 1
    await ctx.send("\n".join(status_messages))
@client.command()
async def go(ctx):
    if ctx.author == client.user:
            return
    global isGo
    if isGo == False:
        isGo = True
        imgs = [
            "之前拋棄了我，現在還有臉回來-BKvy-NQ4.webp",
            "之前明明就不肯和我組樂團-CVo0-7ju.webp",
            "太棒了，爽世同學LOVE.jpg",
            "太好了-Bny2y6a-.webp",
            "太好了3.jpg",
            "叫我嗎-Crz6Q_da.webp",
            "我一直非常期待能和各位見面.jpg",
            "來了-hlcwWAQl.webp",
            "真讓人期待.jpg",
            "這種事早晚會發生的-DQBmYna4.webp",
            "這樣啊.jpg",
            "愛音泡澡.jpg",
            "愛音愛心.jpg",
            "讓我們一起迷失吧.jpg"
        ]
        img = random.choice(imgs)
        await ctx.send(file=discord.File(getIMGPath() + img))
        await ctx.send("還在Go")


@client.command()
async def stfu(ctx):
    #if is bot self message, ignore
    if ctx.author == client.user:
        return
    global isGo
    if isGo:
        isGo = False
        imgs = [
            "什麼意思.jpg",
            "什麼意思-D6R5zlNQ.webp",
            "今後不要再和我扯上關係了.jpg",
            "只要是我能做的，我什麼都願意做.jpg",
            "它沒有結束.jpg",
            "立希_蛤.jpg",
            "我早知道會這樣了.jpg",
            "我除了這世界已經一無所有了-CJ8djB3w.webp",
            "我會繼續做自己的夥伴.jpg",
            "求求妳.jpg",
            "那些我根本就不在乎-BhvdDSVI.webp",
            "那些全都是騙人的.jpg",
            "妳是抱著多大的覺悟說出這種話的.jpg",
            "妳們就請便吧.jpg",
            "妳真的要離開了嗎-BmZxGW1h.webp",
            "怎麼會...簡直不敢相信.jpg",
            "為什麼妳不肯站在我這邊-BNykkCh6.webp",
            "差勁.jpg",
            "差勁2.jpg",
            "真不敢相信.jpg",
            "真是會虛情假意呢.jpg",
            "真是讓人活得難受的世界啊.jpg",
            "做事笨拙總是徒勞.jpg",
            "動機太不單純了.jpg",
            "夠了夠了夠了-DDbwwW2e.webp",
            "從來不覺得玩樂團開心過.jpg",
            "掛斷了-LjNF4ksX.webp",
            "爽世驚訝.jpg",
            "這種事早晚會發生的-DQBmYna4.webp",
            "掰掰.jpg",
            "愛音_蛤.jpg",
            "愛音驚訝.jpg",
            "感謝您讓我佔用的寶貴時間.jpg",
            "態度好差喔.jpg",
            "還有這樣太不負責了吧.jpg"
        ]
        img = random.choice(imgs)
        await ctx.send(file=discord.File(getIMGPath() + img))
        await ctx.send("不再Go了")
    else:
        imgs = [
            "之前拋棄了我，現在還有臉回來-BKvy-NQ4.webp",
            "之前明明就不肯和我組樂團-CVo0-7ju.webp",
            "叫我嗎-Crz6Q_da.webp",
            "這種事早晚會發生的-DQBmYna4.webp",
            "這樣啊.jpg",
        ]
        img = random.choice(imgs)
        await ctx.send(file=discord.File(getIMGPath() + img))
        await ctx.send("還在Go")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    content = message.content
    # If message contains "一輩子" or "一世", send one of two images.
    if "一輩子" in content or "一世" in content:
        if isGo == False:
            return
        n = random.randint(0, 1)
        if n == 0:
            await message.channel.send(file=discord.File(getIMGPath() + "畢竟這是一輩子的事.jpg"))
        elif n == 1:
            await message.channel.send(file=discord.File(getIMGPath()+"是一輩子喔_一輩子.jpg"))
        return

    # If message contains any negative keywords:
    if any(word in content for word in ["不行", "不能", "不可以", "不要", "不想", "dame", "だめ"]) or content in ["No", "no", "NO", "Not", "not", "NOT"]:
        if isGo == False:
            return
        n = random.randint(0, 1)
        if n == 0:
            await message.channel.send(file=discord.File(getIMGPath()+"不行.jpg"))
        elif n == 1:
            await message.channel.send(file=discord.File(getIMGPath()+"不可以-BiaRmwz4.webp"))
        return

    # If message contains "春日影"
    if "春日影" in content:
        if isGo == False:
            return
        await message.channel.send(file=discord.File(getIMGPath()+"為什麼要演奏春日影.jpg"))
        # Here you might join a voice channel if desired.
        if message.content.startswith("!"):
            await client.process_commands(message)
            return
        return

    # If message contains "go" (any case variant)
    if content in ["go", "Go", "GO", "gO","去"]:
        if isGo == False:
            return
        await message.channel.send("還在Go 還在Go")
        await message.channel.send(file=discord.File(getIMGPath()+"我也一樣.jpg"))
        return

    # If message contains "Me too" variants
    if any(word in content for word in ["Me too", "me too", "我也是", "我也是啊", "我也一樣", "我也是呀","me2"]):
        if isGo == False:
            return
        await message.channel.send(file=discord.File(getIMGPath()+"我也一樣.jpg"))
        return

    # If message contains any variants of "Mujica"
    if any(word in content for word in ["Mujica", "mujica", "ムヒカ", "穆希卡", "ミュヒカ","母鷄卡"]):
        if isGo == False:
            return
        await message.channel.send(file=discord.File(getIMGPath()+"現在正是復權的時刻.jpg"))
        return
    if content in ["對健康不好", "不健康", "不健康的", "對健康不好啊", "對健康不好嗎", "不健康嗎", "不健康的嗎", "對健康不好喔", "對健康不好啊喔", "對健康不好啊喔嗎"]:
        if isGo == False:
            return
        imgs = [
            "對健康不好喔_2-Cmch--Fa.webp",
            "對健康不好喔_3-Cpm4dn3P.webp",
            "對健康不好喔-D9lhW0Ao.webp"
        ]
        img = random.choice(imgs)
        await message.channel.send(file=discord.File(getIMGPath() + img))
        return

    if content in ["豐川集團", "TGW", "Togawa Group", "TGWG", "Togawa", "豐川集團TGW", "豐川集團TGWG", "豐川集團Togawa Group"]:
        if isGo == False:
            return
        await message.channel.send(file=discord.File(getIMGPath()+"豐川集團.gif"))
        return

    if content == "!deepseek_mode":
        sent = await message.channel.send("思")
        await asyncio.sleep(0.02)
        sent = await sent.edit(content="思考")
        await asyncio.sleep(0.02)
        sent = await sent.edit(content="思考中")
        await asyncio.sleep(0.02)
        sent = await sent.edit(content="思考中.")
        await asyncio.sleep(0.02)
        sent = await sent.edit(content="思考中..")
        await asyncio.sleep(0.02)
        sent = await sent.edit(content="思考中...")
        await asyncio.sleep(5)
        await message.channel.send("服务器繁忙，请稍后再试")
        return

    # If the bot gets mentioned or one of its nicknames is found:
    if client.user in message.mentions or any(word in content for word in [
            "Soyo", "soyo", "そよ", "長崎そよ", "長崎爽世", "そよちゃん", "爽世", "素世", "長崎素世"]):
        await message.channel.send(file=discord.File(getIMGPath()+"幹嘛-CStDUUrz.webp"))
        return

    await client.process_commands(message)
client.run("TOKEN")