import os
import sys
from transmission_rpc import Client

# --- CONFIGURATION ---
HOST = 'localhost'
PORT = 9091
TARGET_RATIO = 2.0

# Fetch credentials securely from environment variables
USER = os.environ.get('TRANSMIUSER')
PASSWORD = os.environ.get('TRANSMIPASS')
# ---------------------

def pause_high_ratio_torrents():
    try:
        # Inform the user about auth status without leaking the actual password
        if USER:
            print(f"Connecting to Transmission at http://{HOST}:{PORT} as user: {USER}...")
        else:
            print(f"Connecting to Transmission at http://{HOST}:{PORT} (No environment credentials found)...")

        # Initialize connection to Transmission web interface API
        c = Client(host=HOST, port=PORT, username=USER, password=PASSWORD)
        
        # Fetch all torrents with only the fields we need to optimize performance
        torrents = c.get_torrents(arguments=['id', 'name', 'uploadRatio', 'status'])
        
        paused_count = 0
        print(f"\nScanning for torrents with a ratio >= {TARGET_RATIO}...\n")
        
        for torrent in torrents:
            # Check if the torrent is currently active/downloading/seeding
            # 'stopped' means it is already paused
            if torrent.status != 'stopped':
                
                # Check if the current upload ratio meets or exceeds your target
                if torrent.upload_ratio >= TARGET_RATIO:
                    print(f"Match Found: '{torrent.name}'")
                    print(f"  -> Current Ratio: {torrent.upload_ratio:.2f}")
                    print(f"  -> Sending pause command...")
                    
                    # Pause the specific torrent by its unique ID
                    c.pause_torrent(torrent.id)
                    paused_count += 1
                    print("-" * 40)
                    
        print(f"\nTask complete. Total torrents paused: {paused_count}")

    except Exception as e:
        print(f"\n[Error] Could not connect or communicate with Transmission: {e}")
        print("Please ensure Transmission is running, 'Allow remote access' is enabled,")
        print("and your TRANSMIUSER / TRANSMIPASS environment variables are correct.")

if __name__ == "__main__":
    pause_high_ratio_torrents()