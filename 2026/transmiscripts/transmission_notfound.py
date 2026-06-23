#!/usr/bin/env python3
"""
Find files/folders in a Transmission download directory that are not tracked
by any active torrent, ordered from oldest to newest (top 20 by default).

Usage:
    python transmission_notfound.py
    python transmission_notfound.py --path /mnt/media/complete
    python transmission_notfound.py --top 30
    python transmission_notfound.py --host 192.168.1.10 --port 9091
    python transmission_notfound.py --user admin --password secret
"""

import argparse
import os
import shutil
import sys
import urllib.error
from datetime import datetime

from transmission_client import TransmissionClient, format_bytes, env_credentials

DEFAULT_PATH = os.environ.get("NOTFOUND_TRANSMISSION_PATH", "/home/giovas/dostb/transmi/complete")
DEFAULT_LOCAL_PATH = os.environ.get("NOTFOUND_LOCAL_PATH", DEFAULT_PATH)

TORRENT_FIELDS = ["id", "name", "downloadDir", "totalSize", "status"]


# ---------------------------------------------------------------------------
# Importable API (used by Flask app)
# ---------------------------------------------------------------------------

def _is_within(path: str, base: str) -> bool:
    try:
        return os.path.commonpath([path, base]) == base
    except ValueError:
        return False


def resolve_scan_paths(path: str) -> tuple[str, str]:
    """Return (transmission_path, local_path) for a requested download path."""
    requested = os.path.normpath(path)
    transmission_base = os.path.normpath(DEFAULT_PATH)
    local_base = os.path.normpath(DEFAULT_LOCAL_PATH)

    if requested == local_base or _is_within(requested, local_base):
        rel = os.path.relpath(requested, local_base)
        transmission_path = transmission_base if rel == "." else os.path.normpath(os.path.join(transmission_base, rel))
        return transmission_path, requested

    if requested == transmission_base or _is_within(requested, transmission_base):
        rel = os.path.relpath(requested, transmission_base)
        local_path = local_base if rel == "." else os.path.normpath(os.path.join(local_base, rel))
        return requested, local_path

    return requested, requested


def _tracked_names(torrents: list, transmission_path: str) -> set:
    norm_path = os.path.normpath(transmission_path)
    return {
        t["name"]
        for t in torrents
        if os.path.normpath(t["downloadDir"]) == norm_path
    }


def scan_notfound(
    host: str = "localhost",
    port: int = 9091,
    user: str = "",
    password: str = "",
    path: str = DEFAULT_PATH,
    top: int = 20,
) -> list:
    """Return top N filesystem entries in *path* not tracked by any torrent.

    Entries are sorted oldest → newest by last-modified time.

    Each item: {name, full_path, size, size_str, modified, modified_str}
    """
    client = TransmissionClient(host, port, user, password)
    torrents = client.get_torrents(TORRENT_FIELDS)

    transmission_path, local_path = resolve_scan_paths(path)
    tracked = _tracked_names(torrents, transmission_path)

    if not os.path.isdir(local_path):
        if transmission_path != local_path:
            raise FileNotFoundError(f"Directory not found: {local_path} (mapped from {transmission_path})")
        raise FileNotFoundError(f"Directory not found: {local_path}")

    orphans = []
    for entry in os.scandir(local_path):
        if entry.name in tracked:
            continue
        stat = entry.stat(follow_symlinks=False)
        orphans.append({
            "name": entry.name,
            "full_path": entry.path,
            "size": stat.st_size,
            "size_str": format_bytes(stat.st_size),
            "modified": stat.st_mtime,
            "modified_str": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
        })

    orphans.sort(key=lambda e: e["modified"])
    return orphans[:top]


def delete_notfound_entry(
    host: str = "localhost",
    port: int = 9091,
    user: str = "",
    password: str = "",
    path: str = DEFAULT_PATH,
    name: str = "",
) -> dict:
    """Delete one untracked filesystem entry by name from *path*."""
    if not name or os.path.basename(name) != name:
        raise ValueError("name must be a single file or folder name")

    client = TransmissionClient(host, port, user, password)
    torrents = client.get_torrents(TORRENT_FIELDS)
    transmission_path, local_path = resolve_scan_paths(path)

    if name in _tracked_names(torrents, transmission_path):
        raise ValueError("Refusing to delete an entry that is tracked by Transmission")

    target = os.path.normpath(os.path.join(local_path, name))
    if not _is_within(target, os.path.normpath(local_path)):
        raise ValueError("Refusing to delete outside the scanned directory")
    if not os.path.lexists(target):
        raise FileNotFoundError(f"Entry not found: {target}")

    if os.path.isdir(target) and not os.path.islink(target):
        shutil.rmtree(target)
        kind = "directory"
    else:
        os.unlink(target)
        kind = "file"

    return {"name": name, "full_path": target, "kind": kind}


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="List files in a Transmission download path not tracked by any torrent."
    )
    env_user, env_pass = env_credentials()
    parser.add_argument("--host", default="localhost", help="Transmission host (default: localhost)")
    parser.add_argument("--port", type=int, default=9091, help="Transmission port (default: 9091)")
    parser.add_argument("--user", default=env_user, help="RPC username (default: $TRANSMIUSER)")
    parser.add_argument("--password", default=env_pass, help="RPC password (default: $TRANSMIPASS)")
    parser.add_argument("--path", default=DEFAULT_PATH, help=f"Download directory to scan (default: {DEFAULT_PATH})")
    parser.add_argument("--top", type=int, default=20, help="Number of entries to show (default: 20)")
    args = parser.parse_args()

    print(f"Connecting to Transmission at http://{args.host}:{args.port} ...")
    try:
        orphans = scan_notfound(args.host, args.port, args.user, args.password, args.path, args.top)
    except urllib.error.URLError as e:
        print(f"\n  Could not connect: {e.reason}")
        print("  Make sure Transmission is running and the RPC interface is enabled.")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\n  {e}")
        sys.exit(1)

    norm_path = os.path.normpath(args.path)

    if not orphans:
        print(f"\nAll entries in {norm_path} are tracked by Transmission.")
        return

    print(f"\n{'='*80}")
    print(f"  Untracked entries in {norm_path}  ({len(orphans)} shown, oldest first)")
    print(f"{'='*80}\n")

    col_w = 48
    print(f"{'#':>3}  {'Name':<{col_w}} {'Modified':<17}  {'Size':>10}")
    print(f"{'─'*3}  {'-'*col_w} {'-'*16}  {'-'*10}")
    for rank, e in enumerate(orphans, start=1):
        name = e["name"][:col_w - 1] if len(e["name"]) >= col_w else e["name"]
        print(f"{rank:>3}.  {name:<{col_w}} {e['modified_str']:<17}  {e['size_str']:>10}")

    total = sum(e["size"] for e in orphans)
    print(f"\n  Total size of listed entries: {format_bytes(total)}")


if __name__ == "__main__":
    main()
