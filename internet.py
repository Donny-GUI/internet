import socket
import requests
import uuid
import time
#typing
from typing import Dict, NewType, List, Tuple
# site-packages
import netifaces
# local-packages
from opsys import OperatingSystem


# new types
InternetProtocolAddress = NewType("InternetProtocolAddress", str)
InternetConnection = NewType("InternetConnection", Tuple[bool, str])
NetworkMask = NewType("NetworkMask", str)
GlobalUniqueID = NewType('GlobalUniqueID', str)
NetworkInterface = NewType('NetworkInterface', Dict[str, GlobalUniqueID | NetworkMask | InternetProtocolAddress])
NetworkInterfaces = NewType('NetworkInterfaces', List[NetworkInterface])


# collections
dns_servers = [
    "8.8.8.8",       # Google DNS
    "8.8.4.4",       # Google DNS
    "1.1.1.1",       # Cloudflare DNS
    "1.0.0.1",       # Cloudflare DNS
    "9.9.9.9",       # Quad9 DNS
    "149.112.112.112", # Quad9 DNS
    "208.67.222.222", # OpenDNS
    "208.67.220.220", # OpenDNS
    "64.6.64.6",     # Verisign
    "64.6.65.6",     # Verisign
    "77.88.8.8",     # Yandex DNS
    "77.88.8.1",     # Yandex DNS
    "176.103.130.130", # AdGuard DNS
    "176.103.130.131", # AdGuard DNS
    "185.228.168.9", # CleanBrowsing DNS
    "185.228.168.10" # CleanBrowsing DNS
]

     

def list_available_networks():
    return OperatingSystem.get_available_networks()

def guid_to_hexadecimal(guid_str: GlobalUniqueID) -> bytes:
    """
    Takes a guid str and returns the hexadecimal representation
    Returns:
        bytes : hexadecimal representation of guid string
    """
    guid = uuid.UUID(guid_str)
    return guid.hex

def get_internal_ip() -> InternetProtocolAddress:
    """
    Retrieves internal ip address as string.

    Returns:
        - The local IP address of the device (str)

    """
    # Get local IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for server in dns_servers:
        try:
            s.connect((server, 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            continue
    return None

def get_network_interfaces() -> Dict[str, Dict[str, str]]:
    """
    Retrieves information about network interfaces.
    Returns:
        - A dictionary of network interfaces with their 
          IP addresses and netmasks (Dict[str, Dict[str, str]])
    """
    interface_info = []
    for interface in netifaces.interfaces():
        try:
            interface_str = str(interface)[1:-1]
            addr = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
            mask = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['netmask']
            interface_info.append({'ip': addr, 'netmask': mask, 'name': interface_str})
        except:
            pass

    return interface_info

def get_connection_info() -> Dict[str, Dict[str, str|NetworkInterfaces]]:
    """
    Retrieves information about the current internet connection.

    Returns:
        A dictionary containing the following keys:
        - 'local_ip': The local IP address of the device (str)
        - 'external_ip': The external IP address of the device (str)
        - 'connection_speed': The estimated connection speed in requests per second (str)
        - 'network_interfaces': A dictionary of network interfaces with their IP addresses and netmasks (Dict[str, Dict[str, str]])
    """
    # Get local IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    # Get external IP address
    external_ip = requests.get('https://api.ipify.org').text

    # Get connection speed
    try:
        start_time = time.time()
        requests.get('https://www.google.com')
        end_time = time.time()
        connection_speed = round(1 / (end_time - start_time), 2)
    except:
        connection_speed = "Unknown"
    
    # Get network interface information
    interface_info: NetworkInterfaces = get_network_interfaces()
    
    return {'local_ip': local_ip,
            'external_ip': external_ip,
            'connection_speed': str(connection_speed),
            'network_interfaces': interface_info}

def is_internet_available() -> bool:
    """
    Checks if the internet is available by attempting to connect to Google's public DNS server.

    Returns:
        bool: True if the internet is available, False otherwise.
    """
    try:
        # Connect to one of Google's public DNS servers
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        pass
    return False

def check_internet_connection() -> InternetConnection:
    """
    Checks if there is an active internet connection.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating if there is an internet connection and a string message.
    """
    try:
        # Try to connect to a known IP address
        socket.create_connection(("www.google.com", 80))
        return True, "Internet connection available."
    except OSError as e:
        # Handle permission errors
        if e.errno == 13:
            return False, "Permission error: Unable to check internet connection."
        # Handle connection errors
        elif e.errno == 101:
            return False, "Connection error: No internet connection available."
        else:
            return False, f"Error checking internet connection: {e}"
    except Exception as e:
        return False, f"Unexpected error checking internet connection: {e}"
