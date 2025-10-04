# composer.py
# Stitches per-scene clips and per-scene audio into a single vertical mp4 (1080x1920)
# Adds overlay text for title and per-scene source citations
# Uses ffmpeg via subprocess to avoid heavy Python video libraries

import subprocess
import json
from pathlib import Path
import os
import tempfile

OUT_DIR = Path("final_out")
OUT_DIR.mkdir(exist_ok=True)

def compose_final(clips, audios, scenes, output_path=None):
    """
    clips: list of per-scene mp4 files (must match order)
    audios: list of per-scene mp3 files (must match order)
    scenes: list of scene metadata dictionaries containing 'scene', 'source_page', etc.
    output_path: final mp4 path
    """
    assert len(clips) == len(audios) == len(scenes), "clips/audios/scenes length mismatch"
    if output_path is None:
        output_path = OUT_DIR / "short_final.mp4"
    out = str(output_path)

    # Step 1: ensure each clip has its audio merged (or create interim files)
    intermediates = []
    for i, (clip, audio) in enumerate(zip(clips, audios), start=1):
        merged = Path(tempfile.gettempdir()) / f"merge_scene_{i:02d}.mp4"
        # ffmpeg: combine video (no audio) + audio, re-encode
        cmd = [
            "ffmpeg", "-y", "-i", clip, "-i", audio,
            "-c:v", "libx264", "-c:a", "aac", "-shortest", str(merged)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        intermediates.append(str(merged))

    # Step 2: concatenate all intermediates into one big clip using ffmpeg concat demuxer
    list_file = Path(tempfile.gettempdir()) / "concat_list.txt"
    with open(list_file, "w", encoding="utf8") as f:
        for p in intermediates:
            f.write(f"file '{p}'\n")
    concatenated = Path(tempfile.gettempdir()) / "concatenated.mp4"
    cmd2 = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(concatenated)]
    subprocess.run(cmd2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Step 3: overlay title and per-scene citation text. We'll place a single persistent footer showing
    # "Source: input.pdf (pages ...)" to keep it simple. More sophisticated per-scene text needs timestamps.
    # Build citation string
    pages = sorted(set([sc.get("source_page") for sc in scenes if sc.get("source_page")]))
    citation = f"Source pages: {', '.join(map(str,pages))}" if pages else ""
    drawtext = f"drawtext=text='{citation}':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=h-120:box=1:boxcolor=black@0.5"
    cmd3 = [
        "ffmpeg", "-y", "-i", str(concatenated),
        "-vf", drawtext,
        "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p", str(out)
    ]
    subprocess.run(cmd3, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # cleanup temporaries optionally
    print("Final video written to:", out)
    return out

if __name__ == "__main__":
    # Example usage:
    import sys, json
    if len(sys.argv) < 4:
        print("Usage: python composer.py clips_json audios_json scenes_json")
        print("Each json is a list of file paths / dicts")
        sys.exit(1)
    clips = json.load(open(sys.argv[1],'r',encoding='utf8'))
    audios = json.load(open(sys.argv[2],'r',encoding='utf8'))
    scenes = json.load(open(sys.argv[3],'r',encoding='utf8'))
    compose_final(clips, audios, scenes)
