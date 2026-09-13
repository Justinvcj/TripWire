from src.preprocessor import Preprocessor
from src.classifier import LLMClassifier
from src.vector_store import VectorStore
from src.generator import ReplyGenerator
from src.verifier import SelfVerifier
from src.triage import TriageEngine
from src.schemas import TicketResult, Intent
from src.config import settings

class Pipeline:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.classifier = LLMClassifier()
        self.vector_store = VectorStore()
        self.generator = ReplyGenerator()
        self.verifier = SelfVerifier()
        self.triage = TriageEngine(settings.confidence_threshold)

    def process_ticket(self, tweet_id: str, customer_text: str) -> TicketResult:
        # 1. Clean
        cleaned_text = self.preprocessor.clean_text(customer_text)
        
        # 2. Classify
        classification = self.classifier.predict(cleaned_text)
        intent = Intent(classification['intent'])
        confidence = float(classification['confidence'])
        
        # 3. Retrieve
        retrieved_docs = self.vector_store.retrieve(cleaned_text)
        context = retrieved_docs['documents'][0] if retrieved_docs['documents'] else []
        
        # 4. Generate
        draft = self.generator.generate(cleaned_text, intent, context)
        
        # 5. Verify
        is_grounded = self.verifier.verify(cleaned_text, draft, context)
        
        # 6. Triage
        action, reason = self.triage.evaluate(cleaned_text, intent, confidence, is_grounded)
        
        return TicketResult(
            tweet_id=tweet_id,
            intent=intent,
            intent_confidence=confidence,
            action=action,
            escalation_reason=reason,
            draft_reply=draft if action == "AUTO_HANDLE" else None
        )
