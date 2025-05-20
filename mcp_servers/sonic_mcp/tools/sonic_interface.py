from mcp.server.fastmcp import FastMCP

import requests
from requests.auth import HTTPBasicAuth
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def configure_interface_ip(
    device_ip: str,
    username: str,
    password: str,
    interface_name: str,
    ip_prefix: str,
    family: str = "IPv4",
    scope: str = "global"
) -> dict:
    """
    Configure an IP address on a specified interface of a SONiC device via RESTCONF.

    Parameters:
    - device_ip: The management IP address of the SONiC device.
    - username: Username for authentication.
    - password: Password for authentication.
    - interface_name: Name of the interface (e.g., 'Ethernet0').
    - ip_prefix: IP address with prefix (e.g., '192.168.1.10/24').
    - family: IP family ('IPv4' or 'IPv6').
    - scope: Scope of the IP address ('global' or 'local').

    Returns:
    - A dictionary with the status and message of the operation.
    """
    url = f"https://{device_ip}/restconf/data/sonic-interface:sonic-interface/INTERFACE/INTERFACE_IPPREFIX_LIST"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }
    payload = {
        "sonic-interface:INTERFACE_IPPREFIX_LIST": [
            {
                "name": interface_name,
                "ip-prefix": ip_prefix,
                "family": family,
                "scope": scope
            }
        ]
    }

    try:
        response = requests.patch(
            url,
            json=payload,
            headers=headers,
            auth=HTTPBasicAuth(username, password),
            verify=False  # Set to True if using valid SSL certificates
        )

        if response.status_code in [200, 201, 204]:
            return {"status": "success", "message": f"IP {ip_prefix} configured on {interface_name}."}
        else:
            return {"status": "error", "message": f"Failed to configure IP. Status Code: {response.status_code}, Response: {response.text}"}

    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


def get_interface_ip_addresses(device_ip: str, username: str, password: str) -> dict:
    """
    Retrieves IP addresses assigned to interfaces from a SONiC device using RESTCONF.

    Parameters:
    - device_ip: Management IP of the SONiC device.
    - username: Username for RESTCONF authentication.
    - password: Password for RESTCONF authentication.

    Returns:
    - Dictionary mapping interface names to a list of assigned IP prefixes.
    """
    url = f"https://{device_ip}/restconf/data/sonic-interface:sonic-interface"
    headers = {"Accept": "application/yang-data+json"}
    auth = HTTPBasicAuth(username, password)

    try:
        response = requests.get(url, headers=headers, auth=auth, verify=False)

        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"Failed to fetch data. Code: {response.status_code}, Response: {response.text}"
            }

        data = response.json()
        ip_entries = data.get("sonic-interface:sonic-interface", {}).get("INTERFACE", {}).get("INTERFACE_IPADDR_LIST", [])

        result = {}
        for entry in ip_entries:
            portname = entry.get("portname")
            ip_prefix = entry.get("ip_prefix")
            if portname and ip_prefix:
                result.setdefault(portname, []).append(ip_prefix)

        return {"status": "success", "interfaces": result}

    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

