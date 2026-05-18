import platform
import subprocess
import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor

def ping_ip(ip):
    """
    Pings an IP address and returns True if it responds, False otherwise.
    Adjusts flags based on whether the OS is Windows or Unix-based.
    """
    current_os = platform.system().lower()
    
    if current_os == "windows":
        # -n 1: send 1 packet, -w 500: timeout after 500ms
        command = ["ping", "-n", "1", "-w", "500", str(ip)]
    else:
        # -c 1: send 1 packet, -W 1: timeout after 1 second
        command = ["ping", "-c", "1", "-W", "1", str(ip)]
        
    try:
        # Run the ping command silently
        output = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output.returncode == 0
    except Exception:
        return False

def get_hostname(ip):
    """
    Attempts to resolve the hostname of the IP address.
    """
    try:
        hostname, _, _ = socket.gethostbyaddr(str(ip))
        return hostname
    except (socket.herror, socket.gaierror):
        return "Unknown Hostname"

def check_address(ip):
    """
    Worker function to check an IP and print results if it's active.
    """
    if ping_ip(ip):
        hostname = get_hostname(ip)
        print(f"[+] Active: {ip:<15} | Hostname: {hostname}")

def scan_network(ip_range):
    """
    Generates the list of IPs from the network range and scans them concurrently.
    """
    print(f"Scanning range: {ip_range}...")
    print("-" * 50)
    
    try:
        # Create a network object (strict=False allows parsing ranges like 10.0.0.1/24)
        network = ipaddress.ip_network(ip_range, strict=False)
        
        # Use ThreadPoolExecutor to speed up the ping requests
        # max_workers=50 strikes a good balance between speed and network resource usage
        with ThreadPoolExecutor(max_workers=50) as executor:
            executor.map(check_address, network.hosts())
            
    except ValueError as e:
        print(f"Error parsing IP range: {e}")
    
    print("-" * 50)
    print("Scan complete.")

if __name__ == "__main__":
    # Define your target range using CIDR notation.
    # '10.0.0.0/24' covers 10.0.0.1 to 10.0.0.254
    target_range = "10.0.0.0/24" 
    
    scan_network(target_range)