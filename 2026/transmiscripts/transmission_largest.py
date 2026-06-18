#!/usr/bin/env python3
"""
List the top N largest torrents currently seeding, from largest to smallest.

Usage:
    python transmission_largest.py
    python transmission_largest.py --top 20
    python transmission_largest.py --host 192.168.1.10 --port 9091
    python transmission_largest.py --user admin --password secret
"""

import argparse
import sys
import urllib.error

from transmission_client import TransmissionClient, STATUS_MAP, format_bytes, env_credentials

TORRENT_FIELDS = [
    "id", "name", "totalSize", "uploadRatio", "uploadedEver", "status",
]

SEEDING_STATUS = 6


# ---------------------------------------------------------------------------
# Importable API (used by Flask app)
# ---------------------------------------------------------------------------

def scan_largest(
    host: str = "localhost",
    port: int = 9091,
    user: str = "",
    password: str = "",
    top: int = 10,
) -> list:
    """Return the top N largest seeding torrents, sorted largest to smallest.

    Each item: {id, name, total_size, total_size_str, upload_ratio,
                uploaded_ever, uploaded_ever_str, status, status_str}
    """
    client = TransmissionClient(host, port, user, password)
    torrents = client.get_torrents(TORRENT_FIELDS)

    seeding = [t for t in torrents if t["status"] == SEEDING_STATUS]
    seeding.sort(key=lambda t: t["totalSize"], reverse=True)

    return [
        {
            "id": t["id"],
            "name": t["name"],
            "total_size": t["totalSize"],
            "total_size_str": format_bytes(t["totalSize"]),
            "upload_ratio": round(t["uploadRatio"], 4),
            "uploaded_ever": t["uploadedEver"],
            "uploaded_ever_str": format_bytes(t["uploadedEver"]),
            "status": t["status"],
            "status_str": STATUS_MAP.get(t["status"], "Unknown"),
        }
        for t in seeding[:top]
    ]


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="List the largest seeding torrents in Transmission.")
    env_user, env_pass = env_credentials()
    parser.add_argument("--host", default="localhost", help="Transmission host (default: localhost)")
    parser.add_argument("--port", type=int, default=9091, help="Transmission port (default: 9091)")
    parser.add_argument("--user", default=env_user, help="RPC username (default: $TRANSMIUSER)")
    parser.add_argument("--password", default=env_pass, help="RPC password (default: $TRANSMIPASS)")
    parser.add_argument("--top", type=int, default=10, help="Number of torrents to show (default: 10)")
    args = parser.parse_args()

    print(f"Connecting to Transmission at http://{args.host}:{args.port} ...")
    try:
        torrents = scan_largest(args.host, args.port, args.user, args.password, args.top)
    except urllib.error.URLError as e:
        print(f"\n  Could not connect: {e.reason}")
        print("  Make sure Transmission is running and the RPC interface is enabled.")
        sys.exit(1)

    if not torrents:
        print("\nNo seeding torrents found.")
        return

    print(f"\n{'='*80}")
    print(f"  Top {args.top} largest seeding torrents  ({len(torrents)} shown)")
    print(f"{'='*80}\n")

    col_w = 50
    print(f"{'#':>3}  {'Name':<{col_w}} {'Size':>10}  {'Ratio':>7}  {'Uploaded':>10}")
    print(f"{'─'*3}  {'-'*col_w} {'-'*10}  {'-'*7}  {'-'*10}")
    for rank, t in enumerate(torrents, start=1):
        name = t["name"][:col_w - 1] if len(t["name"]) >= col_w else t["name"]
        print(f"{rank:>3}.  {name:<{col_w}} {t['total_size_str']:>10}  {t['upload_ratio']:>7.2f}  {t['uploaded_ever_str']:>10}")

    total = sum(t["total_size"] for t in torrents)
    print(f"\n  Total size of listed torrents: {format_bytes(total)}")


if __name__ == "__main__":
    main()
