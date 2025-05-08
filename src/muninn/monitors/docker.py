"""
Docker containers monitoring
"""

import logging
import docker
from docker.errors import DockerException

logger = logging.getLogger(__name__)

def get_docker_info():
    """Get information about running Docker containers."""
    try:
        # Use unix socket connection instead of http+docker
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        containers = client.containers.list()
        
        if not containers:
            return "No Docker containers are currently running."
        
        reply = "🐳 *Running Docker containers:*\n\n"
        for container in containers:
            name = container.name
            image = container.image.tags[0] if container.image.tags else container.image.id[:12]
            status = container.status
            
            reply += f"*{name}*\n"
            reply += f"├─ Image: `{image}`\n"
            reply += f"├─ Status: `{status}`\n"
            
            ports = container.ports
            if ports:
                port_info = []
                for port, bindings in ports.items():
                    if bindings:
                        for binding in bindings:
                            host_ip = binding.get('HostIp', '')
                            host_port = binding.get('HostPort', '')
                            if host_ip == '0.0.0.0' or not host_ip:
                                host_ip = 'localhost'
                            port_info.append(f"{host_ip}:{host_port}->{port}")
                    else:
                        port_info.append(f"{port}")
                reply += f"└─ Ports: `{', '.join(port_info)}`\n\n"
            else:
                reply += f"└─ Ports: None\n\n"
            
        return reply
    
    except DockerException as e:
        logger.error(f"Error in get_docker_info: {e}")
        return f"Error connecting to Docker: {e}"
    except Exception as e:
        logger.error(f"Error in get_docker_info: {e}")
        return f"Error retrieving Docker information: {e}" 