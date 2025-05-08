"""
Server load monitoring
"""

import logging
import psutil

logger = logging.getLogger(__name__)

def get_load_info():
    """Get server load information."""
    try:
        # Get load averages for the past 1, 5, and 15 minutes
        load1, load5, load15 = psutil.getloadavg()
        cpu_count = psutil.cpu_count()
        
        # Calculate percentage
        load1_percent = (load1 / cpu_count) * 100
        load5_percent = (load5 / cpu_count) * 100
        load15_percent = (load15 / cpu_count) * 100
        
        # Get CPU usage percentage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_used_gb = memory.used / (1024 ** 3)
        memory_total_gb = memory.total / (1024 ** 3)
        memory_percent = memory.percent
        
        # Format response
        reply = "⚡ *Server Load Information:*\n\n"
        reply += f"*CPU Load Averages:*\n"
        reply += f"├─ 1 min: `{load1:.2f}` ({load1_percent:.1f}%)\n"
        reply += f"├─ 5 min: `{load5:.2f}` ({load5_percent:.1f}%)\n"
        reply += f"└─ 15 min: `{load15:.2f}` ({load15_percent:.1f}%)\n\n"
        
        reply += f"*CPU Usage:* `{cpu_percent}%`\n\n"
        
        reply += f"*Memory Usage:*\n"
        reply += f"├─ Used: `{memory_used_gb:.2f} GB` of `{memory_total_gb:.2f} GB`\n"
        reply += f"└─ Percentage: `{memory_percent}%`\n"
        
        return reply
    
    except Exception as e:
        logger.error(f"Error in get_load_info: {e}")
        return f"Error retrieving load information: {e}" 