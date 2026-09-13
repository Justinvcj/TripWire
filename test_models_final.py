import os
import groq
from google import genai
from google.genai import types
from dotenv import load_dotenv
import json

load_dotenv()

print("Testing Groq (openai/gpt-oss-120b)...")
groq_client = groq.Groq()
groq_resp = groq_client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": 'Respond in JSON: {"status": "ok"}'}],
    temperature=0.0,
    response_format={"type": "json_object"}
)
print("Groq Response:", groq_resp.choices[0].message.content)

print("\nTesting Gemini (gemini-3.6-flash)...")
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
gemini_resp = gemini_client.models.generate_content(
    model="gemini-3.6-flash",
    contents='Respond in JSON: {"status": "ok"}',
    config=types.GenerateContentConfig(
        temperature=0.0,
        response_mime_type="application/json",
    )
)
print("Gemini Response:", gemini_resp.text)
