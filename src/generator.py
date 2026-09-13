import json
import groq
from src.config import settings
from src.schemas import Intent

class ReplyGenerator:
    def __init__(self):
        self.client = groq.Groq()
        self.model_name = settings.llm_model

    def generate(self, customer_text: str, intent: Intent, context: list[str]) -> str:
        prompt = self._build_prompt(customer_text, intent, context)
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    def _build_prompt(self, text: str, intent: str, context: list[str]) -> str:
        context_str = "\n".join([f"- {c}" for c in context])
        return f"""You are an @AmazonHelp customer support agent.
The customer has reached out with intent: {intent}.
Here are historical ways we have resolved similar issues:
{context_str}

Draft a helpful, polite, and concise reply to the customer. Limit to {settings.max_reply_chars} characters.
Do not invent policies that are not in the historical resolutions.
If the historical resolutions just ask for a DM, do the same.

Customer Tweet: "{text}"
Reply:"""
