import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

INITIAL_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
DEST_FILE = "cloudflared.exe"
NUM_WORKERS = 12

def get_final_info(url):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        final_url = resp.url
        content_length = int(resp.headers.get("Content-Length", 0))
        return final_url, content_length

def download_chunk(args):
    final_url, start, end, chunk_idx = args
    req = urllib.request.Request(
        final_url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Range": f"bytes={start}-{end}"
        }
    )
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
    return chunk_idx, start, data

def main():
    print(f"Resolving {INITIAL_URL}...", flush=True)
    final_url, total_size = get_final_info(INITIAL_URL)
    print(f"Total size: {total_size / (1024*1024):.2f} MB", flush=True)

    chunk_size = total_size // NUM_WORKERS
    tasks = []
    for i in range(NUM_WORKERS):
        start = i * chunk_size
        end = (start + chunk_size - 1) if i < NUM_WORKERS - 1 else total_size - 1
        tasks.append((final_url, start, end, i))

    print(f"Downloading with {NUM_WORKERS} parallel threads...", flush=True)
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        results = list(executor.map(download_chunk, tasks))

    results.sort(key=lambda x: x[0])

    print("Assembling binary...", flush=True)
    with open(DEST_FILE, "wb") as f:
        for idx, start, data in results:
            f.write(data)

    print(f"Successfully downloaded {DEST_FILE} ({os.path.getsize(DEST_FILE)} bytes)!", flush=True)

if __name__ == "__main__":
    main()
