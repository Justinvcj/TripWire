import groq
from src.config import settings
from src.api_utils import with_retry_and_pacing, groq_limiter

class ReplyGenerator:
    def __init__(self):
        self.client = groq.Groq(max_retries=0)
        self.model_name = settings.llm_model
        
    def generate(self, customer_text: str, intent: str, context: list[str]) -> str:
        context_str = "\n".join([f"- {c}" for c in context])
        prompt = f"""You are an expert Amazon customer support agent.
Draft a polite, helpful reply to this customer.
Ensure it aligns with their intent: {intent}.
Use the historical examples below as style and policy reference. Do NOT invent new policies.
Keep it under {settings.max_reply_chars} characters.

Historical Examples:
{context_str}

Customer Tweet: "{customer_text}"
Drafted Reply:"""
        
        def _call():
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content
            
        return with_retry_and_pacing(groq_limiter, 800, _call)
