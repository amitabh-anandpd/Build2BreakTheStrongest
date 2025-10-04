# # composer.py
# # Stitches per-scene clips and per-scene audio into a single vertical mp4 (1080x1920)
# # Adds overlay text for title and per-scene source citations
# # Uses ffmpeg via subprocess to avoid heavy Python video libraries

# import subprocess
# import json
# from pathlib import Path
# import os
# import tempfile

# OUT_DIR = Path("final_out")
# OUT_DIR.mkdir(exist_ok=True)

# def compose_final(clips, audios, scenes, output_path=None):
#     """
#     clips: list of per-scene mp4 files (must match order)
#     audios: list of per-scene mp3 files (must match order)
#     scenes: list of scene metadata dictionaries containing 'scene', 'source_page', etc.
#     output_path: final mp4 path
#     """
#     assert len(clips) == len(audios) == len(scenes), "clips/audios/scenes length mismatch"
#     if output_path is None:
#         output_path = OUT_DIR / "short_final.mp4"
#     out = str(output_path)

#     # Step 1: ensure each clip has its audio merged (or create interim files)
#     intermediates = []
#     for i, (clip, audio) in enumerate(zip(clips, audios), start=1):
#         merged = Path(tempfile.gettempdir()) / f"merge_scene_{i:02d}.mp4"
#         # ffmpeg: combine video (no audio) + audio, re-encode
#         cmd = [
#             "ffmpeg", "-y", "-i", clip, "-i", audio,
#             "-c:v", "libx264", "-c:a", "aac", "-shortest", str(merged)
#         ]
#         subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#         intermediates.append(str(merged))

#     # Step 2: concatenate all intermediates into one big clip using ffmpeg concat demuxer
#     list_file = Path(tempfile.gettempdir()) / "concat_list.txt"
#     with open(list_file, "w", encoding="utf8") as f:
#         for p in intermediates:
#             f.write(f"file '{p}'\n")
#     concatenated = Path(tempfile.gettempdir()) / "concatenated.mp4"
#     cmd2 = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(concatenated)]
#     subprocess.run(cmd2, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

#     # Step 3: overlay title and per-scene citation text. We'll place a single persistent footer showing
#     # "Source: input.pdf (pages ...)" to keep it simple. More sophisticated per-scene text needs timestamps.
#     # Build citation string
#     pages = sorted(set([sc.get("source_page") for sc in scenes if sc.get("source_page")]))
#     citation = f"Source pages: {', '.join(map(str,pages))}" if pages else ""
#     drawtext = f"drawtext=text='{citation}':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=h-120:box=1:boxcolor=black@0.5"
#     cmd3 = [
#         "ffmpeg", "-y", "-i", str(concatenated),
#         "-vf", drawtext,
#         "-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p", str(out)
#     ]
#     subprocess.run(cmd3, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

#     # cleanup temporaries optionally
#     print("Final video written to:", out)
#     return out

# if __name__ == "__main__":
#     # Example usage:
#     import sys, json
#     if len(sys.argv) < 4:
#         print("Usage: python composer.py clips_json audios_json scenes_json")
#         print("Each json is a list of file paths / dicts")
#         sys.exit(1)
#     clips = json.load(open(sys.argv[1],'r',encoding='utf8'))
#     audios = json.load(open(sys.argv[2],'r',encoding='utf8'))
#     scenes = json.load(open(sys.argv[3],'r',encoding='utf8'))
#     compose_final(clips, audios, scenes)

# composer.py (MoviePy version - no ffmpeg subprocess)
# Combines per-scene video + audio, adds footer text overlay

# composer.py
# Combines per-scene video + audio, adds overlay text using MoviePy
# No ffmpeg subprocess calls required
# Works even without ImageMagick (uses method='caption')

# composer.py
# Combines per-scene video + audio, adds overlay text using MoviePy (no ImageMagick)
# Uses Pillow backend with method='caption' and font

# composer.py — FINAL
# Combines per-scene video + audio, adds footer text using Pillow (no ImageMagick)


# composer.py — Stable version (no ImageMagick, no duration mismatch)

# composer.py — Final Stable Version
from moviepy.editor import (
    VideoFileClip, AudioFileClip,
    TextClip, CompositeVideoClip,
    concatenate_videoclips, concatenate_audioclips, AudioClip
)
from pathlib import Path

OUT_DIR = Path("final_out")
OUT_DIR.mkdir(exist_ok=True)

DEFAULT_FONT = "C:/Windows/Fonts/arial.ttf"  # ✅ Full font path (important for Pillow backend)

def safe_text_clip(text, duration, fontsize=40, position=("center", "bottom")):
    """Create text clip using Pillow (method='caption'), no ImageMagick."""
    text = (text or "").strip()
    if not text:
        return None
    try:
        txt = (TextClip(
            text,
            fontsize=fontsize,
            color='white',
            bg_color='black',
            method='caption',
            font=DEFAULT_FONT,
            size=(1000, None)
        )
        .set_duration(duration)
        .set_position(position))
        return txt
    except Exception as e:
        print(f"⚠️ Could not render text '{text}': {e}")
        return None


def pad_audio_to_duration(audio, duration):
    """Return audio padded or trimmed to exactly match the given duration."""
    if audio.duration < duration:
        # pad with silence
        silence = AudioClip(lambda t: 0, duration=(duration - audio.duration))
        new_audio = concatenate_audioclips([audio, silence])
    elif audio.duration > duration:
        # trim extra
        new_audio = audio.subclip(0, duration)
    else:
        new_audio = audio
    return new_audio.set_duration(duration)


def compose_final(clips, audios, scenes, output_path=None):
    assert len(clips) == len(audios) == len(scenes), "clips/audios/scenes length mismatch"

    if output_path is None:
        output_path = OUT_DIR / "short_final.mp4"
    out = str(output_path)

    composed = []

    for i, (clip_path, audio_path, scene) in enumerate(zip(clips, audios, scenes), start=1):
        print(f"🎬 Scene {i}: combining {clip_path} + {audio_path}")

        video = VideoFileClip(str(clip_path))
        audio = AudioFileClip(str(audio_path))

        # align durations
        audio = pad_audio_to_duration(audio, video.duration)
        video = video.set_audio(audio)

        # add footer text
        src_page = scene.get("source_page")
        footer_text = f"Source page: {src_page}" if src_page else ""
        txt = safe_text_clip(footer_text, duration=video.duration)
        if txt:
            video = CompositeVideoClip([video, txt])

        composed.append(video)


    print("🎬 Concatenating all scenes...")
    final = concatenate_videoclips(composed, method="compose") # This implicitly concatenates the audio too

    # --- NEW FIX FOR IndexError ---
    # Recreate the audio track separately for robustness against duration/indexing errors
    # 1. Collect all *padded* audios
    padded_audios = []
    for i, (clip_path, audio_path, scene) in enumerate(zip(clips, audios, scenes), start=1):
        video = VideoFileClip(str(clip_path))
        audio = AudioFileClip(str(audio_path))
        audio = pad_audio_to_duration(audio, video.duration) # Use the existing safe padding
        padded_audios.append(audio)
    
    # 2. Concatenate the padded audios
    final_audio = concatenate_audioclips(padded_audios)
    
    # 3. Trim/pad the final audio to exactly match the final video's duration
    final_audio = pad_audio_to_duration(final_audio, final.duration)
    
    # 4. Set this explicitly combined audio to the final video clip
    final = final.set_audio(final_audio) 
    # ------------------------------

    # final footer overlay with all pages
    # ... (Your existing footer code)
    
    print(f"🎥 Writing final video to: {out}")
    final.write_videofile(out, fps=25, logger=None) # Added logger=None to clean up output
    print("✅ Final video ready!")
    return out

if __name__ == "__main__":
    import sys, json
    if len(sys.argv) < 4:
        print("Usage: python composer.py clips_json audios_json scenes_json")
        sys.exit(1)
    clips = json.load(open(sys.argv[1], 'r', encoding='utf8'))
    audios = json.load(open(sys.argv[2], 'r', encoding='utf8'))
    scenes = json.load(open(sys.argv[3], 'r', encoding='utf8'))
    compose_final(clips, audios, scenes)
