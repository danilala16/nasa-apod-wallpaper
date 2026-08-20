import requests
import os
import shutil
import ctypes
from datetime import datetime

log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apod_log.txt")

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def set_wallpaper(image_path):
    # SPI_SETDESKWALLPAPER = 20 tells Windows "the action we want is: set desktop wallpaper"
    # The final 3 = SPIF_UPDATEINIFILE (1) + SPIF_SENDCHANGE (2), which saves the setting
    # permanently and tells all open windows to redraw with the new wallpaper immediately.
    SPI_SETDESKWALLPAPER = 20
    result = ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)
    if result:
        log(f"Wallpaper set successfully to {image_path}")
    else:
        log("Wallpaper API call failed (SystemParametersInfoW returned 0)")

log("---- Script started ----")

api_key = os.environ.get("NASA_API_KEY", "YOUR_KEY_HERE")
log(f"API key found: {'yes' if api_key != 'YOUR_KEY_HERE' else 'NO - using placeholder!'}")

response = requests.get("https://api.nasa.gov/planetary/apod", params={"api_key": api_key})
log(f"NASA API status code: {response.status_code}")

if response.status_code != 200:
    log(f"NASA API request failed: {response.status_code} - {response.text[:200]}")
    raise SystemExit(1)

data = response.json()
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, "space_background.jpg")
fallback_path = os.path.join(script_dir, "fallback_image.jpg")

if data.get("media_type") == "image":
    image_url = data["url"]
    log("Found today's space image!")
    log(f"Attempting to download from: {image_url}")

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    image_response = requests.get(image_url, headers=headers)
    log(f"Image download status code: {image_response.status_code}")

    if image_response.status_code == 200:
        with open(output_path, "wb") as file:
            file.write(image_response.content)
        log(f"Download complete! Saved to {output_path}")
    else:
        log(f"Download failed ({image_response.status_code}), using local fallback instead.")
        shutil.copy(fallback_path, output_path)
        log(f"Copied fallback to {output_path}")

else:
    log("Today is a video — using local fallback nebula image instead.")
    shutil.copy(fallback_path, output_path)
    log(f"Copied fallback to {output_path}")

set_wallpaper(output_path)

log("---- Script finished ----")