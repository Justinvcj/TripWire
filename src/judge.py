import json
import os
from google import genai
from google.genai import types
from src.config import settings
from src.api_utils import with_retry_and_pacing, gemini_limiter

class LLMJudge:
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model_name = settings.judge_model

    def evaluate_reply(self, customer_text: str, drafted_reply: str, reference_reply: str) -> dict:
        prompt = f"""You are an expert QA evaluator for customer support.
Evaluate the drafted reply against the customer's query and the historical reference reply on three separate axes.

Customer Query: "{customer_text}"
Reference Reply (Historical): "{reference_reply}"
Drafted Reply: "{drafted_reply}"

Score each axis from 1 to 5:
- groundedness: Is the reply factual and supported by policy/reference? (1=hallucinated, 5=perfectly grounded)
- actionability: Does it give the user clear next steps? (1=useless, 5=clear resolution path)
- tone: Is it polite, empathetic, and on-brand? (1=rude/robotic, 5=perfect empathy)

Respond in JSON exactly as follows:
{{
  "groundedness": <int>,
  "actionability": <int>,
  "tone": <int>,
  "reasoning": "<short explanation for the scores>"
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
            data = json.loads(res_str)
            return {
                "groundedness": data.get("groundedness", 3),
                "actionability": data.get("actionability", 3),
                "tone": data.get("tone", 3),
                "reasoning": data.get("reasoning", "")
            }
        except Exception:
            return {"groundedness": 3, "actionability": 3, "tone": 3, "reasoning": "Failed to parse judge output."}
