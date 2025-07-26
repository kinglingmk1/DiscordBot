#!/bin/bash

# --- ffmpeg install function ---
install_ffmpeg_static() {
    echo "Downloading static ffmpeg build (LGPL)..."
    ffmpeg_url="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
    mkdir -p ./temp_ffmpeg
    cd ./temp_ffmpeg
    curl -L -o "ffmpeg-static.tar.xz" "$ffmpeg_url"
    if [ $? -ne 0 ]; then
        echo "Failed to download ffmpeg static build."
        cd ..
        rm -rf ./temp_ffmpeg
        exit 1
    fi
    tar -xf "ffmpeg-static.tar.xz"
    if [ $? -ne 0 ]; then
        echo "Failed to extract ffmpeg."
        cd ..
        rm -rf ./temp_ffmpeg
        exit 1
    fi
    ffmpeg_dir=$(find . -name "ffmpeg-*-amd64-static" -type d | head -n 1)
    if [ -n "$ffmpeg_dir" ] && [ -f "$ffmpeg_dir/ffmpeg" ]; then
        cp "$ffmpeg_dir/ffmpeg" "../python_ver/ffmpeg"
        chmod +x "../python_ver/ffmpeg"
        echo "ffmpeg static build installed successfully to python_ver directory."
    else
        echo "Failed to find ffmpeg binary in extracted files."
        cd ..
        rm -rf ./temp_ffmpeg
        exit 1
    fi
    cd ..
    rm -rf ./temp_ffmpeg
}

echo "Checking yt-dlp exists..."
yt_dlp_url="https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"

if [ -f "./python_ver/yt-dlp" ]; then
    echo "yt-dlp already exists in python_ver directory."
else
    echo "yt-dlp does not exist, proceeding with download."
    echo "Installing yt-dlp"
    curl -L -o "./python_ver/yt-dlp" "$yt_dlp_url"
    if [ $? -ne 0 ]; then
        echo "Failed to download yt-dlp. Please check your internet connection or the URL."
        exit 1
    fi
    chmod +x "./python_ver/yt-dlp"
    mv "./python_ver/yt-dlp" "./python_ver/yt-dlp_linux"
    echo "Downloaded and made yt-dlp executable."
fi

echo "Checking ffmpeg exists..."
if [ -f "./python_ver/ffmpeg" ]; then
    echo "ffmpeg already exists in python_ver directory."
else
    echo "ffmpeg does not exist, proceeding with download."
    echo "Installing ffmpeg static build..."
    install_ffmpeg_static
fi

echo "Installing Python packages..."

# Python venv setup
VENV_DIR="./python_ver/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment in $VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Please check your Python installation."
        exit 1
    fi
else
    echo "Virtual environment already exists."
fi

# Activate venv and install requirements
source "$VENV_DIR/bin/activate"
echo "Upgrading pip in venv..."
pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "Failed to upgrade pip in venv. Continuing anyway..."
fi

echo "Installing requirements in venv..."
pip install -r ./requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install Python packages in venv. Please check requirements.txt."
    deactivate
    exit 1
fi

deactivate

echo "Making sure python_ver directory has correct permissions..."
chmod +x "./python_ver/yt-dlp" 2>/dev/null
chmod +x "./python_ver/ffmpeg" 2>/dev/null

echo "Installation completed successfully!"
echo ""
echo "To run the bot:"
echo "cd python_ver"
echo "source venv/bin/activate"
echo "python main.py"
echo ""
echo "Note: Make sure to update the Discord bot token in main.py before running."
