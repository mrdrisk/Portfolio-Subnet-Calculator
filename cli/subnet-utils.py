import ipaddress
from typing import Dict

def calculate_subnet(cidr: str) -> Dict[str, str]:
    """
    Given a CIDR notation string (e.g. "192.168.1.0/24"), return
    network info: network, broadcast, mask, host_min, host_max, num_hosts.
    """
    # Create an IPv4Network object (strict=False allows host bits set)
    net = ipaddress.ip_network(cidr, strict=False)
    
    # Network and broadcast
    network_addr   = str(net.network_address)
    broadcast_addr = str(net.broadcast_address)
    
    # Netmask and prefix length
    netmask       = str(net.netmask)
    prefix_length = net.prefixlen
    
    # First and last usable hosts (if more than 2 hosts exist)
    all_hosts = list(net.hosts())
    if len(all_hosts) >= 2:
        host_min, host_max = str(all_hosts[0]), str(all_hosts[-1])
    else:
        # For /31 or /32 nets there aren’t two usable hosts
        host_min = host_max = "N/A"
    
    # Number of usable hosts
    num_hosts = net.num_addresses - 2 if net.num_addresses >= 2 else 0

    return {
        "network":      network_addr,
        "broadcast":    broadcast_addr,
        "netmask":      netmask,
        "prefix_len":   str(prefix_length),
        "host_min":     host_min,
        "host_max":     host_max,
        "num_hosts":    str(num_hosts)
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Subnet calculation utility")
    parser.add_argument("cidr", help="Network in CIDR notation (e.g. 10.0.0.0/16)")
    args = parser.parse_args()

    info = calculate_subnet(args.cidr)
    print(f"Network:    {info['network']}/{info['prefix_len']}")
    print(f"Netmask:    {info['netmask']}")
    print(f"Broadcast:  {info['broadcast']}")
    print(f"Host range: {info['host_min']} – {info['host_max']}")
    print(f"Usable hosts: {info['num_hosts']}")
