import subprocess
import socket
import ipaddress
import argparse
from concurrent.futures import ThreadPoolExecutor

# Common ports to check
DEFAULT_PORTS = [21, 22, 23, 53, 80, 111, 135, 139, 443, 445, 3306, 3389, 8080, 8443]

def get_local_ip_and_range():
    """Automatically detects the machine's local IP and creates a /24 network range."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        ip_parts = local_ip.split('.')
        detected_range = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
        return local_ip, detected_range
    except Exception:
        return "127.0.0.1", None

def ping_ip(ip):
    """Pings the IP. Returns True if alive, False otherwise."""
    command = ["ping", "-c", "1", "-W", "2", str(ip)]
    try:
        output = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output.returncode == 0
    except Exception:
        return False

def get_hostname(ip):
    """Returns the hostname of the IP or None if it cannot be resolved."""
    try:
        hostname, _, _ = socket.gethostbyaddr(str(ip))
        return hostname
    except (socket.herror, socket.gaierror):
        return None

def check_port(ip, port, timeout=0.5):
    """Attempts a TCP connection to a specific port on the IP."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((str(ip), port))
        return port
    except (socket.timeout, ConnectionRefusedError, OSError):
        return None
    finally:
        s.close()

def scan_ports_for_ip(ip, ports=None, max_workers=10):
    """Scans a list of ports concurrently for a specific IP."""
    if ports is None:
        ports = DEFAULT_PORTS
        
    open_ports = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(check_port, ip, port) for port in ports]
        for future in futures:
            result = future.result()
            if result:
                open_ports.append(result)
                
    return sorted(open_ports)

def analyze_host(ip, do_port_scan=False, ports=None):
    """Pings IP, and if alive, grabs hostname and (optionally) open ports."""
    if ping_ip(ip):
        hostname = get_hostname(ip)
        open_ports = scan_ports_for_ip(ip, ports) if do_port_scan else []
        return {
            "ip": str(ip),
            "is_active": True,
            "hostname": hostname,
            "open_ports": open_ports
        }
    return {"ip": str(ip), "is_active": False}

def scan_network(network_range=None, do_port_scan=False, ports=None, max_workers=50):
    """Scans an entire network range."""
    if not network_range:
        _, network_range = get_local_ip_and_range()
        if not network_range:
            raise ValueError("Could not detect local network range.")

    network = ipaddress.ip_network(network_range, strict=False)
    active_hosts = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(analyze_host, ip, do_port_scan, ports) for ip in network.hosts()]
        for future in futures:
            result = future.result()
            if result["is_active"]:
                active_hosts.append(result)

    return active_hosts

if __name__ == "__main__":
    import sys
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="A local network scanner.")
    parser.add_argument("-t", "--target", help="Specific network range to scan (e.g., 192.168.1.0/24). If omitted, auto-detects.", default=None)
    parser.add_argument("-p", "--ports", help="Enable port scanning for discovered hosts.", action="store_true")
    args = parser.parse_args()
    
    target_range = args.target
    if not target_range:
        local_ip, target_range = get_local_ip_and_range()
        if not target_range or local_ip.startswith("127."):
            print("[-] Error: Could not detect an active local network interface.")
            sys.exit(1)
        print(f"[*] Auto-detected Target Range: {target_range}")
    else:
        print(f"[*] Manual Target Range: {target_range}")
        
    print(f"[*] Port Scanning is {'ENABLED' if args.ports else 'DISABLED'}")
    print(f"[*] Beginning scan...")
    print("-" * 60)
    
    # Run the scan with the provided arguments
    results = scan_network(network_range=target_range, do_port_scan=args.ports)
    
    for host in results:
        print(f"[+] Active: {host['ip']:<15} | Hostname: {str(host['hostname']):<20}")
        if args.ports:
            print(f"    Open Ports: {host['open_ports'] if host['open_ports'] else 'None detected from default list'}")
        
    print("-" * 60)
    print(f"Scan complete. Found {len(results)} active device(s).")