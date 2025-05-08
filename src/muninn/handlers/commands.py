"""
Command handlers for Telegram bot
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from muninn.utils.auth import restricted
from muninn.utils.reporting import restart_report_thread, report_config, get_full_report

logger = logging.getLogger(__name__)

@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, monitors) -> None:
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {user.first_name}! I'm Muninn, your server monitoring bot.\n\n"
        "Available commands:\n"
        "/status - Check if the server is online\n"
        "/docker - List running Docker containers\n"
        "/load - Show server load average\n"
        "/disk - Show disk usage\n"
        "/network - Show network connections and open ports\n"
        "/report - Generate a full server report\n"
        "/schedule - Configure automatic reports (hourly/daily)\n"
        "/help - Display this help message"
    )

@restricted
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE, monitors) -> None:
    """Show server status."""
    message = monitors.get_status_info()
    await update.message.reply_text(message, parse_mode="Markdown")

@restricted
async def docker_command(update: Update, context: ContextTypes.DEFAULT_TYPE, monitors) -> None:
    """Show Docker containers status."""
    message = monitors.get_docker_info()
    await update.message.reply_text(message, parse_mode="Markdown")

@restricted
async def load_command(update: Update, context: ContextTypes.DEFAULT_TYPE, monitors) -> None:
    """Show server load average."""
    message = monitors.get_load_info()
    await update.message.reply_text(message, parse_mode="Markdown")

@restricted
async def disk_command(update: Update, context: ContextTypes.DEFAULT_TYPE, monitors) -> None:
    """Show disk usage."""
    message = monitors.get_disk_info()
    await update.message.reply_text(message, parse_mode="Markdown")

@restricted
async def network_command(update: Update, context: ContextTypes.DEFAULT_TYPE, monitors) -> None:
    """Show network connections and open ports."""
    message = monitors.get_network_info()
    await update.message.reply_text(message, parse_mode="HTML")

@restricted
async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE, monitors) -> None:
    """Generate full server report."""
    # Send main report with Markdown
    message = get_full_report(monitors)
    await update.message.reply_text(message, parse_mode="Markdown")
    
    # Send network info separately with HTML
    network_info = monitors.get_network_info()
    if "Error" not in network_info:
        await update.message.reply_text(network_info, parse_mode="HTML")

@restricted
async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE, monitors) -> None:
    """Configure automatic reporting schedule."""
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "Please specify a schedule: '/schedule hourly' or '/schedule daily' or '/schedule disable'"
        )
        return
    
    schedule_type = context.args[0].lower()
    
    if schedule_type not in ["hourly", "daily", "disable"]:
        await update.message.reply_text(
            "Invalid schedule type. Use '/schedule hourly' or '/schedule daily' or '/schedule disable'"
        )
        return
    
    chat_id = update.effective_chat.id
    
    if schedule_type == "disable":
        report_config["enabled"] = False
        await update.message.reply_text("Automatic reports have been disabled.")
    else:
        report_config["enabled"] = True
        report_config["interval"] = schedule_type
        report_config["chat_id"] = chat_id
        
        await update.message.reply_text(
            f"Automatic reports have been enabled with {schedule_type} schedule."
        )
    
    restart_report_thread(context.bot, monitors)

@restricted
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE, monitors) -> None:
    """Send a help message when the command /help is issued."""
    await update.message.reply_text(
        "🔍 *Available Commands:*\n\n"
        "/status - Check if the server is online\n"
        "/docker - List running Docker containers\n"
        "/load - Show server load average\n"
        "/disk - Show disk usage\n"
        "/network - Show network connections and open ports\n"
        "/report - Generate a full server report\n"
        "/schedule hourly - Configure hourly automatic reports\n"
        "/schedule daily - Configure daily automatic reports\n"
        "/schedule disable - Disable automatic reports\n"
        "/help - Display this help message",
        parse_mode="Markdown"
    ) 