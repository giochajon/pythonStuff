import subprocess
import socket
import ipaddress
import sys
from concurrent.futures import ThreadPoolExecutor

def check_ping_tool():
    """
    Checks if the 'ping' command exists on this Ubuntu system.
    """
    try:
        subprocess.run(["ping", "-V"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def ping_ip(ip):
    """
    Ubuntu-specific ping command.
    -c 1: Send exactly 1 packet
    -W 1: Timeout after 1 second if no response
    """
    command = ["ping", "-c", "1", "-W", "1", str(ip)]
    try:
        output = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output.returncode == 0
    except Exception:
        return False

def get_hostname(ip):
    """
    Attempts to resolve local hostname via DNS/hosts.
    """
    try:
        hostname, _, _ = socket.gethostbyaddr(str(ip))
        return hostname
    except (socket.herror, socket.gaierror):
        return "Unknown Hostname"

def check_address(ip):
    """
    Worker function for the thread pool.
    """
    if ping_ip(ip):
        hostname = get_hostname(ip)
        print(f"[+] Active: {ip:<15} | Hostname: {hostname}")

def scan_network(ip_range):
    # Enforce the dependency check so we don't fail silently
    if not check_ping_tool():
        print("[-] Error: The 'ping' utility is missing from this Ubuntu system.")
        print("    Fix it by running: sudo apt install iputils-ping")
        sys.exit(1)

    print(f"Scanning Ubuntu network range: {ip_range}...")
    print("-" * 60)
    
    try:
        # strict=False allows inputting individual IPs (like 10.0.0.1/24) 
        # and automatically scales it to the full subnet range.
        network = ipaddress.ip_network(ip_range, strict=False)
        
        # Ubuntu handles threading incredibly well; bumping workers to 100 for speed
        with ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(check_address, network.hosts())
            
    except ValueError as e:
        print(f"[-] Error parsing IP range: {e}")
    
    print("-" * 60)
    print("Scan complete.")

if __name__ == "__main__":
    # Adjust this to your specific network subnet
    TARGET_RANGE = "10.0.0.0/24" 
    
    scan_network(TARGET_RANGE)