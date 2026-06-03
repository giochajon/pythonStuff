import base64
import json
import os
import urllib.request
import urllib.error

RPC_URL_TEMPLATE = "http://{host}:{port}/transmission/rpc"

STATUS_MAP = {
    0: "Stopped",
    1: "Check queued",
    2: "Checking",
    3: "Download queued",
    4: "Downloading",
    5: "Seed queued",
    6: "Seeding",
}


def env_credentials() -> tuple:
    """Return (user, password) from TRANSMIUSER / TRANSMIPASS env vars."""
    return os.environ.get("TRANSMIUSER", ""), os.environ.get("TRANSMIPASS", "")


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

    def get_torrents(self, fields: list) -> list:
        result = self._call("torrent-get", {"fields": fields})
        if result.get("result") != "success":
            raise RuntimeError(f"RPC error: {result.get('result')}")
        return result["arguments"]["torrents"]

    def pause_torrents(self, ids: list) -> None:
        result = self._call("torrent-stop", {"ids": ids})
        if result.get("result") != "success":
            raise RuntimeError(f"RPC error while pausing: {result.get('result')}")
