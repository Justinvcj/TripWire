import json
import os
import google.genai as genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

prompt = "Output exactly in JSON:\n{\"gold_intent\": \"TEST\", \"gold_action\": \"TEST\"}"
try:
    res = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json",
        )
    )
    print("Success:", res.text)
except Exception as e:
    print("Exception occurred:", repr(e))
