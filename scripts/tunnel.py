"""
Pinggy Tunnel Runner for Kizuna-Vault / VeriLedger Streamlit Web App (Port 8501).
Starts and maintains a public tunnel link via Pinggy.
"""

import time
import sys
import pinggy

def main():
    print("Initializing Pinggy tunnel for port 8501...", flush=True)
    tunnel = pinggy.start_tunnel(forwardto=8501)

    urls = []
    for _ in range(20):
        time.sleep(0.5)
        if hasattr(tunnel, "urls") and tunnel.urls:
            urls = tunnel.urls
            break

    if not urls:
        print("ERROR: Could not fetch URLs from Pinggy tunnel.", flush=True)
        sys.exit(1)

    with open("tunnel_url.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(urls) + "\n")

    print("\n" + "=" * 60, flush=True)
    print("PINGGY PUBLIC TUNNEL ONLINE!", flush=True)
    for url in urls:
        print(f"URL: {url}", flush=True)
    print("=" * 60 + "\n", flush=True)

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("\nStopping tunnel...", flush=True)
        tunnel.stop()

if __name__ == "__main__":
    main()
