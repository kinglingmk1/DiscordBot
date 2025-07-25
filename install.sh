#!/bin/bash

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

install_ffmpeg_static() {
    echo "Downloading static ffmpeg build (LGPL)..."
    ffmpeg_url="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
    
    # Create temp directory
    mkdir -p ./temp_ffmpeg
    cd ./temp_ffmpeg
    
    # Download ffmpeg
    curl -L -o "ffmpeg-static.tar.xz" "$ffmpeg_url"
    if [ $? -ne 0 ]; then
        echo "Failed to download ffmpeg static build."
        cd ..
        rm -rf ./temp_ffmpeg
        exit 1
    fi
    
    # Extract ffmpeg
    tar -xf "ffmpeg-static.tar.xz"
    if [ $? -ne 0 ]; then
        echo "Failed to extract ffmpeg."
        cd ..
        rm -rf ./temp_ffmpeg
        exit 1
    fi
    
    # Find and move ffmpeg binary
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
    
    # Cleanup
    cd ..
    rm -rf ./temp_ffmpeg
}

echo "Installing Python packages..."

# Check if pip3 is available, otherwise use pip
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "pip is not installed. Please install pip first."
    echo "On Debian/Ubuntu: sudo apt-get install python3-pip"
    exit 1
fi

# Check if python3 is available, otherwise use python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Python is not installed. Please install Python first."
    echo "On Debian/Ubuntu: sudo apt-get install python3"
    exit 1
fi

echo "Using $PYTHON_CMD and $PIP_CMD"

# Upgrade pip
$PYTHON_CMD -m pip install --upgrade pip --user
if [ $? -ne 0 ]; then
    echo "Failed to upgrade pip. Continuing anyway..."
fi

# Install requirements
$PYTHON_CMD -m pip install -r ./requirements.txt --user
if [ $? -ne 0 ]; then
    echo "Failed to install Python packages. Please check the requirements.txt file."
    echo "You may need to install additional system packages:"
    echo "sudo apt-get install python3-dev libffi-dev libsodium-dev"
    exit 1
fi

echo "Making sure python_ver directory has correct permissions..."
chmod +x "./python_ver/yt-dlp" 2>/dev/null
chmod +x "./python_ver/ffmpeg" 2>/dev/null

echo "Installation completed successfully!"
echo ""
echo "To run the bot:"
echo "cd python_ver"
echo "$PYTHON_CMD main.py"
echo ""
echo "Note: Make sure to update the Discord bot token in main.py before running."
