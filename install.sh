#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[+] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Check if script is run as root
if [[ $EUID -eq 0 ]]; then
    print_error "This script should not be run as root."
    print_warning "Please run as a regular user. The script will use sudo when needed."
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

print_status "Starting Muninn installation at $(date)"

# Check for required tools
print_status "Checking for required tools..."
for cmd in python3 pip3 systemctl; do
    if ! command -v $cmd &> /dev/null; then
        print_error "$cmd is required but not installed. Please install it and try again."
        exit 1
    fi
done

# Create virtual environment
print_status "Creating Python virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Using existing environment."
else
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install required packages
print_status "Installing required packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating skeleton .env file..."
    cat > .env << EOL
# Telegram Bot Token (get from BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Comma-separated list of authorized Telegram user IDs
AUTHORIZED_USERS=123456789,987654321
EOL
    print_warning "Please edit the .env file with your Telegram Bot token and authorized user IDs."
else
    print_warning ".env file already exists. Not overwriting."
fi

# Create systemd service file
print_status "Creating systemd service file..."

# Get absolute paths for service file
ABSOLUTE_PATH="$SCRIPT_DIR"
PYTHON_PATH="$ABSOLUTE_PATH/venv/bin/python3"
BOT_PATH="$ABSOLUTE_PATH/src/main.py"
USERNAME="$(whoami)"

# Create temporary service file
cat > /tmp/muninn.service << EOL
[Unit]
Description=Muninn Telegram Bot
After=network.target

[Service]
User=$USERNAME
WorkingDirectory=$ABSOLUTE_PATH
ExecStart=$PYTHON_PATH $BOT_PATH
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment=PATH=$ABSOLUTE_PATH/venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=$ABSOLUTE_PATH

[Install]
WantedBy=multi-user.target
EOL

# Install service file
print_status "Installing systemd service (requires sudo)..."
sudo mv /tmp/muninn.service /etc/systemd/system/muninn.service
sudo systemctl daemon-reload

print_status "Installation completed successfully!"
print_status "You can now:"
print_status "1. Edit the .env file with your Telegram Bot token:"
echo "   nano $ABSOLUTE_PATH/.env"
print_status "2. Enable and start the Muninn service:"
echo "   sudo systemctl enable muninn.service"
echo "   sudo systemctl start muninn.service"
print_status "3. Check the status of the service:"
echo "   sudo systemctl status muninn.service"

# Make the main script executable
chmod +x src/main.py

print_status "Muninn installation completed at $(date)"
print_warning "Remember to edit your .env file before starting the service!" 