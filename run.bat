@echo off
rem Set UTF-8 codepage
chcp 65001 > nul
setlocal enabledelayedexpansion

rem Enable ANSI color codes
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
  set "ESC=%%b"
)

rem Display colored logo
echo.
echo %ESC%[97m _  __   _   ____  _____ _____  _    %ESC%[0m
echo %ESC%[97m^| ^|/ /  / \  / ___^|^| ____^|_   _^|/ \   %ESC%[0m
echo %ESC%[97m^| ' /  / _ \ \___ \^|  _^|   ^| ^| / _ \  %ESC%[0m
echo %ESC%[97m^| . \ / ___ \ ___^) ^| ^|___  ^| ^|/ ___ \ %ESC%[0m
echo %ESC%[97m^|_^|\_/_/   \_\____/^|_____^| ^|_/_/   \_\%ESC%[0m
echo %ESC%[91m           Audio Processing Tools v1.0%ESC%[0m
echo %ESC%[97m==================================================%ESC%[0m
echo.

rem Check if settings.json exists and has language setting
set "KASETA_LANGUAGE="
set "SETTINGS_FILE=settings.json"

rem Try to extract language from settings file if it exists
if not exist "%SETTINGS_FILE%" goto language_selection

findstr /C:"language" "%SETTINGS_FILE%" > language_temp.txt
if %errorlevel% neq 0 goto language_selection

for /f "tokens=*" %%a in (language_temp.txt) do (
    for /f "tokens=2 delims=:, " %%b in ("%%a") do (
        set "lang_value=%%~b"
        set "lang_value=!lang_value:"=!"
    )
)
del language_temp.txt

if "!lang_value!"=="ru" set "KASETA_LANGUAGE=ru"
if "!lang_value!"=="en" set "KASETA_LANGUAGE=en"

if not defined KASETA_LANGUAGE goto language_selection

rem Language found in settings
if "%KASETA_LANGUAGE%"=="ru" (
    echo %ESC%[92mUsing saved language setting: Russian%ESC%[0m
) else (
    echo %ESC%[92mUsing saved language setting: English%ESC%[0m
)
goto language_done

:language_selection
rem Language not found in settings, prompt user
echo %ESC%[97mLanguage not found in settings. Please select:%ESC%[0m
echo %ESC%[97mChoose language / Vyberite yazyk:%ESC%[0m
echo %ESC%[97m1. Russian%ESC%[0m
echo %ESC%[97m2. English%ESC%[0m
choice /c 12 /n /m "%ESC%[97mSelect 1 or 2: %ESC%[0m"
set "lang_choice=%errorlevel%"

if %lang_choice%==1 (
    set "KASETA_LANGUAGE=ru"
    echo %ESC%[92mSelected: Russian%ESC%[0m
) else if %lang_choice%==2 (
    set "KASETA_LANGUAGE=en"
    echo %ESC%[92mSelected: English%ESC%[0m
) else (
    set "KASETA_LANGUAGE=ru"
    echo %ESC%[97mDefault: Russian%ESC%[0m
)

:language_done
echo.

rem Check if Python is installed
echo %ESC%[97mChecking Python...%ESC%[0m
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo %ESC%[91mPython not found! Please install Python 3.6 or newer.%ESC%[0m
    echo %ESC%[97mDownload: https://www.python.org/downloads/%ESC%[0m
    pause
    exit /b 1
)

rem Check Python version
echo %ESC%[97mChecking Python version...%ESC%[0m
python -c "import sys; sys.exit(0) if sys.version_info >= (3,6) else sys.exit(1)"
if %errorlevel% neq 0 (
    echo %ESC%[91mPython 3.6+ required!%ESC%[0m
    pause
    exit /b 1
)

rem Check if FFmpeg is installed
echo %ESC%[97mChecking FFmpeg...%ESC%[0m
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo %ESC%[91mFFmpeg not found! Please install FFmpeg.%ESC%[0m
    echo %ESC%[97mDownload: https://ffmpeg.org/download.html%ESC%[0m
    echo %ESC%[97mAdd FFmpeg to your PATH environment variable.%ESC%[0m
    pause
    exit /b 1
)

rem Check virtual environment
echo %ESC%[97mChecking virtual environment...%ESC%[0m
if not exist "venv" (
    echo %ESC%[97mCreating virtual environment...%ESC%[0m
    python -m venv venv
    if !errorlevel! neq 0 (
        echo %ESC%[91mError creating virtual environment!%ESC%[0m
        pause
        exit /b 1
    )
)

rem Activate virtual environment
echo %ESC%[97mActivating virtual environment...%ESC%[0m
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo %ESC%[91mError activating virtual environment!%ESC%[0m
    pause
    exit /b 1
)

rem Check dependencies
echo %ESC%[97mChecking dependencies...%ESC%[0m
pip freeze | findstr /i /c:"PyQt5" >nul
if %errorlevel% neq 0 (
    echo %ESC%[97mInstalling dependencies...%ESC%[0m
    pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo %ESC%[91mError installing dependencies!%ESC%[0m
        pause
        exit /b 1
    )
)

rem Launch application
echo %ESC%[92mAll checks passed! Starting application...%ESC%[0m
python scripts/run_gui.py --lang=%KASETA_LANGUAGE%
if %errorlevel% neq 0 (
    echo %ESC%[91mError launching application!%ESC%[0m
    pause
    exit /b 1
)

deactivate
exit /b 0 