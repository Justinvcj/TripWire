import json
import groq
from src.config import settings

class SelfVerifier:
    def __init__(self):
        # The judge model must be different from generator
        self.client = groq.Groq()
        self.model_name = settings.judge_model
        
    def verify(self, customer_text: str, draft: str, context: list[str]) -> bool:
        context_str = "\n".join([f"- {c}" for c in context])
        prompt = f"""You are a QA bot for Amazon customer support.
Check if the drafted reply is grounded in the provided historical context and doesn't invent hallucinated policies or promises.

Customer: "{customer_text}"
Draft: "{draft}"
Context:
{context_str}

Respond in JSON exactly:
{{
  "is_grounded": true/false
}}
"""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        try:
            return json.loads(response.choices[0].message.content).get("is_grounded", False)
        except Exception:
            return False
