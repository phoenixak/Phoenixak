"""Renders tools/banner.html into profile/banner.webp (the phoenix blooming out of an ink drop).

Usage (from D:\\Projects, so the portfolio art is reachable at /My protfolo/assets/art):
    python -m http.server 8002 --bind 127.0.0.1
    python Phoenixak/tools/render_banner.py

Each of the 37 bloom frames is a headless-Chrome screenshot of banner.html?f=N.
The WebP plays once and rests on the finished banner.
"""
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "profile"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
URL = "http://127.0.0.1:8002/Phoenixak/tools/banner.html?f={}"
FRAMES = 37
W, H = 1280, 440


def shot(i, tmp):
    path = Path(tmp) / f"{i:03d}.png"
    subprocess.run([
        CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", "--default-background-color=00000000",
        "--virtual-time-budget=5000", f"--user-data-dir={tmp}/profile-{i}",
        f"--screenshot={path}", f"--window-size={W},{H}", URL.format(i),
    ], check=True, capture_output=True)
    return Image.open(path).convert("RGBA")


def main():
    OUT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        with ThreadPoolExecutor(6) as pool:
            frames = list(pool.map(lambda i: shot(i, tmp), range(FRAMES)))
    # ink drop lingers a beat, the bloom runs at ~14 fps, the finished banner holds
    durations = [500] + [70] * (FRAMES - 2) + [60000]
    frames[0].save(OUT / "banner.webp", save_all=True, append_images=frames[1:],
                   duration=durations, loop=1, quality=82, method=6)
    for f in ("banner.webp",):
        print(f, round((OUT / f).stat().st_size / 1024), "KB")


if __name__ == "__main__":
    main()
