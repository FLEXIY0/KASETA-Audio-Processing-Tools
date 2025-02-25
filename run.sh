#!/bin/bash

# Set UTF-8 encoding
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

# Terminal colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Display KASETA logo
echo -e "${CYAN}"
echo " _  __   _   ____  _____ _____  _    "
echo "| |/ /  / \  / ___|| ____|_   _|/ \   "
echo "| ' /  / _ \ \___ \|  _|   | | / _ \  "
echo "| . \ / ___ \ ___) | |___  | |/ ___ \ "
echo "|_|\_/_/   \_\____/|_____| |_/_/   \_\\"
echo -e "${YELLOW}     Audio Processing Tools v1.0${NC}"
echo "=================================================="

# Check if settings.json exists and has language setting
SETTINGS_FILE="settings.json"
KASETA_LANGUAGE=""

if [ -f "$SETTINGS_FILE" ]; then
    # Try to extract language from settings file if jq is available
    if command -v grep &> /dev/null; then
        LANG_VALUE=$(grep -o '"language"[[:space:]]*:[[:space:]]*"[^"]*"' "$SETTINGS_FILE" | grep -o '"[^"]*"$' | tr -d '"')
        if [ "$LANG_VALUE" = "ru" ] || [ "$LANG_VALUE" = "en" ]; then
            KASETA_LANGUAGE="$LANG_VALUE"
        fi
    fi
fi

# Language selection function
select_language() {
    echo -e "${CYAN}Choose language / Vyberite yazyk:${NC}"
    echo "1. Russian"
    echo "2. English"
    read -p "Select (1/2): " choice
    case "$choice" in
        1) echo "ru" ;;
        2) echo "en" ;;
        *) echo "default" ;;
    esac
}

# If language not found in settings, prompt user
if [ -z "$KASETA_LANGUAGE" ]; then
    echo -e "${YELLOW}Language not found in settings. Please select:${NC}"
    LANG_CHOICE=$(select_language)
    
    # Set environment variable for language
    if [ "$LANG_CHOICE" = "ru" ]; then
        export KASETA_LANGUAGE="ru"
        echo -e "${GREEN}Selected: Russian${NC}"
    elif [ "$LANG_CHOICE" = "en" ]; then
        export KASETA_LANGUAGE="en"
        echo -e "${GREEN}Selected: English${NC}"
    else
        export KASETA_LANGUAGE="ru"
        echo -e "${YELLOW}Default: Russian${NC}"
    fi
else
    export KASETA_LANGUAGE="$KASETA_LANGUAGE"
    if [ "$KASETA_LANGUAGE" = "ru" ]; then
        echo -e "${GREEN}Using saved language setting: Russian${NC}"
    else
        echo -e "${GREEN}Using saved language setting: English${NC}"
    fi
fi

echo ""

# Check if Python is installed
echo -e "${CYAN}Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 not found! Please install Python 3.6 or newer.${NC}"
    echo "For Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "For Fedora: sudo dnf install python3 python3-pip"
    exit 1
fi

# Check Python version
echo -e "${CYAN}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_VERSION_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_VERSION_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_VERSION_MAJOR" -lt 3 ] || ([ "$PYTHON_VERSION_MAJOR" -eq 3 ] && [ "$PYTHON_VERSION_MINOR" -lt 6 ]); then
    echo -e "${RED}Python 3.6 or newer required! You have Python $PYTHON_VERSION${NC}"
    exit 1
fi

# Check if FFmpeg is installed
echo -e "${CYAN}Checking FFmpeg...${NC}"
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}FFmpeg not found! Please install FFmpeg.${NC}"
    echo "For Ubuntu/Debian: sudo apt install ffmpeg"
    echo "For Fedora: sudo dnf install ffmpeg"
    exit 1
fi

# Check/create virtual environment
echo -e "${CYAN}Checking virtual environment...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error creating virtual environment!${NC}"
        echo "Try installing python3-venv package: sudo apt install python3-venv"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${CYAN}Activating virtual environment...${NC}"
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}Error activating virtual environment!${NC}"
    exit 1
fi

# Check and install dependencies
echo -e "${CYAN}Checking dependencies...${NC}"
if ! pip list | grep -q "PyQt5"; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error installing dependencies!${NC}"
        echo "Try running: sudo apt install python3-pip python3-pyqt5"
        exit 1
    fi
fi

# Launch application
echo -e "${GREEN}All checks passed! Starting application...${NC}"
python3 scripts/run_gui.py --lang=$KASETA_LANGUAGE
if [ $? -ne 0 ]; then
    echo -e "${RED}Error launching application!${NC}"
    exit 1
fi

deactivate
exit 0 