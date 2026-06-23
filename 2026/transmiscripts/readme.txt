transmiscripts
==============

Python CLI scripts and a Flask web UI for managing Transmission torrents over RPC.

Requirements
------------
  pip install flask

Credentials (optional)
----------------------
  export TRANSMIUSER="your_username"
  export TRANSMIPASS="your_secret_password"

Scripts
-------

transmission_high_ratio.py
  List or pause seeding torrents whose upload ratio exceeds a threshold.

  python transmission_high_ratio.py
  python transmission_high_ratio.py --ratio 1.5
  python transmission_high_ratio.py --pause
  python transmission_high_ratio.py --pause --yes

transmission_largest.py
  List the top N largest torrents currently seeding, from largest to smallest.

  python transmission_largest.py
  python transmission_largest.py --top 20

transmission_notfound.py
  Find files/folders in a download directory that are not tracked by any
  active torrent, ordered from oldest to newest.

  python transmission_notfound.py
  python transmission_notfound.py --path /mnt/media/complete
  python transmission_notfound.py --top 30

pause_by_list.py
  Pause torrents whose names fuzzy-match a pasted text blob or file.
  TV episodes require an exact SxxExx code match.

  python pause_by_list.py --glob targets.txt
  python pause_by_list.py --glob targets.txt --pause
  python pause_by_list.py --glob targets.txt --threshold 0.7

All scripts accept --host, --port, --user, and --password to override defaults.

Web UI / API
------------
  python app.py
  Open http://localhost:8073

  The UI exposes all four tools as interactive panels:
    - Pause by Ratio
    - Pause by List
    - Largest Seeding
    - Not in Transmission

  REST endpoints:
    POST /api/ratio/scan        { ratio }
    POST /api/ratio/pause       { ratio }
    POST /api/list/scan         { glob_text, threshold }
    POST /api/list/pause        { glob_text, threshold }
    POST /api/largest/scan      { top }
    POST /api/notfound/scan     { path, top }
    POST /api/notfound/delete   { path, name }

Docker
------
  Build and run with Docker Compose (recommended):
    docker compose up -d

  If host port 8073 is already in use:
    APP_PORT=8074 docker compose up -d

  The stack is named "transmiscripts"; containers appear as transmiscripts-app-1.
  TRANSMIUSER and TRANSMIPASS are forwarded from the host shell if set.

  The Not in Transmission panel needs the app container to see the same
  download files that Transmission reports over RPC. By default compose mounts:

    /home/giovas/dostb/transmi/complete

  into the same path inside the app container. Override these when your host
  path, app-container path, or Transmission-reported path differ:

    NOTFOUND_HOST_PATH=/host/downloads
    NOTFOUND_CONTAINER_PATH=/downloads
    NOTFOUND_TRANSMISSION_PATH=/downloads

  The web UI scans the Transmission path and maps it to NOTFOUND_CONTAINER_PATH
  before reading or deleting files.

  Or build and run manually:
    docker build -t transmiscripts .
    docker run -p 8073:8073 \
      -e TRANSMIUSER="your_username" \
      -e TRANSMIPASS="your_secret_password" \
      -e NOTFOUND_TRANSMISSION_PATH="/downloads" \
      -e NOTFOUND_LOCAL_PATH="/downloads" \
      -v /host/downloads:/downloads \
      transmiscripts

  The web UI will be available at http://localhost:8073
