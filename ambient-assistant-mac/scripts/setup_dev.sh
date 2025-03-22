#!/bin/bash
# Setup script for development environment

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up development environment for Ambient Assistant...${NC}"

# Check if Python 3.9+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}')
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 9 ]); then
    echo -e "${RED}Error: Python 3.9 or higher is required (found $python_version)${NC}"
    echo "Please install Python 3.9+ and try again."
    exit 1
fi

echo -e "${GREEN}✓ Python $python_version detected${NC}"

# Check if Tesseract is installed
if ! command -v tesseract &> /dev/null; then
    echo -e "${YELLOW}Warning: Tesseract OCR not found${NC}"
    echo "Would you like to install Tesseract OCR using Homebrew? (y/n)"
    read -r install_tesseract
    
    if [[ $install_tesseract =~ ^[Yy]$ ]]; then
        # Check if Homebrew is installed
        if ! command -v brew &> /dev/null; then
            echo -e "${YELLOW}Homebrew not found. Installing Homebrew...${NC}"
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        echo -e "${YELLOW}Installing Tesseract OCR...${NC}"
        brew install tesseract
    else
        echo -e "${YELLOW}Skipping Tesseract installation. Note that OCR functionality will not work.${NC}"
    fi
else
    echo -e "${GREEN}✓ Tesseract OCR detected${NC}"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cat > .env << EOF
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_ORG_ID=your_openai_org_id

# Anthropic API Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key

# DeepSeek API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key

# Default LLM Configuration
DEFAULT_LLM_PROVIDER=openai
DEFAULT_LLM_MODEL=gpt-4

# Application Settings
APP_DATA_DIR=~/Library/Application Support/AmbientAssistant
DEBUG=true
EOF
    echo -e "${YELLOW}Please edit the .env file to add your API keys${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p resources/icons

# Check if icons exist, if not create placeholder
if [ ! -f "resources/icons/app_icon.png" ]; then
    echo -e "${YELLOW}Creating placeholder app icon...${NC}"
    # Create a simple colored square as a placeholder
    python3 -c "
from PIL import Image, ImageDraw
img = Image.new('RGBA', (1024, 1024), color=(0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.rectangle([(0, 0), (1024, 1024)], fill=(58, 123, 213))
img.save('resources/icons/app_icon.png')
"
fi

if [ ! -f "resources/icons/tray_icon.png" ]; then
    echo -e "${YELLOW}Creating placeholder tray icon...${NC}"
    # Create a simple colored circle as a placeholder
    python3 -c "
from PIL import Image, ImageDraw
img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.ellipse([(4, 4), (60, 60)], fill=(58, 123, 213))
img.save('resources/icons/tray_icon.png')
"
fi

if [ ! -f "resources/icons/tray_icon_inactive.png" ]; then
    echo -e "${YELLOW}Creating placeholder inactive tray icon...${NC}"
    # Create a simple gray circle as a placeholder
    python3 -c "
from PIL import Image, ImageDraw
img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.ellipse([(4, 4), (60, 60)], fill=(150, 150, 150))
img.save('resources/icons/tray_icon_inactive.png')
"
fi

echo -e "${GREEN}Development environment setup complete!${NC}"
echo -e "To start the application, run: ${YELLOW}python -m ambient.main${NC}"
echo -e "To deactivate the virtual environment when done, run: ${YELLOW}deactivate${NC}"
