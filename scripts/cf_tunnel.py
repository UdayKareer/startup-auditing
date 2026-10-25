"""
Cloudflare Quick Tunnel Runner for Kizuna-Vault / VeriLedger Streamlit Web App (Port 8501).
Starts and maintains a zero-warning public Cloudflare tunnel.
"""

import os
import re
import subprocess
import sys
import time

URL_REGEX = re.compile(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com")
CLOUDFLARED_BIN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cloudflared.exe")

def main():
    if not os.path.exists(CLOUDFLARED_BIN):
        print(f"Error: {CLOUDFLARED_BIN} not found", flush=True)
        sys.exit(1)

    print("Launching Cloudflare Quick Tunnel for http://localhost:8501...", flush=True)

    cmd = [
        CLOUDFLARED_BIN,
        "tunnel",
        "--url",
        "http://localhost:8501",
        "--no-autoupdate",
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    tunnel_url = None
    output_lines = []

    # Read output to capture tunnel URL
    for line in iter(proc.stdout.readline, ""):
        output_lines.append(line)
        print(line, end="", flush=True)
        match = URL_REGEX.search(line)
        if match:
            tunnel_url = match.group(0)
            with open("cloudflare_tunnel_url.txt", "w", encoding="utf-8") as f:
                f.write(tunnel_url + "\n")
            print("\n" + "=" * 60, flush=True)
            print("CLOUDFLARE PUBLIC TUNNEL LIVE (NO WARNING SCREENS)!", flush=True)
            print(f"URL: {tunnel_url}", flush=True)
            print("=" * 60 + "\n", flush=True)
            break

    if not tunnel_url:
        print("ERROR: Could not capture trycloudflare.com URL from output.", flush=True)
        sys.exit(1)

    # Keep process running
    try:
        proc.wait()
    except (KeyboardInterrupt, SystemExit):
        print("Stopping Cloudflare tunnel...", flush=True)
        proc.terminate()

if __name__ == "__main__":
    main()
