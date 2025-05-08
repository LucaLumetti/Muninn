#!/bin/bash

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================${NC}"
echo -e "${GREEN}Muninn Telegram Bot Installer${NC}"
echo -e "${BLUE}====================================${NC}"

# Get the current directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Get current user
CURRENT_USER=$(whoami)

# Find Python interpreter
if [ -d "${SCRIPT_DIR}/venv" ]; then
    PYTHON_PATH="${SCRIPT_DIR}/venv/bin/python"
    echo -e "${GREEN}✓${NC} Found virtual environment Python at: ${PYTHON_PATH}"
else
    PYTHON_PATH=$(which python3)
    if [ -z "$PYTHON_PATH" ]; then
        PYTHON_PATH=$(which python)
    fi
    
    if [ -z "$PYTHON_PATH" ]; then
        echo -e "${RED}✗ Error: Python interpreter not found${NC}"
        echo "Please install Python 3 and try again"
        exit 1
    fi
    
    echo -e "${YELLOW}!${NC} No virtual environment found. Using system Python: ${PYTHON_PATH}"
    echo -e "${YELLOW}!${NC} It's recommended to create a virtual environment:"
    echo "    python3 -m venv venv"
    echo "    source venv/bin/activate"
    echo "    pip install -r requirements.txt"
    echo ""
fi

# Check for .env file
if [ ! -f "${SCRIPT_DIR}/.env" ]; then
    echo -e "${YELLOW}!${NC} No .env file found"
    echo -e "Would you like to create a .env file now? [y/N] "
    read -r CREATE_ENV
    
    if [[ $CREATE_ENV =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}→${NC} Please enter your Telegram Bot Token: "
        read -r BOT_TOKEN
        
        echo -e "${BLUE}→${NC} Please enter authorized Telegram user IDs (comma-separated): "
        read -r USER_IDS
        
        echo "TELEGRAM_BOT_TOKEN=${BOT_TOKEN}" > "${SCRIPT_DIR}/.env"
        echo "AUTHORIZED_USERS=${USER_IDS}" >> "${SCRIPT_DIR}/.env"
        
        echo -e "${GREEN}✓${NC} Created .env file"
    else
        echo -e "${YELLOW}!${NC} Skipping .env creation"
        echo "Please create a .env file manually before running the bot"
    fi
fi

# Create the service file
echo -e "\n${BLUE}→${NC} Creating systemd service file..."

# Prepare the service file content
SERVICE_CONTENT="[Unit]
Description=Muninn Telegram Bot
After=network.target

[Service]
User=${CURRENT_USER}
WorkingDirectory=${SCRIPT_DIR}
ExecStart=${PYTHON_PATH} ${SCRIPT_DIR}/src/main.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target"

# Write to muninn.service file
echo "${SERVICE_CONTENT}" > "${SCRIPT_DIR}/muninn.service"
echo -e "${GREEN}✓${NC} Created muninn.service file with your configuration"

# Ask about installing as a system service
echo -e "\n${BLUE}→${NC} Would you like to install Muninn as a system service? [y/N] "
read -r INSTALL_SERVICE

if [[ $INSTALL_SERVICE =~ ^[Yy]$ ]]; then
    if [ "$EUID" -ne 0 ]; then
        echo -e "${YELLOW}!${NC} Root permissions required to install the service"
        echo -e "${BLUE}→${NC} Running with sudo..."
        
        # Copy the service file to systemd directory
        sudo cp "${SCRIPT_DIR}/muninn.service" /etc/systemd/system/
        
        # Reload systemd, enable and start the service
        echo -e "${BLUE}→${NC} Enabling and starting service..."
        sudo systemctl daemon-reload
        sudo systemctl enable muninn.service
        sudo systemctl start muninn.service
        
        echo -e "${GREEN}✓${NC} Muninn service installed and started"
        echo -e "${BLUE}→${NC} To check service status: sudo systemctl status muninn.service"
        echo -e "${BLUE}→${NC} To view logs: sudo journalctl -u muninn.service -f"
    else
        # Already running as root
        cp "${SCRIPT_DIR}/muninn.service" /etc/systemd/system/
        
        # Reload systemd, enable and start the service
        echo -e "${BLUE}→${NC} Enabling and starting service..."
        systemctl daemon-reload
        systemctl enable muninn.service
        systemctl start muninn.service
        
        echo -e "${GREEN}✓${NC} Muninn service installed and started"
        echo -e "${BLUE}→${NC} To check service status: systemctl status muninn.service"
        echo -e "${BLUE}→${NC} To view logs: journalctl -u muninn.service -f"
    fi
else
    echo -e "${YELLOW}!${NC} Skipping service installation"
    echo -e "${BLUE}→${NC} You can install it later with:"
    echo "    sudo cp ${SCRIPT_DIR}/muninn.service /etc/systemd/system/"
    echo "    sudo systemctl daemon-reload"
    echo "    sudo systemctl enable muninn.service"
    echo "    sudo systemctl start muninn.service"
fi

echo -e "\n${GREEN}Installation completed!${NC}"
echo -e "You can now run the bot manually with: ${PYTHON_PATH} ${SCRIPT_DIR}/src/main.py"
echo -e "Or use the systemd service if you installed it."
echo -e "${BLUE}====================================${NC}" 