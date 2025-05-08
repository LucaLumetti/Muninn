"""
Network monitoring
"""

import logging
import psutil
import socket
import subprocess
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

def escape_html(text):
    """Escape HTML special characters."""
    if not isinstance(text, str):
        text = str(text)
    
    # Replace special characters with their HTML entities
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    
    return text

def get_service_for_port(port, protocol="tcp"):
    """Try to determine which service is using a specific port."""
    try:
        # First try to use /etc/services to find standard services
        with open("/etc/services") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    service_info = parts[1].split("/")
                    if len(service_info) == 2 and service_info[0].isdigit():
                        service_port = int(service_info[0])
                        service_proto = service_info[1]
                        if service_port == port and service_proto == protocol:
                            return parts[0]
        
        # If not found in services file, try to get process name
        connections = psutil.net_connections(kind=protocol)
        for conn in connections:
            # Handle both namedtuple and tuple formats for compatibility
            if hasattr(conn, 'laddr') and hasattr(conn.laddr, 'port'):
                conn_port = conn.laddr.port
            elif len(conn.laddr) >= 2:  # If it's a tuple
                conn_port = conn.laddr[1]
            else:
                continue
                
            if conn_port == port:
                try:
                    process = psutil.Process(conn.pid)
                    return process.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                
        return "Unknown"
    
    except Exception as e:
        logger.error(f"Error getting service for port {port}: {e}")
        return "Unknown"

def get_public_ip():
    """Get the public IP address of the server."""
    try:
        # Try different services to get public IP
        services = [
            "curl -s ifconfig.me",
            "curl -s ipinfo.io/ip",
            "curl -s api.ipify.org",
            "dig +short myip.opendns.com @resolver1.opendns.com"
        ]
        
        for cmd in services:
            try:
                result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                continue
        
        return "Unknown"
    
    except Exception as e:
        logger.error(f"Error getting public IP: {e}")
        return "Unable to determine public IP"

def get_active_connections():
    """Get information about active network connections."""
    try:
        # Get all network connections
        connections = psutil.net_connections(kind='inet')
        
        # Group connections by status and protocol
        grouped = defaultdict(lambda: defaultdict(int))
        
        # Count connections per status and protocol
        for conn in connections:
            proto = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
            status = conn.status if conn.status else "UNKNOWN"
            grouped[proto][status] += 1
        
        # Format the connections report
        connection_info = "<b>Connection Statistics:</b>\n"
        
        for proto, statuses in grouped.items():
            connection_info += f"<b>{proto}:</b> "
            status_parts = []
            for status, count in statuses.items():
                status_parts.append(f"{status}: {count}")
            connection_info += ", ".join(status_parts) + "\n"
        
        return connection_info
    
    except Exception as e:
        logger.error(f"Error getting active connections: {e}")
        return "Error retrieving connection information"

def get_listening_ports():
    """Get information about open/listening ports and the services using them."""
    try:
        # Get connections that are listening
        connections = psutil.net_connections(kind='inet')
        listening = [conn for conn in connections if conn.status == 'LISTEN']
        
        # Sort by port number
        listening.sort(key=lambda x: x.laddr[1] if isinstance(x.laddr, tuple) else x.laddr.port) # noqa
        
        # Format the listening ports report
        if not listening:
            return "<b>No listening ports found</b>"
        
        listening_info = "<b>Open Ports:</b>\n"
        
        for conn in listening:
            try:
                protocol = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
                
                # Handle both namedtuple and tuple formats for compatibility
                if hasattr(conn, 'laddr') and hasattr(conn.laddr, 'port'):
                    port = conn.laddr.port
                    addr = conn.laddr.ip
                else:  # It's a tuple
                    port = conn.laddr[1]
                    addr = conn.laddr[0]
                
                # Get process information if possible
                process_name = "Unknown"
                cmdline = "N/A"
                try:
                    process = psutil.Process(conn.pid)
                    process_name = escape_html(process.name())
                    cmd_parts = process.cmdline()
                    if cmd_parts:
                        cmdline = escape_html(" ".join(cmd_parts))
                        if len(cmdline) > 40:
                            cmdline = cmdline[:37] + "..."
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                
                # Get service information
                service = escape_html(get_service_for_port(port, protocol.lower()))
                
                listening_info += f"<b>{addr}:{port} ({protocol})</b>\n"
                listening_info += f"├─ Service: <code>{service if service != process_name else 'N/A'}</code>\n"
                listening_info += f"├─ Process: <code>{process_name}</code>\n"
                listening_info += f"└─ Command: <code>{cmdline}</code>\n\n"
            
            except Exception as e:
                logger.error(f"Error processing connection {conn}: {e}")
                continue
        
        return listening_info
    
    except Exception as e:
        logger.error(f"Error getting listening ports: {e}")
        return "Error retrieving port information"

def get_network_interfaces():
    """Get information about network interfaces."""
    try:
        # Get network addresses
        addrs = psutil.net_if_addrs()
        # Get network stats
        stats = psutil.net_if_stats()
        
        # Format the interfaces report
        interfaces_info = "<b>Network Interfaces:</b>\n\n"
        
        for interface, addr_list in addrs.items():
            # Skip loopback interfaces
            if interface.startswith("lo"):
                continue
                
            # Get interface status
            is_up = stats[interface].isup if interface in stats else False
            interface_speed = stats[interface].speed if interface in stats else 0
            
            status_icon = "🟢" if is_up else "🔴"
            
            interfaces_info += f"{status_icon} <b>{escape_html(interface)}</b>"
            if interface_speed > 0:
                interfaces_info += f" ({interface_speed} Mbps)"
            interfaces_info += "\n"
            
            # Add addresses
            for addr in addr_list:
                if addr.family == socket.AF_INET:
                    interfaces_info += f"├─ IPv4: <code>{escape_html(addr.address)}</code>\n"
                    interfaces_info += f"├─ Netmask: <code>{escape_html(addr.netmask)}</code>\n"
                elif addr.family == socket.AF_INET6:
                    interfaces_info += f"├─ IPv6: <code>{escape_html(addr.address)}</code>\n"
                elif addr.family == psutil.AF_LINK:
                    interfaces_info += f"├─ MAC: <code>{escape_html(addr.address)}</code>\n"
            
            # Add traffic statistics if available
            try:
                io_counters = psutil.net_io_counters(pernic=True)
                if interface in io_counters:
                    sent_mb = io_counters[interface].bytes_sent / (1024 * 1024)
                    recv_mb = io_counters[interface].bytes_recv / (1024 * 1024)
                    
                    interfaces_info += f"├─ Sent: <code>{sent_mb:.2f} MB</code>\n"
                    interfaces_info += f"└─ Received: <code>{recv_mb:.2f} MB</code>\n\n"
                else:
                    interfaces_info += "└─ No traffic statistics available\n\n"
            except Exception as e:
                logger.error(f"Error getting interface stats: {e}")
                interfaces_info += "└─ No traffic statistics available\n\n"
        
        return interfaces_info
    
    except Exception as e:
        logger.error(f"Error getting network interfaces: {e}")
        return "Error retrieving interface information"

def get_network_info():
    """Get comprehensive network information."""
    try:
        # Get public IP
        public_ip = get_public_ip()
        
        # Build the complete network report
        report = "🌐 <b>Network Information:</b>\n\n"
        report += f"<b>Public IP:</b> <code>{escape_html(public_ip)}</code>\n\n"
        
        # Add network interfaces
        report += get_network_interfaces()
        
        # Add open/listening ports
        report += get_listening_ports()
        
        # Add active connections statistics
        report += get_active_connections()
        
        # Truncate if too long for Telegram (max ~4096 chars)
        if len(report) > 4000:
            report = report[:3950] + "\n\n... <b>Output truncated due to size limits</b> ..."
        
        return report
    
    except Exception as e:
        logger.error(f"Error in get_network_info: {e}")
        return f"Error retrieving network information: {str(e)}" 