from src.schemas import TicketResult, EscalationReason, Action, Intent
from src.preprocessor import Preprocessor
from src.classifier import LLMClassifier
from src.vector_store import VectorStore
from src.generator import ReplyGenerator
from src.verifier import SelfVerifier
from src.triage import TriageEngine
from src.config import settings

class Pipeline:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.classifier = LLMClassifier()
        self.vector_store = VectorStore()
        self.generator = ReplyGenerator()
        self.verifier = SelfVerifier()
        self.triage = TriageEngine(confidence_threshold=settings.confidence_threshold)

    def process_ticket(self, tweet_id: str, raw_text: str) -> TicketResult:
        cleaned_text = self.preprocessor.clean_text(raw_text)
        
        class_res = self.classifier.predict(cleaned_text)
        intent = Intent(class_res['intent'])
        confidence = class_res['confidence']
        
        retrieval = self.vector_store.retrieve(cleaned_text)
        context = retrieval.get("documents", [[]])[0]
        distances = retrieval.get("distances", [[]])[0]
        # Convert L2 distance roughly to similarity score (higher is better) for tracking
        similarity_scores = [max(0.0, 1.0 - d) for d in distances]
        
        draft = ""
        is_grounded = False
        verifier_retries = 0
        
        # Action/Triage based on intent & confidence first
        action, reason = self.triage.evaluate(cleaned_text, intent, confidence, is_grounded=True)
        
        if action == Action.AUTO_HANDLE:
            draft = self.generator.generate(cleaned_text, intent.value, context)
            is_grounded = self.verifier.verify(cleaned_text, draft, context)
            
            while not is_grounded and verifier_retries < settings.max_verifier_retries:
                verifier_retries += 1
                draft = self.generator.generate(cleaned_text, intent.value, context)
                is_grounded = self.verifier.verify(cleaned_text, draft, context)
                
            if not is_grounded:
                action = Action.ESCALATE_TO_HUMAN
                reason = EscalationReason.VERIFICATION_FAILED
                
        return TicketResult(
            tweet_id=tweet_id,
            intent=intent,
            intent_confidence=confidence,
            action=action,
            escalation_reason=reason,
            draft_reply=draft,
            verifier_retries=verifier_retries,
            retrieval_scores=similarity_scores
        )
