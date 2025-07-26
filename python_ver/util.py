import os
from pathlib import Path
import re


def removefileName(input_path):
    """Remove file extension from the input path."""
    extensions = {".mp3": 4, ".flac": 5, ".m4a": 4}
    for ext, length in extensions.items():
        if input_path.endswith(ext):
            return input_path[:-length]
    return input_path


def mainPath():
    return os.path.dirname(os.path.realpath(__file__))


def getIMGPath():
    return os.path.join(mainPath(), "img")


def decode_subprocess_output(output_bytes):
    """嘗試使用不同編碼解碼subprocess輸出，優先處理日文編碼"""
    encodings = [
        "shift_jis",
        "cp932",
        "utf-8",
        "euc-jp",
        "iso-2022-jp",
        "cp1252",
        "cp437",
        "gbk",
        "big5",
    ]
    for enc in encodings:
        try:
            decoded = output_bytes.decode(enc).strip()
            if "\\u" in decoded:
                try:
                    decoded = decoded.encode().decode("unicode_escape")
                except Exception:
                    pass
            if (
                any(
                    "\u3040" <= c <= "\u309f"  # Hiragana
                    or "\u30a0" <= c <= "\u30ff"  # Katakana
                    or "\u4e00" <= c <= "\u9faf"  # Kanji
                    for c in decoded
                )
                or enc in encodings[:3]
            ):
                return decoded
        except UnicodeDecodeError:
            continue
    result = output_bytes.decode("shift_jis", errors="ignore").strip()
    return result.encode().decode("unicode_escape") if "\\u" in result else result


def intgrated(input_path):
    """Combine MP3 path with the cleaned audio path."""
    return os.path.join(getMP3Path(), removePath(getAudioPath(input_path)))


def clean_filename(filename):
    return re.sub(r'[<>:"/\\|?*【】「」／\\]', "", filename).replace("！", "!").strip()


def getFFMPEGPath():
    """Return the correct FFmpeg path based on the operating system."""
    return os.path.join(mainPath(), "ffmpeg.exe" if os.name == "nt" else "ffmpeg")


def getMP3Path():
    return os.path.join(mainPath(), "music")


def getAudioPath(input_name):
    music_dir = Path(getMP3Path())
    extensions = [".mp3", ".flac", ".m4a"]

    # Check exact matches first
    for ext in extensions:
        file = music_dir / (input_name + ext)
        if file.exists():
            return str(file)

    # Fallback to partial matching
    input_lower = input_name.lower()
    for ext in extensions:
        for file in music_dir.glob(f"*{ext}"):
            if input_lower in file.stem.lower():
                return str(file)

    return None


def removePath(input_path):
    mp3_path = getMP3Path() + os.sep
    return (
        input_path[len(mp3_path) :] if input_path.startswith(mp3_path) else input_path
    )
