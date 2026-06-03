#!/usr/bin/env python3
"""
Pause Transmission torrents whose names match entries in a text blob (--glob).

Matching rules:
  - General     : 80% of the torrent name's tokens must appear in the glob text.
  - Season/Ep   : if the name contains SxxExx, that code must also appear verbatim.

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
import json
import os
import re
import sys
import urllib.request
import urllib.error


RPC_URL_TEMPLATE = "http://{host}:{port}/transmission/rpc"

TORRENT_FIELDS = ["id", "name", "status"]

STATUS_MAP = {
    0: "Stopped",
    1: "Check queued",
    2: "Checking",
    3: "Download queued",
    4: "Downloading",
    5: "Seed queued",
    6: "Seeding",
}

SXXEXX_RE = re.compile(r'S\d{2,}E\d{2,}', re.IGNORECASE)


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


def tokenize(name: str) -> list[str]:
    return [t.lower() for t in re.split(r'[\s._\-\[\]()+]+', name) if t]


def matches_glob(torrent_name: str, glob_text: str, threshold: float = 0.8) -> tuple[bool, float]:
    """
    Returns (matched, score) where score is the fraction of name tokens found in glob_text.

    If the torrent name contains SxxExx, that episode code must appear verbatim in
    glob_text — a mismatch causes an immediate (False, 0.0) regardless of token score.
    """
    glob_lower = glob_text.lower()

    ep_match = SXXEXX_RE.search(torrent_name)
    if ep_match:
        if ep_match.group(0).lower() not in glob_lower:
            return False, 0.0

    tokens = tokenize(torrent_name)
    if not tokens:
        return False, 0.0

    matched_count = sum(1 for t in tokens if t in glob_lower)
    score = matched_count / len(tokens)
    return score >= threshold, score


def load_glob(glob_arg: str) -> str:
    if os.path.isfile(glob_arg):
        with open(glob_arg, encoding="utf-8", errors="replace") as f:
            return f.read()
    return glob_arg


def main():
    parser = argparse.ArgumentParser(
        description="Pause Transmission torrents matched by name against a text blob.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--host", default="localhost", help="Transmission host (default: localhost)")
    parser.add_argument("--port", type=int, default=9091, help="Transmission port (default: 9091)")
    parser.add_argument("--user", default="", help="RPC username")
    parser.add_argument("--password", default="", help="RPC password")
    parser.add_argument("--glob", required=True,
                        help="Path to a text file OR raw text containing torrent names to match")
    parser.add_argument("--threshold", type=float, default=0.8,
                        help="Minimum token-match ratio, 0.0–1.0 (default: 0.8)")
    parser.add_argument("--pause", action="store_true",
                        help="Pause matched torrents (without this flag the run is dry-run only)")
    parser.add_argument("--yes", action="store_true",
                        help="Skip confirmation prompt when used with --pause")
    args = parser.parse_args()

    if not 0.0 < args.threshold <= 1.0:
        parser.error("--threshold must be between 0.0 (exclusive) and 1.0")

    glob_text = load_glob(args.glob)

    client = TransmissionClient(args.host, args.port, args.user, args.password)
    print(f"Connecting to Transmission at {client.url} ...")
    try:
        torrents = client.get_torrents()
    except urllib.error.URLError as e:
        print(f"\n  Could not connect: {e.reason}")
        print("  Make sure Transmission is running and the RPC interface is enabled.")
        sys.exit(1)

    matched = []
    for t in torrents:
        ok, score = matches_glob(t["name"], glob_text, args.threshold)
        if ok:
            matched.append((t, score))

    mode_label = "PAUSE" if args.pause else "DRY-RUN"
    print(f"\n{'='*70}")
    print(f"  Matched {len(matched)} of {len(torrents)} torrent(s) against glob")
    print(f"  Threshold: {args.threshold:.0%}  |  Mode: {mode_label}")
    print(f"{'='*70}\n")

    if not matched:
        print("No torrents matched. Nothing to do.")
        return

    col_w = 55
    print(f"{'Name':<{col_w}} {'Match':>6}  Status")
    print(f"{'-'*col_w} {'-'*6}  {'-'*14}")
    for t, score in matched:
        name = t["name"][:col_w - 1] if len(t["name"]) >= col_w else t["name"]
        status = STATUS_MAP.get(t["status"], "Unknown")
        ep_tag = "  [SxxExx]" if SXXEXX_RE.search(t["name"]) else ""
        print(f"{name:<{col_w}} {score:>5.0%}  {status}{ep_tag}")

    if not args.pause:
        print(f"\n[Dry-run] No changes made. Re-run with --pause to stop these torrents.")
        return

    to_pause = [t for t, _ in matched if t["status"] != 0]

    if not to_pause:
        print("\nAll matched torrents are already stopped. Nothing to pause.")
        return

    print(f"\n{len(to_pause)} torrent(s) will be paused.")

    if not args.yes:
        try:
            answer = input("Proceed? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            return
        if answer not in ("y", "yes"):
            print("Aborted.")
            return

    ids = [t["id"] for t in to_pause]
    try:
        client.pause_torrents(ids)
        print(f"\n  Successfully paused {len(ids)} torrent(s).")
    except Exception as e:
        print(f"\n  Failed to pause torrents: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
