#!/usr/bin/env python3
"""
subnet_utils.py
Pure subnet calculation logic — no I/O, no side effects.
Used by both the CLI (subnet_calc.py) and any future API layer.
"""
 
import ipaddress
from typing import Dict
 
 
def get_ip_class(ip: str) -> str:
    """Return the classful class (A/B/C/D/E) of an IPv4 address."""
    first_octet = int(ip.split(".")[0])
    if first_octet < 128:
        return "A"
    if first_octet < 192:
        return "B"
    if first_octet < 224:
        return "C"
    if first_octet < 240:
        return "D (Multicast)"
    return "E (Reserved)"
 
 
def get_scope(network: ipaddress.IPv4Network) -> str:
    """Return 'Private (RFC 1918)' or 'Public' for a given network."""
    return "Private (RFC 1918)" if network.is_private else "Public"
 
 
def calculate_subnet(cidr: str) -> Dict[str, str]:
    """
    Given a CIDR notation string, return a dict of subnet information.
 
    Args:
        cidr: IPv4 network in CIDR notation, e.g. "192.168.1.10/24".
              Host bits may be set — they are masked to the network address.
 
    Returns:
        Dict with keys: network, broadcast, netmask, wildcard_mask,
        prefix_len, host_min, host_max, num_hosts, total_addresses,
        ip_class, scope.
 
    Raises:
        ValueError: if the input is not valid CIDR notation.
    """
    try:
        net = ipaddress.ip_network(cidr, strict=False)
    except ValueError:
        raise ValueError(
            f'"{cidr}" is not valid CIDR notation. '
            "Expected format: x.x.x.x/prefix (e.g. 192.168.1.0/24)"
        )
 
    network_addr   = str(net.network_address)
    broadcast_addr = str(net.broadcast_address)
    prefix_len     = net.prefixlen
    total          = net.num_addresses
 
    # Wildcard mask = bitwise NOT of subnet mask
    wildcard = str(net.hostmask)
 
    # Host range — handle /31 (RFC 3021) and /32 as special cases
    if prefix_len <= 30:
        host_min  = str(net.network_address + 1)
        host_max  = str(net.broadcast_address - 1)
        num_hosts = total - 2
    elif prefix_len == 31:
        # RFC 3021: both addresses usable on point-to-point links
        host_min  = network_addr
        host_max  = broadcast_addr
        num_hosts = 2
    else:
        # /32: single host route
        host_min  = network_addr
        host_max  = network_addr
        num_hosts = 1
 
    return {
        "network":         network_addr,
        "broadcast":       broadcast_addr,
        "netmask":         str(net.netmask),
        "wildcard_mask":   wildcard,
        "prefix_len":      str(prefix_len),
        "host_min":        host_min,
        "host_max":        host_max,
        "num_hosts":       str(num_hosts),
        "total_addresses": str(total),
        "ip_class":        get_ip_class(network_addr),
        "scope":           get_scope(net),
    }