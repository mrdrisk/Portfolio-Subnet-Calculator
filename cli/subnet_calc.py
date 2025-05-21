#!/usr/bin/env python3
import argparse
import ipaddress
import sqlite3
import sys
from typing import Dict

# ─── Subnet Calculation Logic ────────────────────────────────────────────────
def calculate_subnet(cidr: str) -> Dict[str, str]:
    net = ipaddress.ip_network(cidr, strict=False)
    all_hosts = list(net.hosts())
    host_min, host_max = ("N/A","N/A")
    if len(all_hosts) >= 2:
        host_min, host_max = str(all_hosts[0]), str(all_hosts[-1])
    num_hosts = net.num_addresses - 2 if net.num_addresses >= 2 else 0

    return {
        "network":   str(net.network_address),
        "broadcast": str(net.broadcast_address),
        "netmask":   str(net.netmask),
        "prefix":    str(net.prefixlen),
        "host_min":  host_min,
        "host_max":  host_max,
        "num_hosts": str(num_hosts),
    }

# ─── SQLite Helper ───────────────────────────────────────────────────────────
DB_FILE = "history.db"
TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cidr TEXT NOT NULL,
    network TEXT,
    broadcast TEXT,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(TABLE_SCHEMA)
    conn.commit()
    conn.close()

def save_history(cidr: str, info: Dict[str,str]):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO history (cidr, network, broadcast) VALUES (?, ?, ?)",
        (cidr, info["network"], info["broadcast"])
    )
    conn.commit()
    conn.close()

def show_history(limit: int = 10):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT cidr, network, broadcast, calculated_at "
        "FROM history ORDER BY calculated_at DESC LIMIT ?",
        (limit,)
    )
    rows = c.fetchall()
    conn.close()
    if not rows:
        print("No history found.")
    else:
        print(f"Last {len(rows)} calculations:")
        for cidr, net, bc, ts in rows:
            print(f"  {ts} — {cidr} → net={net}, bc={bc}")

# ─── CLI Argument Parsing ────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Subnet Calculator CLI with history (SQLite)"
    )
    parser.add_argument(
        "cidr",
        nargs="?",
        help="Network in CIDR notation (e.g. 192.168.1.0/24)"
    )
    parser.add_argument(
        "--history", "-H",
        action="store_true",
        help="Show past calculations (up to --limit)"
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=10,
        help="Number of history entries to show (default: 10)"
    )
    args = parser.parse_args()

    # Initialize DB & table
    init_db()

    # If user asked for history, show and exit
    if args.history:
        show_history(limit=args.limit)
        sys.exit(0)

    # Require a CIDR if not showing history
    if not args.cidr:
        parser.print_usage()
        print("error: the following argument is required: cidr")
        sys.exit(1)

    # Calculate and display
    try:
        info = calculate_subnet(args.cidr)
    except ValueError as e:
        print(f"Invalid CIDR: {e}")
        sys.exit(1)

    print(f"Network:       {info['network']}/{info['prefix']}")
    print(f"Netmask:       {info['netmask']}")
    print(f"Broadcast:     {info['broadcast']}")
    print(f"Host range:    {info['host_min']} – {info['host_max']}")
    print(f"Usable hosts:  {info['num_hosts']}")

    # Save query in history
    save_history(args.cidr, info)

if __name__ == "__main__":
    main()
