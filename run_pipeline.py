# run_pipeline.py
# High-level orchestrator: runs full pipeline end-to-end using fallback components by default.

import json, os
from pathlib import Path

from pdf_extractor import extract_text_sentences
from scriptwriter import extractive_scene_maker
from visuals_maker import generate_visuals_for_scenes
from animator import make_clips_for_images
from narrator import generate_narration_files
from composer import compose_final

WORKDIR = Path(".").resolve()
SAMPLE_PDF = WORKDIR / "input.pdf"  # put your PDF here
SCENES_FILE = WORKDIR / "scenes.json"
IMAGES_FILE = WORKDIR / "images.json"
CLIPS_FILE = WORKDIR / "clips.json"
AUDIOS_FILE = WORKDIR / "audios.json"

def run(pdf_path=SAMPLE_PDF, n_scenes=4, per_scene_duration=8):
    print("1) Extracting text from PDF ...")
    extracted = extract_text_sentences(str(pdf_path))
    if not extracted:
        raise RuntimeError("No text extracted. PDF may be image-only. Consider OCR fallback.")

    print("2) Generating scene script (extractive summarizer)...")
    scenes = extractive_scene_maker(extracted, n_scenes=n_scenes, max_words=12)
    if not scenes:
        raise RuntimeError("Script generation failed.")

    print("3) Generating visuals (fallback doodles) ...")
    images = generate_visuals_for_scenes(scenes, use_sd=False)

    print("4) Animating visuals into clips (Ken Burns) ...")
    clips = make_clips_for_images(images, duration=per_scene_duration)

    print("5) Generating narration audio (gTTS fallback) ...")
    audios = generate_narration_files(scenes, per_scene_duration_ms=per_scene_duration*1000)

    # Save intermediary manifests
    json.dump(scenes, open(SCENES_FILE, 'w', encoding='utf8'), indent=2)
    json.dump(images, open(IMAGES_FILE, 'w', encoding='utf8'), indent=2)
    json.dump(clips, open(CLIPS_FILE, 'w', encoding='utf8'), indent=2)
    json.dump(audios, open(AUDIOS_FILE, 'w', encoding='utf8'), indent=2)

    print("6) Composing final video ...")
    final = compose_final(clips, audios, scenes)
    print("All done. Final file:", final)

if __name__ == "__main__":
    import sys
    pdf = sys.argv[1] if len(sys.argv) > 1 else "input.pdf"
    if not Path(pdf).exists():
        print(f"Place your source PDF at {pdf} and rerun.")
    else:
        run(pdf_path=pdf, n_scenes=5, per_scene_duration=4)
