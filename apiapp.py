# app.py
from flask import Flask, request, jsonify
import requests
import time
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

app = Flask(__name__)

AI_API_KEY = os.getenv("AI_API_KEY")
AI_BASE_URL = os.getenv("AI_BASE_URL")

@app.route("/generate_video", methods=["POST"])
def generate_video():
    data = request.json
    text_prompt = data.get("text_prompt")

    if not text_prompt:
        return jsonify({"error": "Missing 'text_prompt'"}), 400

    # Prepare request body as per your example
    payload = {
        "text_prompt": text_prompt,
        "model": "gen3",
        "width": 1344,
        "height": 768,
        "motion": 5,
        "seed": 0,
        "callback_url": "",
        "time": 5
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": AI_API_KEY
    }

    # Step 1: Call AI Video API
    resp = requests.post(f"{AI_BASE_URL}/generate", json=payload, headers=headers)
    if resp.status_code not in (200, 202):
        return jsonify({"error": "AI API call failed", "details": resp.text}), 500

    result = resp.json()
    render_id = result.get("id") or result.get("render_id")
    if not render_id:
        return jsonify({"error": "No render ID returned", "response": result}), 500

    # Step 2: Poll until ready
    video_url = None
    for _ in range(30):  # poll up to 30 times (~150s)
        time.sleep(5)
        status_resp = requests.get(f"{AI_BASE_URL}/renders/{render_id}", headers=headers)
        if status_resp.status_code != 200:
            continue
        status_data = status_resp.json()
        status = status_data.get("status")

        if status == "completed":
            video_url = status_data.get("video_url")
            break
        elif status == "failed":
            return jsonify({"error": "Video generation failed", "details": status_data}), 500

    if not video_url:
        return jsonify({"error": "Timeout waiting for video"}), 504

    return jsonify({"video_url": video_url})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
