"""
Disk usage monitoring
"""

import os
import logging
import psutil
import subprocess

logger = logging.getLogger(__name__)

def should_skip_partition(mountpoint, fstype):
    """Determine if a partition should be skipped."""
    # Skip snap-related partitions
    if 'snap' in mountpoint:
        return True
    
    # Skip certain filesystem types
    skip_fs_types = ['tmpfs', 'devtmpfs', 'devfs', 'overlay', 'aufs', 'squashfs']
    if fstype in skip_fs_types:
        return True
    
    # Skip virtual or special filesystems
    if mountpoint.startswith(('/sys', '/proc', '/run', '/dev')):
        return True
    
    return False

def get_additional_partitions():
    """Get partitions that might be missed by psutil."""
    try:
        # Run df command to get all mounted filesystems
        result = subprocess.run(['df', '-h'], capture_output=True, text=True, check=True)
        
        # Parse the output to find important partitions
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        
        additional_partitions = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 6:
                device = parts[0]
                mountpoint = parts[5]
                
                # Skip if it's likely a special filesystem
                if should_skip_partition(mountpoint, ""):
                    continue
                
                # Add to list if it's a real disk partition
                if device.startswith('/dev/'):
                    additional_partitions.append(mountpoint)
        
        return additional_partitions
    
    except Exception as e:
        logger.error(f"Error getting additional partitions: {e}")
        return []

def format_partition_info(mountpoint, total_gb, used_gb, free_gb, percent):
    """Format the partition information string, highlighting high usage."""
    # Highlight partitions with high usage
    is_critical = percent >= 90
    highlight = "*" if is_critical else ""
    
    # Format the partition info
    info = f"{highlight}*Partition:* `{mountpoint}`{highlight}\n"
    
    if is_critical:
        info += f"├─ Total: `{total_gb:.2f} GB`\n"
        info += f"├─ Used: `{used_gb:.2f} GB` (*{percent}%* ⚠️)\n"
        info += f"└─ Free: `{free_gb:.2f} GB`\n\n"
    else:
        info += f"├─ Total: `{total_gb:.2f} GB`\n"
        info += f"├─ Used: `{used_gb:.2f} GB` ({percent}%)\n"
        info += f"└─ Free: `{free_gb:.2f} GB`\n\n"
    
    return info

def get_disk_info():
    """Get disk usage information."""
    try:
        partitions = psutil.disk_partitions(all=False)
        
        reply = "💾 *Disk Usage Information:*\n\n"
        processed_mountpoints = set()
        
        # Process partitions from psutil
        for partition in partitions:
            if os.name == 'nt':
                if 'cdrom' in partition.opts or partition.fstype == '':
                    # Skip CD-ROM drives on Windows
                    continue
            
            # Skip certain partitions
            if should_skip_partition(partition.mountpoint, partition.fstype):
                continue
            
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                
                # Convert to GB
                total_gb = usage.total / (1024 ** 3)
                used_gb = usage.used / (1024 ** 3)
                free_gb = usage.free / (1024 ** 3)
                
                reply += format_partition_info(
                    partition.mountpoint, total_gb, used_gb, free_gb, usage.percent
                )
                
                processed_mountpoints.add(partition.mountpoint)
                
            except PermissionError:
                continue
        
        # Add any missing partitions
        additional_mountpoints = get_additional_partitions()
        for mountpoint in additional_mountpoints:
            if mountpoint not in processed_mountpoints:
                try:
                    usage = psutil.disk_usage(mountpoint)
                    
                    # Convert to GB
                    total_gb = usage.total / (1024 ** 3)
                    used_gb = usage.used / (1024 ** 3)
                    free_gb = usage.free / (1024 ** 3)
                    
                    reply += format_partition_info(
                        mountpoint, total_gb, used_gb, free_gb, usage.percent
                    )
                except Exception:
                    continue
        
        # Add total I/O statistics
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