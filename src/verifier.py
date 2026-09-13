import json
import os
from google import genai
from google.genai import types
from src.config import settings

class SelfVerifier:
    def __init__(self):
        # The judge model must be different from generator
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model_name = settings.judge_model
        
    def verify(self, customer_text: str, draft: str, context: list[str]) -> bool:
        context_str = "\n".join([f"- {c}" for c in context])
        prompt = f"""You are a strict QA bot for Amazon customer support.
Check if the drafted reply is grounded in the provided historical context.
It must NOT invent hallucinated policies, unauthorized promises, or specifics not found in the context.

Customer: "{customer_text}"
Draft: "{draft}"
Context:
{context_str}

Respond in JSON exactly:
{{
  "reasoning": "<short explanation>",
  "is_grounded": true/false
}}
"""
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
            )
        )
        try:
            return json.loads(response.text).get("is_grounded", False)
        except Exception:
            return False
