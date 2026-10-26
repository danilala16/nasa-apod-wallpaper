# NASA Astronomy Picture of the Day: Desktop Wallpaper

A Python script that fetches NASA's [Astronomy Picture of the Day](https://science.nasa.gov/apod/) and automatically sets it as your Windows desktop wallpaper. Runs daily and unattended via Task Scheduler.

If today's APOD is a video (not an image), or the download fails for any reason, the script falls back to a local backup image instead of leaving your wallpaper unchanged or crashing.

## Features

- Fetches the current APOD from NASA's `science.nasa.gov` endpoint (no API key needed)
- Sets the image as your Windows desktop wallpaper automatically
- Timeouts and automatic retries, so a slow network at logon or a temporary NASA outage does not hang the script
- Validates the download before using it: the URL must look like a photo, the response must be an image type, and the file must be a reasonable size
- Falls back to a local image on video days, failed requests, or bad downloads (no dependency on a second network call that could also fail)
- Logs every run to `apod_log.txt` for easy debugging
- Designed to run hands-off via Task Scheduler (daily trigger plus a delayed logon trigger)

## Requirements

- Windows (uses `ctypes` to call the Windows API for setting wallpaper)
- Python 3.x
- [`requests`](https://pypi.org/project/requests/) library

## Setup

1. **Clone this repo** and install dependencies:
   ```
   pip install requests
   ```

2. **Add a local fallback image.** Save any space/nebula image into the project folder and name it `fallback_image.jpg`. This is used whenever today's APOD is a video or the download otherwise fails.

No API key is required. The script uses NASA's newer APOD endpoint, which has no key or quota.

## Usage

Run manually:
```
python apod.py
```

Check `apod_log.txt` afterward to confirm what happened on that run (request status, whether the fallback was used and why, whether the wallpaper was set successfully).

## Automating with Task Scheduler

To run this without opening it yourself:

1. Open **Task Scheduler** and choose **Create Basic Task**. Set the trigger to **Daily**, at a time your PC is usually on.
2. Action: **Start a program**
   - **Program/script**: the full path to your `python.exe`, *in quotes* if the path contains spaces (e.g. `"C:\Users\Your Name\AppData\Local\Programs\Python\Python313\python.exe"`)
   - **Add arguments**: the full path to the script, in quotes if it contains spaces (e.g. `"C:\Users\Your Name\Desktop\nasa-apod\apod.py"`)
   - **Start in**: the full path to this project's folder
3. Save, then double-click the task in the Task Scheduler Library to open its properties and make two more changes:
   - **Triggers** tab: click **New...** and add an **At log on** trigger. Tick **Delay task for** and choose 1 or 2 minutes, so the network is ready when the script runs. This covers days when the PC was off at the daily time.
   - **Settings** tab: tick **Run task as soon as possible after a scheduled start is missed**.
4. Right-click the task and choose **Run** to test it immediately.

A logon trigger on its own only fires when you actually sign in, so a PC that sleeps for days will not run the task. Keeping the Daily trigger avoids that.

## Troubleshooting

**The wallpaper is a NASA logo, or the wrong image.**
Earlier versions read the `url` field from NASA's old API and trusted any response with status 200. After NASA changed its endpoints, that field no longer pointed at the photo and the script downloaded a site logo. The current version reads the image from `hdurl` and checks that the download is a real photo. If you see "using local fallback because" in `apod_log.txt`, the reason is on that line.

**The script hangs or takes a very long time.**
Requests without a timeout can wait forever when a server is struggling. This script sets timeouts and retries, and logs each attempt. If every attempt fails, it uses the fallback image.

**The old `api.nasa.gov/planetary/apod` endpoint returns a 500 error.**
That endpoint began failing in late September 2026 and is reportedly being retired. This project now uses `https://science.nasa.gov/wp-json/wp/v2/apod-basic`, so the old API key and the `NASA_API_KEY` environment variable are no longer needed.

**Task shows "Ready" after running, but nothing changed.**
"Ready" is the normal idle status both before and after a run. It does not tell you whether the script actually succeeded. Check `apod_log.txt` instead, or enable more detail via Task Scheduler's **Action menu > Enable All Tasks History**, then check the task's **History** tab.

**Task Scheduler error `0x8007000B` ("not a valid Win32 application").**
The **Program/script** field needs quotes around the path if it contains spaces (e.g. a username with a space in it). Note this is different from the **Start in** field, which does not need quotes.

**Script runs manually but silently fails under Task Scheduler.**
If you have more than one Python installation on your machine (e.g. a Microsoft Store version and a standalone installer version from python.org), they do **not** share installed packages. Find out which interpreter Task Scheduler is actually pointing at, and install `requests` into that specific one:
```
"C:\full\path\to\that\python.exe" -m pip install requests
```
Run `py -0p` in a terminal to list all installed Python versions and their full paths.

**Wallpaper doesn't visibly change.**
Check `apod_log.txt` for a "Wallpaper set successfully" line to confirm the script finished. If today's image is identical to yesterday's fallback, there may simply be no visible difference to notice.

## Notes

Several similar NASA APOD wallpaper scripts exist in the open-source community. This one was built as a learning project to practice API requests, error handling, retries and timeouts, file I/O, Windows automation via `ctypes`, and task scheduling. It was later updated after NASA's APOD API changed, which was a good lesson in diagnosing a real outage from log files.
