#!/usr/bin/env python3
"""
Flask API wrapping transmission_high_ratio and pause_by_list.
Runs on 0.0.0.0:8073.
"""

import urllib.error

from flask import Flask, jsonify, render_template, request

import pause_by_list as pl
import transmission_high_ratio as hr
from transmission_client import env_credentials

app = Flask(__name__)


def _conn(data: dict) -> dict:
    env_user, env_pass = env_credentials()
    return {
        "host": data.get("host", "localhost"),
        "port": int(data.get("port", 9091)),
        "user": data.get("user") or env_user,
        "password": data.get("password") or env_pass,
    }


def _conn_error(exc) -> tuple:
    return jsonify({"success": False, "error": f"Cannot reach Transmission: {exc}"}), 502


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# Ratio endpoints
# ---------------------------------------------------------------------------

@app.route("/api/ratio/scan", methods=["POST"])
def ratio_scan():
    data = request.get_json(force=True)
    try:
        torrents = hr.scan_high_ratio(**_conn(data), ratio=float(data.get("ratio", 2.0)))
        total_up = sum(t["uploaded_ever"] for t in torrents)
        return jsonify({
            "success": True,
            "torrents": torrents,
            "count": len(torrents),
            "total_uploaded_str": hr.format_bytes(total_up),
        })
    except (urllib.error.URLError, OSError) as e:
        return _conn_error(e)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/ratio/pause", methods=["POST"])
def ratio_pause():
    data = request.get_json(force=True)
    try:
        result = hr.pause_high_ratio(**_conn(data), ratio=float(data.get("ratio", 2.0)))
        return jsonify({"success": True, **result})
    except (urllib.error.URLError, OSError) as e:
        return _conn_error(e)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------------------------------------------------------------------
# List / glob endpoints
# ---------------------------------------------------------------------------

@app.route("/api/list/scan", methods=["POST"])
def list_scan():
    data = request.get_json(force=True)
    glob_text = data.get("glob_text", "").strip()
    if not glob_text:
        return jsonify({"success": False, "error": "glob_text is required"}), 400
    try:
        torrents = pl.scan_by_glob(
            **_conn(data),
            glob_text=glob_text,
            threshold=float(data.get("threshold", 0.8)),
        )
        return jsonify({"success": True, "torrents": torrents, "count": len(torrents)})
    except (urllib.error.URLError, OSError) as e:
        return _conn_error(e)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/list/pause", methods=["POST"])
def list_pause():
    data = request.get_json(force=True)
    glob_text = data.get("glob_text", "").strip()
    if not glob_text:
        return jsonify({"success": False, "error": "glob_text is required"}), 400
    try:
        result = pl.pause_by_glob(
            **_conn(data),
            glob_text=glob_text,
            threshold=float(data.get("threshold", 0.8)),
        )
        return jsonify({"success": True, **result})
    except (urllib.error.URLError, OSError) as e:
        return _conn_error(e)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8073, debug=False)
