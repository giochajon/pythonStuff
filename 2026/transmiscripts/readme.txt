pip install transmission-rpc

export TRANSMIUSER="your_username"
export TRANSMIPASS="your_secret_password"
python3 pause_by_ratio.py

--- Docker ---

Build the image:
  docker build -t transmiscripts .

Run the container:
  docker run -p 8073:8073 \
    -e TRANSMIUSER="your_username" \
    -e TRANSMIPASS="your_secret_password" \
    transmiscripts

The web UI will be available at http://localhost:8073