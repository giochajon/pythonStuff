import subprocess
import socket
import ipaddress
import sys
from concurrent.futures import ThreadPoolExecutor

def get_local_ip_and_range():
    """
    Automatically detects the machine's local IP and creates a /24 network range.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't actually connect, but forces OS to pick the correct outbound interface
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Turn "192.168.1.45" into "192.168.1.0/24"
        ip_parts = local_ip.split('.')
        detected_range = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
        return local_ip, detected_range
    except Exception:
        return "127.0.0.1", None

def ping_ip(ip):
    """
    Pings the IP. Uses a slightly longer timeout (-W 2) just in case the network is slow.
    """
    command = ["ping", "-c", "1", "-W", "2", str(ip)]
    try:
        output = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output.returncode == 0
    except Exception:
        return False

def get_hostname(ip):
    try:
        hostname, _, _ = socket.gethostbyaddr(str(ip))
        return hostname
    except (socket.herror, socket.gaierror):
        return "Unknown Hostname"

def check_address(ip):
    if ping_ip(ip):
        hostname = get_hostname(ip)
        # FIXED: Explicitly converted 'ip' to str(ip) so string formatting works perfectly
        print(f"[+] Active: {str(ip):<15} | Hostname: {hostname}")
        return True
    return False

def main():
    local_ip, target_range = get_local_ip_and_range()
    
    print(f"Your Local IP Address: {local_ip}")
    
    if not target_range or local_ip.startswith("127."):
        print("[-] Error: Could not detect an active local network interface.")
        print("    Are you connected to the internet/local Wi-Fi?")
        sys.exit(1)
        
    print(f"Auto-detected Target Range: {target_range}")
    print("-" * 60)
    
    network = ipaddress.ip_network(target_range, strict=False)
    
    # Track if we found at least one device
    active_count = 0
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(check_address, network.hosts()))
        active_count = sum(1 for r in results if r)
            
    print("-" * 60)
    print(f"Scan complete. Found {active_count} active device(s).")
    
    if active_count == 0:
        print("\n[!] TROUBLESHOOTING TIPS:")
        print(f"1. Try running this manually in your terminal: ping -c 3 {local_ip}")
        print("2. If you are inside WSL2 (Windows Subsystem for Linux), WSL cannot see")
        print("   your local physical LAN by default due to network isolation.")

if __name__ == "__main__":
    main()