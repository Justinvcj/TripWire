import os
import groq
from dotenv import load_dotenv
load_dotenv()
client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))
print(client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role": "user", "content": "hi"}]))
