#!/usr/bin/env python3
"""
List or pause Transmission torrents with a seeding ratio above a given threshold.

Usage:
    python transmission_high_ratio.py
    python transmission_high_ratio.py --ratio 1.5
    python transmission_high_ratio.py --host 192.168.1.10 --port 9091
    python transmission_high_ratio.py --user admin --password secret --pause
    python transmission_high_ratio.py --pause --yes
"""

import argparse
import sys
import urllib.error

from transmission_client import TransmissionClient, STATUS_MAP, format_bytes, env_credentials

TORRENT_FIELDS = [
    "id", "name", "uploadRatio", "status",
    "totalSize", "uploadedEver",
]

SEEDING_STATUS = 6


# ---------------------------------------------------------------------------
# Importable API (used by Flask app)
# ---------------------------------------------------------------------------

def scan_high_ratio(
    host: str = "localhost",
    port: int = 9091,
    user: str = "",
    password: str = "",
    ratio: float = 2.0,
    sort: str = "ratio",
) -> list:
    """Return torrents with uploadRatio >= ratio, sorted as requested.

    Each item: {id, name, upload_ratio, total_size, total_size_str,
                uploaded_ever, uploaded_ever_str, status, status_str}
    """
    client = TransmissionClient(host, port, user, password)
    torrents = client.get_torrents(TORRENT_FIELDS)

    high = [t for t in torrents if t["uploadRatio"] >= ratio]

    sort_key = {
        "ratio": lambda t: t["uploadRatio"],
        "name":  lambda t: t["name"].lower(),
        "size":  lambda t: t["totalSize"],
    }.get(sort, lambda t: t["uploadRatio"])
    high.sort(key=sort_key, reverse=(sort != "name"))

    return [
        {
            "id": t["id"],
            "name": t["name"],
            "upload_ratio": round(t["uploadRatio"], 4),
            "total_size": t["totalSize"],
            "total_size_str": format_bytes(t["totalSize"]),
            "uploaded_ever": t["uploadedEver"],
            "uploaded_ever_str": format_bytes(t["uploadedEver"]),
            "status": t["status"],
            "status_str": STATUS_MAP.get(t["status"], "Unknown"),
        }
        for t in high
    ]


def pause_high_ratio(
    host: str = "localhost",
    port: int = 9091,
    user: str = "",
    password: str = "",
    ratio: float = 2.0,
) -> dict:
    """Pause all actively seeding torrents with uploadRatio >= ratio.

    Returns {paused, skipped, names}
    """
    client = TransmissionClient(host, port, user, password)
    torrents = client.get_torrents(TORRENT_FIELDS)

    candidates = [t for t in torrents if t["uploadRatio"] >= ratio]
    to_pause = [t for t in candidates if t["status"] == SEEDING_STATUS]
    skipped = len(candidates) - len(to_pause)

    if to_pause:
        client.pause_torrents([t["id"] for t in to_pause])

    return {
        "paused": len(to_pause),
        "skipped": skipped,
        "names": [t["name"] for t in to_pause],
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="List Transmission torrents with ratio above threshold.")
    env_user, env_pass = env_credentials()
    parser.add_argument("--host", default="localhost", help="Transmission host (default: localhost)")
    parser.add_argument("--port", type=int, default=9091, help="Transmission port (default: 9091)")
    parser.add_argument("--user", default=env_user, help="RPC username (default: $TRANSMIUSER)")
    parser.add_argument("--password", default=env_pass, help="RPC password (default: $TRANSMIPASS)")
    parser.add_argument("--ratio", type=float, default=2.0, help="Minimum ratio threshold (default: 2.0)")
    parser.add_argument("--sort", choices=["ratio", "name", "size"], default="ratio")
    parser.add_argument("--pause", action="store_true", help="Pause seeding torrents that meet the ratio threshold")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    print(f"Connecting to Transmission at http://{args.host}:{args.port} ...")
    try:
        torrents = scan_high_ratio(args.host, args.port, args.user, args.password, args.ratio, args.sort)
    except urllib.error.URLError as e:
        print(f"\n  Could not connect: {e.reason}")
        print("  Make sure Transmission is running and the RPC interface is enabled.")
        sys.exit(1)

    if not torrents:
        print(f"\nNo torrents found with ratio >= {args.ratio}")
        return

    print(f"\n{'='*80}")
    print(f"  Torrents with ratio >= {args.ratio}  ({len(torrents)} found)")
    print(f"{'='*80}\n")

    col_w = 50
    print(f"{'Name':<{col_w}} {'Ratio':>7}  {'Size':>10}  {'Uploaded':>10}  Status")
    print(f"{'-'*col_w} {'-'*7}  {'-'*10}  {'-'*10}  {'-'*12}")
    for t in torrents:
        name = t["name"][:col_w - 1] if len(t["name"]) >= col_w else t["name"]
        print(f"{name:<{col_w}} {t['upload_ratio']:>7.2f}  {t['total_size_str']:>10}  {t['uploaded_ever_str']:>10}  {t['status_str']}")

    total_up = sum(t["uploaded_ever"] for t in torrents)
    print(f"\n  Total uploaded by these torrents: {format_bytes(total_up)}")

    if not args.pause:
        return

    to_pause = [t for t in torrents if t["status"] == SEEDING_STATUS]
    if not to_pause:
        print(f"\n  No actively seeding torrents to pause.")
        return

    print(f"\n  {len(to_pause)} torrent(s) will be paused:")
    for t in to_pause:
        print(f"     - {t['name'][:70]}  (ratio {t['upload_ratio']:.2f})")

    if not args.yes:
        try:
            answer = input("\nProceed? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            return
        if answer not in ("y", "yes"):
            print("Aborted.")
            return

    try:
        result = pause_high_ratio(args.host, args.port, args.user, args.password, args.ratio)
        print(f"\n  Successfully paused {result['paused']} torrent(s).")
    except Exception as e:
        print(f"\n  Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
