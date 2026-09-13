from src.schemas import EscalationReason, Action, Intent

class TriageEngine:
    def __init__(self, confidence_threshold: float):
        self.confidence_threshold = confidence_threshold

    def evaluate(self, customer_text: str, intent: Intent, confidence: float, is_grounded: bool) -> (Action, EscalationReason):
        if intent == Intent.NON_ENGLISH_QUERY:
            return Action.ESCALATE_TO_HUMAN, EscalationReason.NON_ENGLISH

        if confidence < self.confidence_threshold:
            return Action.ESCALATE_TO_HUMAN, EscalationReason.LOW_INTENT_CONFIDENCE
            
        if not is_grounded:
            return Action.ESCALATE_TO_HUMAN, EscalationReason.VERIFICATION_FAILED
            
        lower_text = customer_text.lower()
        if "lawsuit" in lower_text or "sue" in lower_text or "attorney" in lower_text:
            return Action.ESCALATE_TO_HUMAN, EscalationReason.LEGAL_REPUTATIONAL_RISK
            
        if "ssn" in lower_text or "credit card" in lower_text or "password" in lower_text:
            return Action.ESCALATE_TO_HUMAN, EscalationReason.PII_REQUIRED_DM_HANDOFF
            
        return Action.AUTO_HANDLE, EscalationReason.NONE
