import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from mcp_servers.sonic_mcp.tools.sonic_interface import configure_interface_ip, get_interface_ip_addresses



if __name__ == "__main__":
    result = get_interface_ip_addresses(
        device_ip="192.168.200.21",
        username="admin",
        password="YourPaSsWoRd"
    )
    print(result)