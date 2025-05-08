"""
Combined monitor that provides access to all monitoring functions
"""

from .status import get_status_info
from .load import get_load_info
from .disk import get_disk_info
from .docker import get_docker_info
from .network import get_network_info

class Monitors:
    """Class to access all monitoring functions."""
    
    @staticmethod
    def get_status_info():
        """Get server status information."""
        return get_status_info()
    
    @staticmethod
    def get_load_info():
        """Get server load information."""
        return get_load_info()
    
    @staticmethod
    def get_disk_info():
        """Get disk usage information."""
        return get_disk_info()
    
    @staticmethod
    def get_docker_info():
        """Get information about running Docker containers."""
        return get_docker_info()
    
    @staticmethod
    def get_network_info():
        """Get network information."""
        return get_network_info() 