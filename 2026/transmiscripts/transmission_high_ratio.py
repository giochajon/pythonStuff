#!/usr/bin/env python3
"""
List Transmission torrents with a seeding ratio above a given threshold.
Uses the Transmission RPC API (no web scraping needed).

Usage:
    python transmission_high_ratio.py                  # ratio > 2.0 (default)
    python transmission_high_ratio.py --ratio 1.5      # ratio > 1.5
    python transmission_high_ratio.py --host 192.168.1.10 --port 9091
    python transmission_high_ratio.py --user admin --password secret
    python transmission_high_ratio.py --pause           # pause seeding torrents with ratio > 2.0
    python transmission_high_ratio.py --pause --yes     # pause without confirmation prompt

    Gio example: 
    python3 transmission_high_ratio.py --user transmission --password thepassword --pause
"""

import argparse
import json
import sys
import urllib.request
import urllib.error


RPC_URL_TEMPLATE = "http://{host}:{port}/transmission/rpc"

TORRENT_FIELDS = [
    "id",
    "name",
    "uploadRatio",
    "status",
    "totalSize",
    "uploadedEver",
    "downloadedEver",
    "percentDone",
    "rateUpload",
    "rateDownload",
]

STATUS_MAP = {
    0: "Stopped",
    1: "Check queued",
    2: "Checking",
    3: "Download queued",
    4: "Downloading",
    5: "Seed queued",
    6: "Seeding",
}

SEEDING_STATUS = 6


def format_bytes(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


class TransmissionClient:
    def __init__(self, host: str, port: int, user: str = "", password: str = ""):
        self.url = RPC_URL_TEMPLATE.format(host=host, port=port)
        self.session_id = ""
        self.user = user
        self.password = password

    def _build_request(self, method: str, arguments: dict) -> urllib.request.Request:
        payload = json.dumps({"method": method, "arguments": arguments}).encode()
        req = urllib.request.Request(self.url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("X-Transmission-Session-Id", self.session_id)
        if self.user:
            import base64
            creds = base64.b64encode(f"{self.user}:{self.password}".encode()).decode()
            req.add_header("Authorization", f"Basic {creds}")
        return req

    def _call(self, method: str, arguments: dict) -> dict:
        req = self._build_request(method, arguments)
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            # Transmission returns 409 with a new session ID on first request
            if e.code == 409:
                self.session_id = e.headers.get("X-Transmission-Session-Id", "")
                req = self._build_request(method, arguments)
                with urllib.request.urlopen(req) as resp:
                    return json.loads(resp.read())
            raise

    def get_torrents(self) -> list[dict]:
        result = self._call("torrent-get", {"fields": TORRENT_FIELDS})
        if result.get("result") != "success":
            raise RuntimeError(f"RPC error: {result.get('result')}")
        return result["arguments"]["torrents"]

    def pause_torrents(self, ids: list[int]) -> None:
        result = self._call("torrent-stop", {"ids": ids})
        if result.get("result") != "success":
            raise RuntimeError(f"RPC error while pausing: {result.get('result')}")


def main():
    parser = argparse.ArgumentParser(description="List Transmission torrents with ratio above threshold.")
    parser.add_argument("--host", default="localhost", help="Transmission host (default: localhost)")
    parser.add_argument("--port", type=int, default=9091, help="Transmission port (default: 9091)")
    parser.add_argument("--user", default="", help="RPC username (if authentication is enabled)")
    parser.add_argument("--password", default="", help="RPC password (if authentication is enabled)")
    parser.add_argument("--ratio", type=float, default=2.0, help="Minimum ratio threshold (default: 2.0)")
    parser.add_argument("--sort", choices=["ratio", "name", "size"], default="ratio",
                        help="Sort results by field (default: ratio)")
    parser.add_argument("--pause", action="store_true",
                        help="Pause torrents that are actively Seeding and meet the ratio threshold")
    parser.add_argument("--yes", action="store_true",
                        help="Skip confirmation prompt when used with --pause")
    args = parser.parse_args()

    client = TransmissionClient(args.host, args.port, args.user, args.password)

    print(f"Connecting to Transmission at {client.url} ...")
    try:
        torrents = client.get_torrents()
    except urllib.error.URLError as e:
        print(f"\n❌  Could not connect: {e.reason}")
        print("   Make sure Transmission is running and the RPC interface is enabled.")
        sys.exit(1)

    # Filter by ratio threshold (-1 means incomplete/no data)
    high_ratio = [t for t in torrents if t["uploadRatio"] >= args.ratio]

    if not high_ratio:
        print(f"\nNo torrents found with ratio ≥ {args.ratio}")
        return

    # Sort
    sort_key = {
        "ratio": lambda t: t["uploadRatio"],
        "name":  lambda t: t["name"].lower(),
        "size":  lambda t: t["totalSize"],
    }[args.sort]
    high_ratio.sort(key=sort_key, reverse=(args.sort != "name"))

    # Display
    print(f"\n{'='*80}")
    print(f"  Torrents with ratio ≥ {args.ratio}  ({len(high_ratio)} of {len(torrents)} total)")
    print(f"{'='*80}\n")

    col_w = 50
    print(f"{'Name':<{col_w}} {'Ratio':>7}  {'Size':>10}  {'Uploaded':>10}  Status")
    print(f"{'-'*col_w} {'-'*7}  {'-'*10}  {'-'*10}  {'-'*12}")

    for t in high_ratio:
        name     = t["name"][:col_w - 1] if len(t["name"]) >= col_w else t["name"]
        ratio    = f"{t['uploadRatio']:.2f}"
        size     = format_bytes(t["totalSize"])
        uploaded = format_bytes(t["uploadedEver"])
        status   = STATUS_MAP.get(t["status"], "Unknown")
        print(f"{name:<{col_w}} {ratio:>7}  {size:>10}  {uploaded:>10}  {status}")

    total_uploaded = sum(t["uploadedEver"] for t in high_ratio)
    print(f"\n  Total uploaded by these torrents: {format_bytes(total_uploaded)}")

    # --- Pause logic ---
    if args.pause:
        to_pause = [t for t in high_ratio if t["status"] == SEEDING_STATUS]

        if not to_pause:
            print(f"\n⏸  No actively seeding torrents found with ratio ≥ {args.ratio}. Nothing to pause.")
            return

        print(f"\n⏸  {len(to_pause)} torrent(s) will be paused:")
        for t in to_pause:
            print(f"     • {t['name'][:70]}  (ratio {t['uploadRatio']:.2f})")

        if not args.yes:
            try:
                answer = input("\nProceed? [y/N] ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nAborted.")
                return
            if answer not in ("y", "yes"):
                print("Aborted.")
                return

        ids = [t["id"] for t in to_pause]
        try:
            client.pause_torrents(ids)
            print(f"\n✅  Successfully paused {len(ids)} torrent(s).")
        except Exception as e:
            print(f"\n❌  Failed to pause torrents: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
