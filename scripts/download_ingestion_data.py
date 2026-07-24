import os
import requests
import urllib3
import time

# Disable annoying warnings about insecure SSL connections
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
output_dir = "data/raw/ncert_pdfs"
os.makedirs(output_dir, exist_ok=True)

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# List of Chapter file codes
chapters = ["iesc107"]

print(f"Starting textbook downloads into: {output_dir}")
for ch in chapters:
    url = "https://ncert.nic.in/textbook/pdf/" + ch + ".pdf"
    target_path = os.path.join(output_dir, ch + ".pdf")

    print(f"Downloading from: {url}")
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=130)
            if response.status_code == 200:
                with open(target_path, "wb") as f:
                    f.write(response.content)
                    print(f"✅ Successfully saved: {target_path}")
                    break
            else:
                print(f"❌ Failed. Server responded with status code: {response.status_code}")
        except Exception as e:
            if attempt < 2:
                time.sleep(3)
            else:
                print(f"{ch}: attempt {attempt+1} failed,printing error")
                print(e)

