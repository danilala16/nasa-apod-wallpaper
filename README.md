# NASA Astronomy Picture of the Day — Desktop Wallpaper

A Python script that fetches NASA's [Astronomy Picture of the Day](https://apod.nasa.gov/apod/astropix.html) and automatically sets it as your Windows desktop wallpaper. Runs daily and unattended via Task Scheduler.

If today's APOD is a video (not an image), or the download fails for any reason, the script falls back to a local backup image instead of leaving your wallpaper unchanged or crashing.

## Features

- Fetches the current APOD via NASA's public API
- Sets the image as your Windows desktop wallpaper automatically
- Falls back to a local image on video days or failed downloads (no dependency on a second network call that could also fail)
- Logs every run to `apod_log.txt` for easy debugging
- Designed to run hands-off, once a day, via Task Scheduler

## Requirements

- Windows (uses `ctypes` to call the Windows API for setting wallpaper)
- Python 3.x
- [`requests`](https://pypi.org/project/requests/) library

## Setup

1. **Get a free NASA API key** at [api.nasa.gov](https://api.nasa.gov/) (just requires an email, no billing).

2. **Clone this repo** and install dependencies:
   ```
   pip install requests
   ```

3. **Set your API key as an environment variable** named `NASA_API_KEY`:
   - Windows: Start → search "env" → *Edit environment variables for your account* → New → Name: `NASA_API_KEY`, Value: your key
   - Restart any open terminal windows after setting it

4. **Add a local fallback image.** Save any space/nebula image into the project folder and name it `fallback_image.jpg`. This is used whenever today's APOD is a video or the download otherwise fails.

## Usage

Run manually:
```
python apod.py
```

Check `apod_log.txt` afterward to confirm what happened on that run (API status, whether the fallback was used, whether the wallpaper was set successfully).

## Automating with Task Scheduler

To run this daily without opening it yourself:

1. Open **Task Scheduler** → **Create Basic Task**
2. Set the trigger to **Daily**, at whatever time you'd like
3. Action: **Start a program**
   - **Program/script**: the full path to your `python.exe`, *in quotes* if the path contains spaces (e.g. `"C:\Users\Your Name\AppData\Local\Programs\Python\Python313\python.exe"`)
   - **Add arguments**: `apod.py`
   - **Start in**: the full path to this project's folder
4. Save, then right-click the task → **Run** to test it immediately

## Troubleshooting

**Task shows "Ready" after running, but nothing changed.**
"Ready" is the normal idle status both before and after a run — it doesn't tell you whether the script actually succeeded. Check `apod_log.txt` instead, or enable more detail via Task Scheduler's **Action menu → Enable All Tasks History**, then check the task's **History** tab.

**Task Scheduler error `0x8007000B` ("not a valid Win32 application").**
The **Program/script** field needs quotes around the path if it contains spaces (e.g. a username with a space in it). Note this is different from the **Start in** field, which does not need quotes.

**Script runs manually but silently fails under Task Scheduler.**
If you have more than one Python installation on your machine (e.g. a Microsoft Store version and a standalone installer version from python.org), they do **not** share installed packages. Find out which interpreter Task Scheduler is actually pointing at, and install `requests` into that specific one:
```
"C:\full\path\to\that\python.exe" -m pip install requests
```
Run `py -0p` in a terminal to list all installed Python versions and their full paths.

**Wallpaper doesn't visibly change.**
Check `apod_log.txt` for a "Wallpaper set successfully" line to confirm the API call itself succeeded. If today's image is identical to yesterday's fallback, there may simply be no visible difference to notice.

## Notes

Several similar NASA APOD wallpaper scripts exist in the open-source community — this one was built as a learning project to practice API requests, error handling, file I/O, environment variables, Windows automation via `ctypes`, and task scheduling.
