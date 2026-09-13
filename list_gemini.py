import os
from google import genai
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
models = client.models.list()
for m in models:
    if "flash" in m.name:
        print(m.name)
