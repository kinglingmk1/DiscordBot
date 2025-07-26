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
echo "Install this script means you agree to all of the license terms of the software it installs."
echo "Do you agree to install the software? (y/n)"
read -r install_choice
if [[ "$install_choice" != "y" && "$install_choice" != "Y" ]]; then
    echo "Installation aborted."
    exit 0
fi

echo "Checking ffmpeg exists..."
if [ -f "./python_ver/ffmpeg" ]; then
    echo "ffmpeg already exists in python_ver directory."
else
    echo "ffmpeg does not exist, proceeding with download."
    echo "Do you agree to install ffmpeg static build? (y/n)"
    read -r install_ffmpeg_choice
    if [[ "$install_ffmpeg_choice" != "y" && "$install_ffmpeg_choice" != "Y" ]]; then
        echo "Skipping ffmpeg installation. You may need to install it manually."
        echo "Cleaning up..."
        rm -f "./python_ver/yt-dlp"
        echo "Installation aborted."
        exit 0
    fi
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
echo "Do you want to check and upgrade pip in the virtual environment? (y/n)"
read -r upgrade_pip_choice
if [[ "$upgrade_pip_choice" == "y" || "$upgrade_pip_choice" == "Y" ]]; then
    echo "Upgrading pip in venv..."
    pip install --upgrade pip
    if [ $? -ne 0 ]; then
        echo "Failed to upgrade pip in venv. Continuing anyway..."
    fi
fi

echo "Do you want to install requirements from requirements.txt? (y/n)"
read -r install_requirements_choice
if [[ "$install_requirements_choice" == "y" || "$install_requirements_choice" == "Y" ]]; then
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
