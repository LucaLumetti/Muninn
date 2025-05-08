"""
Command handlers for Telegram bot
"""

import logging
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from muninn.utils.auth import restricted
from muninn.utils.reporting import restart_report_thread, report_config, get_full_report

logger = logging.getLogger(__name__)

@restricted
def start(update: Update, context: CallbackContext, monitors) -> None:
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_text(
        f"Hello {user.first_name}! I'm Muninn, your server monitoring bot.\n\n"
        "Available commands:\n"
        "/status - Check if the server is online\n"
        "/docker - List running Docker containers\n"
        "/load - Show server load average\n"
        "/disk - Show disk usage\n"
        "/report - Generate a full server report\n"
        "/schedule - Configure automatic reports (hourly/daily)\n"
        "/help - Display this help message"
    )

@restricted
def status_command(update: Update, context: CallbackContext, monitors) -> None:
    """Check if the server is online."""
    update.message.reply_text(monitors.get_status_info())

@restricted
def docker_command(update: Update, context: CallbackContext, monitors) -> None:
    """List running Docker containers."""
    message = monitors.get_docker_info()
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

@restricted
def load_command(update: Update, context: CallbackContext, monitors) -> None:
    """Show server load average."""
    message = monitors.get_load_info()
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

@restricted
def disk_command(update: Update, context: CallbackContext, monitors) -> None:
    """Show disk usage."""
    message = monitors.get_disk_info()
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

@restricted
def report_command(update: Update, context: CallbackContext, monitors) -> None:
    """Generate and send a full report."""
    message = get_full_report(monitors)
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

@restricted
def schedule_command(update: Update, context: CallbackContext, monitors) -> None:
    """Configure automatic reporting schedule."""
    if not context.args or len(context.args) < 1:
        update.message.reply_text(
            "Please specify a schedule: '/schedule hourly' or '/schedule daily' or '/schedule disable'"
        )
        return
    
    schedule_type = context.args[0].lower()
    
    if schedule_type not in ["hourly", "daily", "disable"]:
        update.message.reply_text(
            "Invalid schedule type. Use '/schedule hourly' or '/schedule daily' or '/schedule disable'"
        )
        return
    
    chat_id = update.effective_chat.id
    
    if schedule_type == "disable":
        report_config["enabled"] = False
        update.message.reply_text("Automatic reports have been disabled.")
    else:
        report_config["enabled"] = True
        report_config["interval"] = schedule_type
        report_config["chat_id"] = chat_id
        
        update.message.reply_text(
            f"Automatic reports have been enabled with {schedule_type} schedule."
        )
    
    restart_report_thread(context.bot, monitors)

@restricted
def help_command(update: Update, context: CallbackContext, monitors) -> None:
    """Send a help message when the command /help is issued."""
    update.message.reply_text(
        "🔍 *Available Commands:*\n\n"
        "/status - Check if the server is online\n"
        "/docker - List running Docker containers\n"
        "/load - Show server load average\n"
        "/disk - Show disk usage\n"
        "/report - Generate a full server report\n"
        "/schedule hourly - Configure hourly automatic reports\n"
        "/schedule daily - Configure daily automatic reports\n"
        "/schedule disable - Disable automatic reports\n"
        "/help - Display this help message",
        parse_mode=ParseMode.MARKDOWN
    ) 