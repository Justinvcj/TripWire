import os
import groq
from dotenv import load_dotenv
load_dotenv()
client = groq.Groq(api_key=os.environ.get("GEMINI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
res = client.chat.completions.create(model="gemini-1.5-flash", messages=[{"role": "user", "content": "hi"}])
print(res.choices[0].message.content)
