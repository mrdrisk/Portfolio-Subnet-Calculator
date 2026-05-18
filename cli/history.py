#!/usr/bin/env python3
"""
history.py
SQLite history management for the subnet calculator CLI.
Handles saving, retrieving, and displaying past queries.
"""
 
import sqlite3
import os
from datetime import datetime
 
# Store the DB next to this file so it's always findable
DB_PATH = os.path.join(os.path.dirname(__file__), "history.db")
HISTORY_LIMIT = 50
 
 
def _get_connection() -> sqlite3.Connection:
    """Open a connection and ensure the history table exists."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            cidr_input   TEXT    NOT NULL,
            network      TEXT    NOT NULL,
            prefix_len   INTEGER NOT NULL,
            num_hosts    INTEGER NOT NULL,
            calculated_at TEXT   NOT NULL
        )
    """)
    conn.commit()
    return conn
 
 
def save_entry(cidr: str) -> None:
    """
    Save a subnet query to history.
    Silently skips saving if the same CIDR was the most recent entry.
    """
    from subnet_utils import calculate_subnet
 
    try:
        info = calculate_subnet(cidr)
    except ValueError:
        return  # Don't save invalid inputs
 
    conn = _get_connection()
    try:
        # Skip duplicate consecutive entries
        last = conn.execute(
            "SELECT cidr_input FROM history ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if last and last["cidr_input"] == cidr:
            return
 
        conn.execute(
            """
            INSERT INTO history (cidr_input, network, prefix_len, num_hosts, calculated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                cidr,
                info["network"],
                int(info["prefix_len"]),
                int(info["num_hosts"]),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
 
        # Trim to HISTORY_LIMIT rows
        conn.execute(
            f"""
            DELETE FROM history
            WHERE id NOT IN (
                SELECT id FROM history ORDER BY id DESC LIMIT {HISTORY_LIMIT}
            )
            """
        )
        conn.commit()
    finally:
        conn.close()
 
 
def get_history(limit: int = 20) -> list:
    """Return the most recent history entries as a list of dicts."""
    conn = _get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
 
 
def print_history(limit: int = 20) -> None:
    """Print history to stdout in a readable table format."""
    rows = get_history(limit)
 
    if not rows:
        print("No history yet. Run a calculation first.")
        return
 
    col_cidr = max(len(r["cidr_input"]) for r in rows)
    col_net  = max(len(f"{r['network']}/{r['prefix_len']}") for r in rows)
 
    header = (
        f"  {'#':<4} "
        f"{'Input':<{col_cidr}}  "
        f"{'Network':<{col_net}}  "
        f"{'Hosts':<10}  "
        f"Calculated At"
    )
    print()
    print(header)
    print("  " + "─" * (len(header) - 2))
 
    for i, row in enumerate(rows, start=1):
        network_str = f"{row['network']}/{row['prefix_len']}"
        print(
            f"  {i:<4} "
            f"{row['cidr_input']:<{col_cidr}}  "
            f"{network_str:<{col_net}}  "
            f"{row['num_hosts']:<10}  "
            f"{row['calculated_at']}"
        )
 
    print()
 
 
def clear_history() -> None:
    """Delete all history entries."""
    conn = _get_connection()
    try:
        conn.execute("DELETE FROM history")
        conn.commit()
    finally:
        conn.close()