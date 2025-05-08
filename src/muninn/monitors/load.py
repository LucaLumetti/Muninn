"""
Server load monitoring
"""

import logging
import psutil
import subprocess
import re
from shutil import which

logger = logging.getLogger(__name__)

def get_nvidia_gpu_info():
    """Get information about NVIDIA GPUs using nvidia-smi."""
    if not which('nvidia-smi'):
        return None
    
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=index,name,temperature.gpu,utilization.gpu,utilization.memory,memory.used,memory.total,power.draw', 
             '--format=csv,noheader,nounits'],
            capture_output=True, text=True, check=True
        )
        
        gpus = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
                
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 8:
                gpu = {
                    'index': parts[0],
                    'name': parts[1],
                    'temp': parts[2],
                    'gpu_util': parts[3],
                    'mem_util': parts[4],
                    'mem_used': parts[5],
                    'mem_total': parts[6],
                    'power': parts[7]
                }
                gpus.append(gpu)
        
        return gpus
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.warning("nvidia-smi command failed")
        return None
    except Exception as e:
        logger.error(f"Error getting GPU info: {e}")
        return None

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
        
        # Get GPU information if available
        gpus = get_nvidia_gpu_info()
        if gpus:
            reply += f"\n*GPU Information:*\n"
            for i, gpu in enumerate(gpus):
                reply += f"*GPU {gpu['index']}: {gpu['name']}*\n"
                reply += f"├─ Temperature: `{gpu['temp']}°C`\n"
                reply += f"├─ GPU Usage: `{gpu['gpu_util']}%`\n"
                reply += f"├─ Memory: `{gpu['mem_used']} MB` / `{gpu['mem_total']} MB` (`{gpu['mem_util']}%`)\n"
                reply += f"└─ Power: `{gpu['power']} W`\n"
                
                # Add a separator between GPUs except for the last one
                if i < len(gpus) - 1:
                    reply += "\n"
        
        return reply
    
    except Exception as e:
        logger.error(f"Error in get_load_info: {e}")
        return f"Error retrieving load information: {e}" 