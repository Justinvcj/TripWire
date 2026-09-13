import json
import os
from google import genai
from google.genai import types
from src.config import settings
from src.api_utils import with_retry_and_pacing, gemini_limiter

class SelfVerifier:
    def __init__(self):
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
        def _call():
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                )
            )
            return response.text
            
        try:
            res_str = with_retry_and_pacing(gemini_limiter, 400, _call)
            return json.loads(res_str).get("is_grounded", False)
        except Exception as e:
            return False
