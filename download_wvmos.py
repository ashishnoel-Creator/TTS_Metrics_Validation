import os
import requests
import sys

def download_file(url, filename):
    print(f"Downloading {url} to {filename}...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024 # 1 Kibibyte
    
    with open(filename, 'wb') as file:
        downloaded = 0
        for data in response.iter_content(block_size):
            file.write(data)
            downloaded += len(data)
            done = int(50 * downloaded / total_size) if total_size > 0 else 0
            sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {downloaded//1024//1024}MB / {total_size//1024//1024}MB")
            sys.stdout.flush()
    print("\nDownload complete!")

if __name__ == "__main__":
    url = "https://zenodo.org/record/6201162/files/wav2vec2.ckpt?download=1"
    os.makedirs("models", exist_ok=True)
    target_path = "models/wv_mos.ckpt"
    
    # Remove partial/corrupt file from failed curl
    if os.path.exists(target_path):
        os.remove(target_path)
        
    download_file(url, target_path)
