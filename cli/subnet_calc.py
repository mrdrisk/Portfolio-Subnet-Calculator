import argparse, ipaddress, sqlite3

parser = argparse.ArgumentParser(description="Subnet calculator CLI")
parser.add_argument("network", help="Network (CIDR notation, e.g., 10.0.0.0/16)")
args = parser.parse_args()

net = ipaddress.ip_network(args.network, strict=False)  # using ipaddress module:contentReference[oaicite:10]{index=10}
print("Network address:", net.network_address)
print("Broadcast address:", net.broadcast_address)
# More output as needed (host range, mask, etc.)

# Save to history DB
conn = sqlite3.connect('history.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS history
             (network TEXT, calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
c.execute('INSERT INTO history (network) VALUES (?)', (str(net),))
conn.commit()
conn.close()
