import json
import os
import pickle
from src.schemas import Intent, TicketResult
from src.config import settings
import groq

class MajorityClassifier:
    def __init__(self, majority_class: str = "DELIVERY_SHIPPING_STATUS"):
        self.majority_class = majority_class

    def predict(self, text: str) -> Intent:
        return Intent(self.majority_class)


class TfidfLogRegClassifier:
    def __init__(self, vectorizer_path="models/baseline2_vectorizer.pkl", model_path="models/baseline2_model.pkl"):
        if not os.path.exists(vectorizer_path) or not os.path.exists(model_path):
            raise FileNotFoundError("Baseline 2 models not found. Run evaluation/train_baseline2.py first.")
            
        with open(vectorizer_path, "rb") as f:
            self.vectorizer = pickle.load(f)
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

    def predict(self, text: str) -> Intent:
        X = self.vectorizer.transform([text])
        pred = self.model.predict(X)[0]
        return Intent(pred)


class LLMClassifier:
    def __init__(self):
        # Assumes GROQ_API_KEY is in environment
        self.client = groq.Groq()
        self.model_name = settings.llm_model
        
    def get_prompt(self, text: str) -> str:
        with open("prompts/classify.txt", "r", encoding="utf-8") as f:
            prompt_template = f.read()
        return prompt_template.replace("{{text}}", text)

    def predict(self, text: str) -> dict:
        prompt = self.get_prompt(text)
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        
        result_str = response.choices[0].message.content
        return json.loads(result_str)
