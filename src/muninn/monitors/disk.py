"""
Disk usage monitoring
"""

import os
import logging
import psutil

logger = logging.getLogger(__name__)

def get_disk_info():
    """Get disk usage information."""
    try:
        partitions = psutil.disk_partitions(all=False)
        
        reply = "💾 *Disk Usage Information:*\n\n"
        
        for partition in partitions:
            if os.name == 'nt':
                if 'cdrom' in partition.opts or partition.fstype == '':
                    # Skip CD-ROM drives on Windows
                    continue
            
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                
                total_gb = usage.total / (1024 ** 3)
                used_gb = usage.used / (1024 ** 3)
                free_gb = usage.free / (1024 ** 3)
                
                reply += f"*Partition:* `{partition.mountpoint}`\n"
                reply += f"├─ Total: `{total_gb:.2f} GB`\n"
                reply += f"├─ Used: `{used_gb:.2f} GB` ({usage.percent}%)\n"
                reply += f"└─ Free: `{free_gb:.2f} GB`\n\n"
                
            except PermissionError:
                continue
        
        io_counters = psutil.disk_io_counters()
        if io_counters:
            read_mb = io_counters.read_bytes / (1024 ** 2)
            write_mb = io_counters.write_bytes / (1024 ** 2)
            
            reply += f"*Disk I/O (since boot):*\n"
            reply += f"├─ Read: `{read_mb:.2f} MB`\n"
            reply += f"└─ Written: `{write_mb:.2f} MB`\n"
        
        return reply
    
    except Exception as e:
        logger.error(f"Error in get_disk_info: {e}")
        return f"Error retrieving disk information: {e}" 