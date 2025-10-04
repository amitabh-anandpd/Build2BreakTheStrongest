# animator.py
# Creates short animated clips from static images using ffmpeg Ken Burns (zoom & pan)
# Output: per-scene mp4 clips in clips_out/

import os
import subprocess
from pathlib import Path

CLIPS_DIR = Path("clips_out")
CLIPS_DIR.mkdir(exist_ok=True)

# def ken_burns_clip(image_path, out_path, duration=8, resolution=(1080,1920)):
#     """
#     Uses ffmpeg to create a simple zoom-in/out + gentle pan.
#     out_path: mp4 output (should end with .mp4)
#     """
#     w,h = resolution
#     # scale image to fill height and keep aspect ratio, pad if needed
#     # create a filtergraph with zoompan simplifies: use zoompan or use scale and crop with expressions
#     # We'll use a simple zoom via 'zoompan' is for images to create many frames, but it's cumbersome;
#     # instead, use ffmpeg's zoom/pan via 'scale' + 'crop' with 'zoom' variable.
#     # For simplicity, we implement a slow zoom centered.
#     zoom_start = 1.0
#     zoom_end = 1.08
#     # ffmpeg's zoompan is harder; simpler approach: create a fade-in of scaled image using overlay via loop
#     # We'll use a straightforward command that runs on most ffmpeg versions:
#     cmd = [
#         r"C:\ffmpeg\bin\ffmpeg.exe", "-y", "-loop", "1", "-i", str(image_path),
#         "-vf", f"scale={w}:{h},zoompan=z='if(lte(on,{duration*25}),{zoom_start}+(on/{(duration*25)})*({zoom_end-zoom_start}),{zoom_end})':d={duration*25}:s={w}x{h}",
#         "-c:v", "libx264", "-t", str(duration), "-pix_fmt", "yuv420p", str(out_path)
#     ]
#     # The zoompan expression above attempts to create a zoom across frames. It may vary with ffmpeg versions.
#     # If this fails on some systems, we fallback to a simple image->video conversion:
#     try:
#         subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#     except Exception:
#         # fallback simple loop (no zoom)
#         cmd2 = [r"C:\ffmpeg\bin\ffprobe.exe", "-y", "-loop", "1", "-i", str(image_path), "-c:v", "libx264", "-t", str(duration), "-pix_fmt", "yuv420p", str(out_path)]
#         subprocess.run(cmd2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#     return out_path

FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
from moviepy.editor import ImageClip

def ken_burns_clip(image_path, out_path, duration=4, resolution=(1080, 1920)):
    clip = (ImageClip(image_path)
            .resize(height=resolution[1])
            .set_duration(duration)
            .fx(lambda c: c.resize(lambda t: 1 + 0.02 * t)))  # simple zoom
    clip.write_videofile(str(out_path), fps=25)
    return out_path


def make_clips_for_images(image_paths, duration=8):
    out_clips = []
    for i, img in enumerate(image_paths, start=1):
        out = CLIPS_DIR / f"scene_{i:02d}.mp4"
        ken_burns_clip(img, out, duration=duration)
        out_clips.append(str(out))
    return out_clips

if __name__ == "__main__":
    import sys,json
    if len(sys.argv) < 2:
        print("Usage: python animator.py images_list.json")
        sys.exit(1)
    images = json.load(open(sys.argv[1], 'r', encoding='utf8'))
    clips = make_clips_for_images(images, duration=8)
    print("Created clips:", clips)
