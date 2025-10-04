# client.py
import requests
import os
from dotenv import load_dotenv

env_path = ".env"
if env_path.exists():
    load_dotenv(env_path)
API_URL = os.getenv("API_URL")
API_URL_LOCAL = os.getenv("API_URL_LOCAL")

prompt_text = "masterpiece, cinematic, man smoking cigarette looking outside window, moving around"

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
