# visuals_maker.py
# VisualsMaker: two-tier approach
# 1) If you have Stable Diffusion and the 'diffusers' environment set up, you can enable SD by setting USE_SD=True
# 2) Otherwise fallback to simple doodle generation by rendering SVG icons with Pillow or returning a placeholder image.
#
# The fallback is fast and works on CPU.

import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from tqdm import tqdm

# Toggle this to True if you have SD model & GPU & diffusers installed
USE_SD = False

if USE_SD:
    # Example additional imports for SD (not installed by default)
    # from diffusers import StableDiffusionPipeline
    # import torch
    pass

# directory for produced images
OUT_DIR = Path("visuals_out")
OUT_DIR.mkdir(exist_ok=True)

# simple doodle generator: draw a big icon-label box with text and sketched circle
def make_doodle_from_keywords(scene_text, out_path, size=(1080,1920), bg=(255,255,255)):
    w,h = size
    img = Image.new("RGB", (w,h), color=bg)
    draw = ImageDraw.Draw(img)
    # draw a "hand-drawn" circle
    r = min(w,h)//4
    cx,cy = w//2, h//3
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), outline=(0,0,0), width=6)
    # draw text (centered)
    font = ImageFont.load_default()
    # wrap text
    lines = []
    words = scene_text.split()
    line = ""
    for word in words:
        if len(line + " " + word) > 20:
            lines.append(line.strip())
            line = word
        else:
            line += " " + word
    lines.append(line.strip())
    # place lines under circle
    start_y = cy + r + 30
    for i, ln in enumerate(lines):
        bbox = draw.textbbox((0, 0), ln, font=font)
        w_text = bbox[2] - bbox[0]
        h_text = bbox[3] - bbox[1]
        draw.text(((w - w_text)//2, start_y + i*20), ln, fill=(0, 0, 0), font=font)

    img.save(out_path)
    return out_path

def generate_visuals_for_scenes(scenes, use_sd=False):
    """
    scenes: list of {'scene','text','source_page'}
    returns: list of output image paths (one per scene)
    """
    out_paths = []
    for sc in tqdm(scenes, desc="Generating visuals"):
        fname = OUT_DIR / f"scene_{sc['scene']:02d}.png"
        if use_sd and USE_SD:
            # Insert your SD generation pipeline here (not included).
            # For example: prompt = f"doodle sketch of {sc['text']} in line-art style"
            # call pipeline and save image to fname
            pass
        else:
            make_doodle_from_keywords(sc['text'], fname)
        out_paths.append(str(fname))
    return out_paths

if __name__ == "__main__":
    import sys, json
    if len(sys.argv) < 2:
        print("Usage: python visuals_maker.py scenes.json")
        sys.exit(1)
    scenes = json.load(open(sys.argv[1], 'r', encoding='utf8'))
    out = generate_visuals_for_scenes(scenes, use_sd=False)
    print("Generated images:", out)
