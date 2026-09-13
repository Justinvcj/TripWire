import os
import groq
from dotenv import load_dotenv
load_dotenv()
client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))
print([m.id for m in client.models.list().data])
