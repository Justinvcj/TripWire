import json
import os
from google import genai
from google.genai import types
from src.config import settings

class LLMJudge:
    def __init__(self):
        # Assumes GEMINI_API_KEY is in environment
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model_name = settings.judge_model

    def evaluate_reply(self, customer_text: str, drafted_reply: str, reference_reply: str) -> dict:
        prompt = f"""You are an expert QA evaluator for customer support.
Evaluate the drafted reply against the customer's query and the historical reference reply.

Customer Query: "{customer_text}"
Reference Reply (Historical): "{reference_reply}"
Drafted Reply: "{drafted_reply}"

Score the drafted reply on a scale of 1 to 5, where:
1 - Unhelpful, hallucinated, or actively harmful.
2 - Poor, misses the main point or has incorrect tone.
3 - Acceptable, but lacks clarity or grounding.
4 - Good, accurate and polite.
5 - Excellent, fully resolves the issue with perfect tone and grounding.

Respond in JSON exactly as follows:
{{
  "score": <int>,
  "reasoning": "<short string explaining the score>"
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
            return json.loads(response.text)
        except Exception:
            return {"score": 3, "reasoning": "Failed to parse judge output."}
