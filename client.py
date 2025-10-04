# client.py
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
API_URL = os.getenv("API_URL")
API_URL_LOCAL = os.getenv("API_URL_LOCAL")

prompt_text = "doodle video, hackathon scene"

response = requests.post(
    API_URL_LOCAL,
    json={"text_prompt": prompt_text}
)

if response.status_code == 200:
    data = response.json()
    print("✅ Video generated!")
    print("🎥 URL:", data["video_url"])
else:
    print("❌ Error:", response.text)

# https://files.aivideoapi.com/20251004/1759578766055984063-video_raw_41d1aaa4be499fe1cc105b2d69741ef1_430849236075454473_cut.mp4