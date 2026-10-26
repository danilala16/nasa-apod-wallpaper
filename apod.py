import requests
import os
import shutil
import ctypes
import time
import glob
from datetime import datetime
from urllib.parse import urlparse

# ---------- Settings ----------
# NASA retired the old api.nasa.gov APOD endpoint. This one needs no API key.
APOD_URL = "https://science.nasa.gov/wp-json/wp/v2/apod-basic"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")
MIN_IMAGE_BYTES = 50_000  # a real wallpaper photo is bigger than this; a logo or error page is not

script_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(script_dir, "apod_log.txt")
output_path = os.path.join(script_dir, "space_background.jpg")
fallback_path = os.path.join(script_dir, "fallback_image.jpg")


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


def get_with_retries(url, params=None, timeout=20, attempts=4, wait=15):
    """Try a request several times. Returns the response, or None if every attempt failed.

    At logon the network is often not ready yet, so waiting and retrying is more
    reliable than failing on the first try. The timeout stops a stalled connection
    from hanging the script forever.
    """
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
            log(f"Attempt {attempt}/{attempts}: {url[:80]} returned {response.status_code}")
            if response.status_code == 200:
                return response
        except requests.exceptions.RequestException as error:
            log(f"Attempt {attempt}/{attempts}: request error: {type(error).__name__}")
        if attempt < attempts:
            time.sleep(wait)
    return None


def use_fallback(reason):
    log(f"Using local fallback because: {reason}")
    if os.path.exists(fallback_path):
        shutil.copy(fallback_path, output_path)
        log(f"Copied fallback to {output_path}")
        set_wallpaper(output_path)
    else:
        log("Fallback image not found, wallpaper left unchanged.")


def main():
    log("---- Script started ----")

    # 1. Ask NASA for today's picture (the answer comes back as a list with one item)
    response = get_with_retries(APOD_URL, params={"per_page": 1})
    if response is None:
        use_fallback("could not reach the NASA APOD endpoint")
        return

    try:
        data = response.json()
        entry = data[0] if data else {}
    except ValueError:
        use_fallback("NASA response was not valid JSON")
        return

    # 2. Make sure today's entry is an image, not a video
    if entry.get("media_type") != "image":
        use_fallback(f"today's media type is {entry.get('media_type')!r}, not an image")
        return

    # 3. 'hdurl' is the real image. 'url' is now the article web page, so we do not use it.
    image_url = entry.get("hdurl")
    log(f"Found today's space image: {entry.get('title')}")
    log(f"Attempting to download from: {image_url}")

    # Check only the path part of the URL, because the query string (?w=4222...) hides the extension
    path = urlparse(image_url or "").path.lower()
    if not path.endswith(IMAGE_EXTENSIONS) or "logo" in path:
        use_fallback(f"image URL does not look like a photo: {image_url}")
        return

    # 4. Download the image and check that we really received an image
    image_response = get_with_retries(image_url, timeout=60)
    if image_response is None:
        use_fallback("image download failed")
        return

    content_type = image_response.headers.get("Content-Type", "")
    size = len(image_response.content)
    if not content_type.startswith("image/") or size < MIN_IMAGE_BYTES:
        use_fallback(f"download is not a real photo (type={content_type}, bytes={size})")
        return

    # 5. Save it with the correct extension and set it as the wallpaper
    extension = os.path.splitext(path)[1]  # ".jpg", ".jpeg" or ".png", taken from the URL
    saved_path = os.path.join(script_dir, "space_background" + extension)

    # Remove an older copy that has a different extension, so only one file is left
    for old_file in glob.glob(os.path.join(script_dir, "space_background.*")):
        if old_file != saved_path:
            os.remove(old_file)

    with open(saved_path, "wb") as file:
        file.write(image_response.content)
    log(f"Download complete! Saved {size} bytes to {saved_path}")
    set_wallpaper(saved_path)

    log("---- Script finished ----")


if __name__ == "__main__":
    main()