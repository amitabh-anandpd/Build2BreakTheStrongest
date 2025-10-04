# import requests

# headers = {"Authorization": "Bearer 741add49e9745ea49fcfaf470a62d03f", "Content-Type": "application/json"}
# payload = {
#   "text_prompt": "masterpiece, cinematic, man smoking cigarette looking outside window, moving around",
#   "model": "gen3",
#   "width": 1344,
#   "height": 768,
#   "motion": 5,
#   "seed": 0,
#   "callback_url": "",
#   "time": 5
# }

# r = requests.post("https://api.aivideoapi.com/runway/generate/text", headers=headers, json=payload)
# print(r.status_code, r.text)
import shutil
print("FFMPEG PATH:", shutil.which("ffmpeg"))
