# Muninn - Server Monitoring Telegram Bot

<p align="center">
  <img src="assets/images/MuninnLogo.png" alt="Muninn Logo" width="300" height="300">
</p>

Muninn is a lightweight Telegram bot for monitoring Linux servers. It provides a convenient way to remotely check server status, system resources, network information, and Docker containers through simple commands.

Named after one of Odin's ravens in Norse mythology who brought information from around the world, Muninn keeps you informed about your server's health and status.

## Features

- 🔄 **Server Status**: Basic connectivity and uptime checks
- 🐳 **Docker Monitoring**: List running containers with status, image info, and port mappings
- ⚡ **System Load**: CPU usage, memory usage, and load averages with GPU support
- 💾 **Disk Usage**: Storage information with warning for high-usage partitions
- 🌐 **Network Monitoring**: Connection statistics, active connections, and open ports
- 📊 **Full Reports**: Generate comprehensive reports with all metrics
- ⏱️ **Scheduled Reports**: Configure automatic hourly/daily reports
- 🔒 **User Authorization**: Limit bot access to specific Telegram users

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/Muninn.git
   cd Muninn
   ```

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Telegram Bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   AUTHORIZED_USERS=comma_separated_list_of_telegram_user_ids
   ```

   To get a bot token, talk to [BotFather](https://t.me/BotFather) on Telegram.
   To find your Telegram user ID, talk to [userinfobot](https://t.me/userinfobot).

5. Run the bot:
   ```
   python src/main.py
   ```

## Usage

Send the following commands to the bot:

- `/start` - Welcome message and command list
- `/status` - Check if the server is online
- `/docker` - List running Docker containers
- `/load` - Show server load average and GPU information
- `/disk` - Show disk usage with warnings for high-usage partitions
- `/network` - Show network connections, interfaces and open ports
- `/report` - Generate a full server report with all metrics
- `/schedule hourly` - Enable hourly automatic reports
- `/schedule daily` - Enable daily automatic reports
- `/schedule disable` - Disable automatic reports
- `/help` - Display available commands

## Project Structure

```
Muninn/
├── assets/
│   └── images/            # Project images (including logo)
├── src/
│   ├── muninn/
│   │   ├── handlers/      # Telegram command handlers
│   │   ├── monitors/      # Server monitoring modules
│   │   ├── utils/         # Utility functions
│   │   └── bot.py         # Main bot implementation
│   └── main.py            # Entry point
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
└── README.md              # Documentation
```

## Adding New Monitoring Functions

The bot is designed to be modular and easily extended with new commands. To add a new monitoring function:

1. Create a new module in the `src/muninn/monitors/` directory
2. Add a getter function to the `Monitors` class in `src/muninn/monitors/all.py`
3. Create a command handler in `src/muninn/handlers/commands.py`
4. Register the command in the handlers dictionary in `src/muninn/bot.py`
5. Update the help text in `start()` and `help_command()` functions

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
   ExecStart=/usr/bin/python3 /path/to/Muninn/src/main.py
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

## Troubleshooting

### Markdown Parsing Issues
If you see "Can't parse entities" errors in your logs, it's likely due to Telegram's strict Markdown parsing. The bot now uses HTML formatting for complex outputs like network information to avoid these issues.

### Git Pre-Commit Hook Warning
If you're developing and see warnings about potential secrets in network.py, you can:
1. Add `# noqa` at the end of the line that's triggering the warning
2. Use `git commit --no-verify` to bypass the check
3. Modify the pre-commit hook to ignore code that handles network connections

## Dependencies

- `python-telegram-bot`: Telegram Bot API wrapper
- `psutil`: System monitoring utilities
- `python-dotenv`: Environment variable management
- `docker`: Docker API client

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
