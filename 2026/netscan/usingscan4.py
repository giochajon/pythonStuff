import scan4

# Example 1: Quick ping sweep (no ports)
fast_results = scan4.scan_network()

# Example 2: Sweep with default ports scanned
detailed_results = scan4.scan_network(do_port_scan=True)

# Example 3: Sweep specific network looking ONLY for web servers (ports 80, 443)
web_servers = scan4.scan_network(
    network_range="192.168.50.0/24", 
    do_port_scan=True, 
    ports=[80, 443]
)

for device in web_servers:
    print(device)