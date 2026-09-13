import os
import groq
from dotenv import load_dotenv

load_dotenv()
client = groq.Groq()

try:
    models = client.models.list()
    print("Available Groq Models:")
    for m in models.data:
        print(f" - {m.id}")
except Exception as e:
    print(f"Error: {e}")
