# scriptwriter.py
# ScriptWriter: two modes:
#  - USE_GEMINI = True -> placeholder example showing how to call an LLM (Gemini).
#  - Fallback extractive summarizer (safe, deterministic).
#
# We strongly recommend using the fallback for the hackathon demo.
#
# If you enable Gemini / LLM calls, ensure you sanitize inputs and only pass
# small cleaned chunks and always validate JSON schema of LLM output.

import json
from sentence_transformers import SentenceTransformer, util
import math

MODEL_NAME = 'all-MiniLM-L6-v2'  # small and fast
model = SentenceTransformer(MODEL_NAME)

def extractive_scene_maker(extracted_sentences, n_scenes=4, max_words=10):
    """
    Splits the extracted sentences into n_scenes chunks by position and picks a representative sentence.
    Returns list of scenes: [{'scene':int,'text':short_text,'source_page':int}, ...]
    """
    sents = [d['sentence'] for d in extracted_sentences]
    pages = [d['page'] for d in extracted_sentences]
    if not sents:
        return []
    total = len(sents)
    chunk_size = max(1, math.ceil(total / n_scenes))
    scenes = []
    for i in range(n_scenes):
        start = i * chunk_size
        end = min(total, (i+1)*chunk_size)
        chunk = sents[start:end]
        chunk_pages = pages[start:end]
        if not chunk:
            continue
        emb = model.encode(chunk, convert_to_tensor=True)
        centroid = emb.mean(dim=0, keepdim=True)
        scores = util.cos_sim(centroid, emb)[0]
        idx = int(scores.argmax())
        chosen = chunk[idx].strip()
        words = chosen.split()
        short = " ".join(words[:max_words]) + ("..." if len(words) > max_words else "")
        scenes.append({'scene': i+1, 'text': short, 'source_page': int(chunk_pages[idx])})
    return scenes

# PLACEHOLDER: Gemini integration
def gemini_script_writer(cleaned_small_doc_text):
    """
    Example placeholder for sending a request to Gemini. This is not an implemented call.
    If you have a Gemini API client, replace this with a safe call:
      - do NOT pass whole PDF
      - use system prompt that forces JSON output and cite sources
      - validate the returned JSON against schema
    For hackathon, prefer extractive_scene_maker.
    """
    raise NotImplementedError("Gemini integration is not enabled in this demo. Use extractive_scene_maker() instead.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scriptwriter.py extracted_sentences.json")
        sys.exit(1)
    data = json.load(open(sys.argv[1], 'r', encoding='utf8'))
    scenes = extractive_scene_maker(data, n_scenes=4, max_words=10)
    json.dump(scenes, open('scenes.json','w',encoding='utf8'), indent=2)
    print(f"Wrote {len(scenes)} scenes -> scenes.json")
