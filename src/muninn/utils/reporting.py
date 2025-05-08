"""
Reporting utilities for scheduled reports
"""

import time
import logging
import threading
from datetime import datetime
from telegram import ParseMode

logger = logging.getLogger(__name__)

# Global variable to store report schedule configuration
report_config = {
    "enabled": False,
    "interval": "daily",  # "hourly" or "daily"
    "chat_id": None,
    "last_report_time": 0,
    "report_thread": None,
}

def get_full_report(monitors):
    """Generate a complete server report with all metrics."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"📊 *SERVER MONITORING REPORT*\n"
    report += f"*Time:* `{timestamp}`\n\n"
    
    # Add all monitoring information
    report += monitors.get_status_info() + "\n\n"
    report += monitors.get_load_info() + "\n\n"
    report += monitors.get_disk_info() + "\n\n"
    report += monitors.get_docker_info()
    
    return report

def report_thread_function(bot, monitors):
    """Background thread function that sends periodic reports."""
    while report_config["enabled"]:
        current_time = time.time()
        
        interval = 3600 if report_config["interval"] == "hourly" else 86400  # 1 hour or 24 hours
        
        if current_time - report_config["last_report_time"] >= interval:
            try:
                if report_config["chat_id"]:
                    report = get_full_report(monitors)
                    bot.send_message(
                        chat_id=report_config["chat_id"],
                        text=report,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    report_config["last_report_time"] = current_time
                    logger.info(f"Sent scheduled {report_config['interval']} report")
            except Exception as e:
                logger.error(f"Error sending scheduled report: {e}")
        
        time.sleep(60)  # Check every minute

def restart_report_thread(bot, monitors):
    """Stop existing reporting thread and start a new one if enabled."""
    # Stop existing thread if running
    if report_config["report_thread"] and report_config["report_thread"].is_alive():
        report_config["enabled"] = False
        report_config["report_thread"].join(timeout=2.0)
    
    # Start new thread if reports are enabled
    if report_config["enabled"]:
        report_config["last_report_time"] = time.time()
        report_config["report_thread"] = threading.Thread(
            target=report_thread_function,
            args=(bot, monitors),
            daemon=True
        )
        report_config["report_thread"].start()
        logger.info(f"Started automatic {report_config['interval']} reporting") 