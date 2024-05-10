import subprocess
from platform import system



class _OperatingSystem:
    _system = system()
    NAME = _system
    list_networks_command = "netsh wlan show networks"

    if _system == 'Linux':
        list_networks_command = "nmcli device wifi list"
    elif _system == 'Darwin':
        list_networks_command = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s"
    
    @staticmethod
    def parse_network_address(address: str):
        return address.split()[0] if _OperatingSystem.NAME == "Darwin" else address.split(":")[1].strip()

    @staticmethod
    def get_available_networks():
        ssids = []
        output = subprocess.check_output(_OperatingSystem.list_networks_command, shell=True, text=True)
        for line in output.splitlines():
            if "SSID" in line:
                ssids.append(_OperatingSystem.parse_network_address(line))
        return ssids

# Assigning the class itself, not an instance of it
OperatingSystem = _OperatingSystem
