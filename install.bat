@echo off
echo Checking yt-dlp.exe exists...
set yt_dlp_url=https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe
if exist "./python_ver/yt-dlp.exe" (
    echo yt-dlp.exe already exists in python_ver directory.
) else (
    echo yt-dlp.exe does not exist, proceeding with download.
    echo Installing yt-dlp.exe
    curl -L -o "./python_ver/yt-dlp.exe" %yt_dlp_url%
    if %errorlevel% neq 0 (
        echo Failed to download yt-dlp.exe. Please check your internet connection or the URL.
        goto :cleanup
    )
)
echo Checking ffmpeg.exe exists...
if exist "./python_ver/ffmpeg.exe" (
    echo ffmpeg.exe already exists in python_ver directory.
    goto :completed
) else (
    echo ffmpeg.exe does not exist, proceeding with download.
)
echo Installing ffmpeg-master-latest-win64-lgpl
set ffmpeg_url=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-lgpl.zip
curl -L -o "./ffmpeg.zip" %ffmpeg_url%
if %errorlevel% neq 0 (
    echo Failed to download ffmpeg.exe. Please check your internet connection or the URL.
    goto :cleanup
)
echo Extracting ffmpeg.zip...
powershell -Command "Expand-Archive -Path './ffmpeg.zip' -DestinationPath './ffmpeg' -Force"
if %errorlevel% neq 0 (
    echo Failed to extract ffmpeg.zip. Please check the zip file.
)
echo Extracted ffmpeg.zip successfully
echo Moving ffmpeg.exe to directory
if exist ".\ffmpeg\ffmpeg-master-latest-win64-lgpl\bin\ffmpeg.exe" (
    move /Y ".\ffmpeg\ffmpeg-master-latest-win64-lgpl\bin\ffmpeg.exe" "./python_ver/ffmpeg.exe"
    if %errorlevel% neq 0 (
        echo Failed to move ffmpeg.exe. Please check the file paths.
    )
    echo Moved successfully to directory.
)
:cleanup
echo Cleaning up temporary files...
del /Q "./ffmpeg.zip"
if %errorlevel% neq 0 (
    echo Failed to delete ffmpeg.zip. Please check the file path.
)
rmdir /S /Q "./ffmpeg"
if %errorlevel% neq 0 (
    echo Failed to delete ffmpeg directory. Please check the file path.
)
:completed
echo Installing Python packages...
python -m pip install --upgrade pip
python -m pip install -r ./requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install Python packages. Please check the requirements.txt file.
)
echo Installation completed successfully.
pause