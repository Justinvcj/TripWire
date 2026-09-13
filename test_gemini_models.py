import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello"
    )
    print("gemini-2.5-flash works")
except Exception as e:
    print(f"Error with 2.5-flash: {e}")

try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Hello"
    )
    print("gemini-2.0-flash works")
except Exception as e:
    print(f"Error with 2.0-flash: {e}")
