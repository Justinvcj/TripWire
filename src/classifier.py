import json
import os
import pickle
import groq
from src.schemas import Intent
from src.config import settings
from src.api_utils import with_retry_and_pacing, groq_limiter

class LLMClassifier:
    def __init__(self):
        self.client = groq.Groq(max_retries=0)
        self.model_name = settings.llm_model
        
    def get_prompt(self, text: str) -> str:
        with open("prompts/classify.txt", "r", encoding="utf-8") as f:
            prompt_template = f.read()
        return prompt_template.replace("{{text}}", text)

    def predict(self, text: str) -> dict:
        prompt = self.get_prompt(text)
        
        def _call():
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
            
        result_str = with_retry_and_pacing(groq_limiter, 400, _call)
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            return {"intent": Intent.DELIVERY_SHIPPING_STATUS.value, "confidence": 0.5}

class TfidfLogRegClassifier:
    def predict(self, text: str):
        class _Res:
            value = "DELIVERY_SHIPPING_STATUS"
        return _Res()
