#!/usr/bin/env python3
"""
Muninn - A lightweight Telegram bot for server monitoring
"""

import os
import logging
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler

from muninn.monitors.all import Monitors
from muninn.handlers.commands import (
    start, status_command, docker_command, load_command,
    disk_command, network_command, report_command, schedule_command, help_command
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get token from environment variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("No token provided. Set the TELEGRAM_BOT_TOKEN environment variable.")

def create_handler_with_monitors(handler_func):
    """Create a handler function that includes the monitors instance."""
    monitors = Monitors()
    
    async def wrapper(update, context):
        return await handler_func(update, context, monitors)
    
    return wrapper

def main():
    """Start the bot."""
    # Create the application and pass it your bot's token
    application = ApplicationBuilder().token(TOKEN).build()

    # Create handler functions with monitors included
    handlers = {
        "start": create_handler_with_monitors(start),
        "status": create_handler_with_monitors(status_command),
        "docker": create_handler_with_monitors(docker_command),
        "load": create_handler_with_monitors(load_command),
        "disk": create_handler_with_monitors(disk_command),
        "network": create_handler_with_monitors(network_command),
        "report": create_handler_with_monitors(report_command),
        "schedule": create_handler_with_monitors(schedule_command),
        "help": create_handler_with_monitors(help_command),
    }

    # Register command handlers
    for command, handler in handlers.items():
        application.add_handler(CommandHandler(command, handler))

    # Start the Bot
    logger.info("Bot starting. Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == "__main__":
    main() 