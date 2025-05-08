# Muninn - Server Monitoring Telegram Bot

Muninn is a Telegram bot for monitoring my Linux servers. A custom-built solution for remotely checking server status such as Docker containers, and system resources through simple commands.

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/Muninn.git
   cd Muninn
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Telegram Bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   AUTHORIZED_USERS=comma_separated_list_of_telegram_user_ids
   ```

   To get a bot token, talk to [BotFather](https://t.me/BotFather) on Telegram.
   To find your Telegram user ID, talk to [userinfobot](https://t.me/userinfobot).

4. Run the bot:
   ```
   python muninn_bot.py
   ```

## Usage

Send the following commands to the bot:

- `/start` - Welcome message and command list
- `/status` - Check if the server is online
- `/docker` - List running Docker containers
- `/load` - Show server load average
- `/disk` - Show disk usage
- `/report` - Generate a full server report with all metrics
- `/schedule hourly` - Enable hourly automatic reports
- `/schedule daily` - Enable daily automatic reports
- `/schedule disable` - Disable automatic reports
- `/help` - Display available commands

## Extending the Bot

The bot is designed to be easily extended with new commands. To add a new monitoring function:

1. Add a new data collection function in the "MONITORING FUNCTIONS" section
2. Add a new command handler in the "COMMAND HANDLERS" section
3. Register the new command in the main() function
4. Update the help_command() and start() functions to include your new command

Example for adding a new "network" command:

```python
# In the MONITORING FUNCTIONS section
def get_network_info():
    """Get network usage information."""
    # Your code to collect network data
    return formatted_message

# In the COMMAND HANDLERS section
@restricted
def network_command(update: Update, context: CallbackContext) -> None:
    """Show network usage."""
    message = get_network_info()
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

# In the main() function, add:
dispatcher.add_handler(CommandHandler("network", network_command))
```

Don't forget to update the full report function to include your new metrics:

```python
def get_full_report():
    # ...existing code...
    report += get_network_info() + "\n\n"
    # ...existing code...
```

## Run as a Service

To run the bot as a systemd service:

1. Create a service file:
   ```
   sudo nano /etc/systemd/system/muninn.service
   ```

2. Add the following content:
   ```
   [Unit]
   Description=Muninn Telegram Bot
   After=network.target

   [Service]
   User=your_username
   WorkingDirectory=/path/to/Muninn
   ExecStart=/usr/bin/python3 /path/to/Muninn/muninn_bot.py
   Restart=on-failure
   RestartSec=10
   StandardOutput=journal
   StandardError=journal

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```
   sudo systemctl enable muninn.service
   sudo systemctl start muninn.service
   ```

4. Check the status:
   ```
   sudo systemctl status muninn.service
   ``` 