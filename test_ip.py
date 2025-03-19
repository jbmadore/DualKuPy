import subprocess
import socket

def get_ip_address():
    """
    Retrieves the Raspberry Pi's IP address on the network.
    
    Returns:
        str: The detected IP address, or None if no connection is found.
    """
    try:
        ip = subprocess.check_output("hostname -I", shell=True).decode().strip().split()
        return ip if ip else None
    except Exception as e:
        print(f"Error getting IP: {e}")
        return None
    
print(get_ip_address())