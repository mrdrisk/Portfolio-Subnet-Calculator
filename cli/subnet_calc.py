#!/usr/bin/env python3
"""
subnet_calc.py
CLI entry point for the subnet calculator.
Computes subnet info from a CIDR string and logs the result to history.db.
 
Usage:
    python3 subnet_calc.py 192.168.1.0/24
    python3 subnet_calc.py 10.0.0.0/8 --no-history
    python3 subnet_calc.py --history
"""
 
import argparse
import sys
import os
 
# Ensure cli/ sibling modules (subnet_utils, history) are always importable
# regardless of working directory or how this script is invoked.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
 
from subnet_utils import calculate_subnet
from history import save_entry, print_history
 
 
def print_result(cidr: str) -> None:
    """Calculate and print subnet info for a given CIDR string."""
    try:
        info = calculate_subnet(cidr)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
 
    # Column width for alignment
    col = 18
    print()
    print(f"  {'Network Address':<{col}} {info['network']}/{info['prefix_len']}")
    print(f"  {'Subnet Mask':<{col}} {info['netmask']}")
    print(f"  {'Wildcard Mask':<{col}} {info['wildcard_mask']}")
    print(f"  {'Broadcast':<{col}} {info['broadcast']}")
    print(f"  {'Host Range':<{col}} {info['host_min']} – {info['host_max']}")
    print(f"  {'Usable Hosts':<{col}} {info['num_hosts']}")
    print(f"  {'Total Addresses':<{col}} {info['total_addresses']}")
    print(f"  {'IP Class':<{col}} {info['ip_class']}")
    print(f"  {'Scope':<{col}} {info['scope']}")
    print()
 
 
def main() -> None:
    parser = argparse.ArgumentParser(
        prog="subnet_calc",
        description="IPv4 subnet calculator — CIDR notation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python3 subnet_calc.py 192.168.1.0/24\n"
               "  python3 subnet_calc.py 10.0.0.0/8 --no-history\n"
               "  python3 subnet_calc.py --history",
    )
    parser.add_argument(
        "cidr",
        nargs="?",
        help="Network in CIDR notation (e.g. 192.168.1.0/24)",
    )
    parser.add_argument(
        "--no-history",
        action="store_true",
        help="Do not save this query to history",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Print calculation history and exit",
    )
 
    args = parser.parse_args()
 
    if args.history:
        print_history()
        return
 
    if not args.cidr:
        parser.print_help()
        sys.exit(1)
 
    print_result(args.cidr)
 
    if not args.no_history:
        save_entry(args.cidr)
 
 
if __name__ == "__main__":
    main()