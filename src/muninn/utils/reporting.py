"""
Reporting utilities for scheduled reports
"""

import time
import logging
import threading
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

# Global variable to store report schedule configuration
report_config = {
    "enabled": False,
    "interval": "hourly",  # "hourly" or "daily"
    "chat_id": None,
    "last_report_time": 0,
    "report_thread": None,
}

report_thread = None
thread_stop_event = threading.Event()

def get_full_report(monitors):
    """Get a comprehensive server report."""
    report = "📊 *FULL SERVER REPORT*\n\n"
    
    # Basic server status
    report += monitors.get_status_info() + "\n\n"
    
    # Load information
    report += monitors.get_load_info() + "\n\n"
    
    # Disk usage
    report += monitors.get_disk_info() + "\n\n"
    
    # Docker containers
    docker_info = monitors.get_docker_info()
    if "Error" not in docker_info and "No Docker" not in docker_info:
        report += docker_info + "\n\n"
    
    report += "\n\n⏰ Report generated at: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return report

async def send_report(bot, chat_id, monitors):
    """Send a report asynchronously to the specified chat."""
    try:
        # Send main report with Markdown
        report = get_full_report(monitors)
        await bot.send_message(chat_id=chat_id, text=report, parse_mode="Markdown")
        
        # Send network info separately with HTML
        network_info = monitors.get_network_info()
        if "Error" not in network_info:
            await bot.send_message(chat_id=chat_id, text=network_info, parse_mode="HTML")
        
        logger.info(f"Report sent to chat {chat_id}")
        
        # Update last report time
        report_config["last_report_time"] = time.time()
    except Exception as e:
        logger.error(f"Error sending report: {e}")

def report_thread_function(bot, monitors):
    """Background thread for periodic reporting."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    while not thread_stop_event.is_set():
        try:
            # Check if reporting is enabled
            if not report_config["enabled"] or not report_config["chat_id"]:
                time.sleep(60)
                continue
            
            current_time = time.time()
            last_report_time = report_config["last_report_time"]
            interval = report_config["interval"]
            
            # Determine the reporting interval in seconds
            interval_seconds = 3600  # Default: hourly
            if interval == "daily":
                interval_seconds = 86400
            
            # Check if it's time to send a report
            if current_time - last_report_time >= interval_seconds:
                loop.run_until_complete(
                    send_report(bot, report_config["chat_id"], monitors)
                )
            
            # Sleep for 60 seconds before checking again
            time.sleep(60)
            
        except Exception as e:
            logger.error(f"Error in report thread: {e}")
            time.sleep(60)
    
    logger.info("Report thread stopped")

def restart_report_thread(bot, monitors):
    """Start or restart the reporting thread."""
    global report_thread, thread_stop_event
    
    # Stop existing thread if running
    if report_thread and report_thread.is_alive():
        thread_stop_event.set()
        report_thread.join(timeout=5)
        thread_stop_event.clear()
    
    # Start new thread
    report_thread = threading.Thread(
        target=report_thread_function,
        args=(bot, monitors),
        daemon=True
    )
    report_thread.start()
    logger.info("Report thread started/restarted") 