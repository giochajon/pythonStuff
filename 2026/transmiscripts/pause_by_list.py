#!/usr/bin/env python3
"""
Pause Transmission torrents whose names match entries in a text blob (--glob).

Matching rules:
  - General  : 80% of the torrent name's tokens must appear in the glob text.
  - Season/Ep: if the name contains SxxExx, that code must also appear verbatim.

Default run shows matches only (dry-run). Use --pause to actually stop torrents.

Usage:
    python pause_by_list.py --glob targets.txt
    python pause_by_list.py --glob "long text blob with names inside..."
    python pause_by_list.py --glob targets.txt --pause
    python pause_by_list.py --glob targets.txt --pause --yes
    python pause_by_list.py --glob targets.txt --threshold 0.7
    python pause_by_list.py --host 192.168.1.10 --user admin --password secret --glob targets.txt
"""

import argparse
import os
import re
import sys
import urllib.error

from transmission_client import TransmissionClient, STATUS_MAP, env_credentials

TORRENT_FIELDS = ["id", "name", "status"]

SXXEXX_RE = re.compile(r'S\d{2,}E\d{2,}', re.IGNORECASE)


# ---------------------------------------------------------------------------
# Matching helpers
# ---------------------------------------------------------------------------

def _tokenize(name: str) -> list:
    return [t.lower() for t in re.split(r'[\s._\-\[\]()+]+', name) if t]


def _matches_glob(torrent_name: str, glob_text: str, threshold: float = 0.8) -> tuple:
    """Return (matched: bool, score: float).

    If the name contains SxxExx the episode code must appear verbatim in
    glob_text — a mismatch returns (False, 0.0) before checking token score.
    """
    glob_lower = glob_text.lower()

    ep_match = SXXEXX_RE.search(torrent_name)
    if ep_match and ep_match.group(0).lower() not in glob_lower:
        return False, 0.0

    tokens = _tokenize(torrent_name)
    if not tokens:
        return False, 0.0

    score = sum(1 for t in tokens if t in glob_lower) / len(tokens)
    return score >= threshold, score


def _load_glob(glob_arg: str) -> str:
    if os.path.isfile(glob_arg):
        with open(glob_arg, encoding="utf-8", errors="replace") as f:
            return f.read()
    return glob_arg


# ---------------------------------------------------------------------------
# Importable API (used by Flask app)
# ---------------------------------------------------------------------------

def scan_by_glob(
    host: str = "localhost",
    port: int = 9091,
    user: str = "",
    password: str = "",
    glob_text: str = "",
    threshold: float = 0.8,
) -> list:
    """Return torrents whose names match glob_text at the given threshold.

    Each item: {id, name, score, has_episode, episode_code, status, status_str}
    """
    client = TransmissionClient(host, port, user, password)
    torrents = client.get_torrents(TORRENT_FIELDS)

    results = []
    for t in torrents:
        ok, score = _matches_glob(t["name"], glob_text, threshold)
        if ok:
            ep = SXXEXX_RE.search(t["name"])
            results.append({
                "id": t["id"],
                "name": t["name"],
                "score": round(score, 4),
                "has_episode": ep is not None,
                "episode_code": ep.group(0).upper() if ep else None,
                "status": t["status"],
                "status_str": STATUS_MAP.get(t["status"], "Unknown"),
            })

    return results


def pause_by_glob(
    host: str = "localhost",
    port: int = 9091,
    user: str = "",
    password: str = "",
    glob_text: str = "",
    threshold: float = 0.8,
) -> dict:
    """Pause all non-stopped torrents whose names match glob_text.

    Returns {paused, skipped, names}
    """
    client = TransmissionClient(host, port, user, password)
    torrents = client.get_torrents(TORRENT_FIELDS)

    matched = [t for t in torrents if _matches_glob(t["name"], glob_text, threshold)[0]]
    to_pause = [t for t in matched if t["status"] != 0]
    skipped = len(matched) - len(to_pause)

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
    parser = argparse.ArgumentParser(
        description="Pause Transmission torrents matched by name against a text blob.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    env_user, env_pass = env_credentials()
    parser.add_argument("--host", default="localhost", help="Transmission host (default: localhost)")
    parser.add_argument("--port", type=int, default=9091, help="Transmission port (default: 9091)")
    parser.add_argument("--user", default=env_user, help="RPC username (default: $TRANSMIUSER)")
    parser.add_argument("--password", default=env_pass, help="RPC password (default: $TRANSMIPASS)")
    parser.add_argument("--glob", required=True,
                        help="Path to a text file OR raw text containing torrent names to match")
    parser.add_argument("--threshold", type=float, default=0.8,
                        help="Minimum token-match ratio 0–1 (default: 0.8)")
    parser.add_argument("--pause", action="store_true",
                        help="Pause matched torrents (without this flag the run is dry-run only)")
    parser.add_argument("--yes", action="store_true",
                        help="Skip confirmation prompt")
    args = parser.parse_args()

    if not 0.0 < args.threshold <= 1.0:
        parser.error("--threshold must be between 0.0 (exclusive) and 1.0")

    glob_text = _load_glob(args.glob)
    mode_label = "PAUSE" if args.pause else "DRY-RUN"

    print(f"Connecting to Transmission at http://{args.host}:{args.port} ...")
    try:
        matched = scan_by_glob(args.host, args.port, args.user, args.password, glob_text, args.threshold)
    except urllib.error.URLError as e:
        print(f"\n  Could not connect: {e.reason}")
        sys.exit(1)

    print(f"\n{'='*70}")
    print(f"  Matched {len(matched)} torrent(s)  |  Threshold: {args.threshold:.0%}  |  Mode: {mode_label}")
    print(f"{'='*70}\n")

    if not matched:
        print("No torrents matched. Nothing to do.")
        return

    col_w = 55
    print(f"{'Name':<{col_w}} {'Match':>6}  Status")
    print(f"{'-'*col_w} {'-'*6}  {'-'*14}")
    for t in matched:
        name = t["name"][:col_w - 1] if len(t["name"]) >= col_w else t["name"]
        ep_tag = f"  [{t['episode_code']}]" if t["has_episode"] else ""
        print(f"{name:<{col_w}} {t['score']:>5.0%}  {t['status_str']}{ep_tag}")

    if not args.pause:
        print(f"\n[Dry-run] No changes made. Re-run with --pause to stop these torrents.")
        return

    to_pause = [t for t in matched if t["status"] != 0]
    if not to_pause:
        print("\nAll matched torrents are already stopped. Nothing to pause.")
        return

    print(f"\n  {len(to_pause)} torrent(s) will be paused.")
    if not args.yes:
        try:
            answer = input("Proceed? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            return
        if answer not in ("y", "yes"):
            print("Aborted.")
            return

    try:
        result = pause_by_glob(args.host, args.port, args.user, args.password, glob_text, args.threshold)
        print(f"\n  Successfully paused {result['paused']} torrent(s).")
    except Exception as e:
        print(f"\n  Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
