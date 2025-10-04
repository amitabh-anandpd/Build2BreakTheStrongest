# narrator.py
# Narrator: two modes: Piper (placeholder) or fallback gTTS
# Fallback is used by default for hackathon.

from gtts import gTTS
from pydub import AudioSegment
from pathlib import Path
import os

AUDIO_DIR = Path("audio_out")
AUDIO_DIR.mkdir(exist_ok=True)

USE_PIPER = False  # set True if you have Piper TTS integration

def piper_tts_placeholder(text, out_path):
    """
    Placeholder for piper TTS integration.
    If you integrate Piper, replace this implementation accordingly.
    """
    raise NotImplementedError("Piper TTS not integrated in this demo. Use gTTS fallback.")

import re
def is_speakable(text: str) -> bool:
    """Return True if text has at least one letter or pronounceable word."""
    return bool(re.search(r'[A-Za-z]', text))

# def tts_gtts(text, out_path, lang="en", target_duration_ms=8000):
#     # create TTS and pad/trim to target duration (in ms)
#     tmp = out_path + ".tmp.mp3"
#     tts = gTTS(text=text, lang=lang)
#     tts.save(tmp)
#     audio = AudioSegment.from_mp3(tmp)
#     if len(audio) < target_duration_ms:
#         audio = audio + AudioSegment.silent(duration=(target_duration_ms - len(audio)))
#     else:
#         # if audio longer, shorten with small fade
#         audio = audio[:target_duration_ms]
#     audio.export(out_path, format="mp3")
#     os.remove(tmp)
#     return out_path

from gtts import gTTS
from moviepy.editor import AudioClip
from moviepy.editor import AudioFileClip

def tts_gtts(text, out_path, target_duration_ms=None):
    text = (text or "").strip()  # handle None too
    if not is_speakable(text):
        print(f"⚠️ Skipping non-speakable text for {out_path!r}: {repr(text)}")
        duration = target_duration_ms or 8000
        silent = AudioClip(lambda t: 0, duration=duration/1000)
        silent.write_audiofile(out_path, fps=44100)
        return
    if not text:
        print(f"⚠️ Empty text for {out_path}, generating silent audio")
        duration = target_duration_ms or 8000
        # create silent audio using MoviePy
        silent = AudioClip(lambda t: 0, duration=duration/1000)
        silent.write_audiofile(out_path, fps=44100)
        return

    tts = gTTS(text)
    tmp_path = out_path.replace(".mp3", "_raw.mp3")
    tts.save(tmp_path)

    if target_duration_ms:
        audio = AudioFileClip(tmp_path)
        audio = audio.set_duration(target_duration_ms / 1000)
        audio.write_audiofile(out_path)
        audio.close()
        os.remove(tmp_path)
    else:
        os.rename(tmp_path, out_path)

    print(f"✅ Saved narration: {out_path}")


def generate_narration_files(scenes, per_scene_duration_ms=8000):
    files = []
    for sc in scenes:
        out = AUDIO_DIR / f"scene_{sc['scene']:02d}.mp3"
        text = sc['text']
        print(f"🎙 Scene {sc['scene']}: {repr(text)}")
        if USE_PIPER:
            piper_tts_placeholder(text, str(out))
        else:
            tts_gtts(text, str(out), target_duration_ms=per_scene_duration_ms)
        files.append(str(out))
    return files

if __name__ == "__main__":
    import sys,json
    if len(sys.argv) < 2:
        print("Usage: python narrator.py scenes.json")
        sys.exit(1)
    scenes = json.load(open(sys.argv[1], 'r', encoding='utf8'))
    out = generate_narration_files(scenes, per_scene_duration_ms=8000)
    print("Generated audio:", out)
