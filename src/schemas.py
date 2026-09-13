from enum import Enum
from pydantic import BaseModel
from typing import Optional, List

class Intent(str, Enum):
    DELIVERY_SHIPPING_STATUS = "DELIVERY_SHIPPING_STATUS"
    REFUND_CANCELLATION_BILLING = "REFUND_CANCELLATION_BILLING"
    WRONG_OR_DEFECTIVE_ITEM = "WRONG_OR_DEFECTIVE_ITEM"
    NON_ENGLISH_QUERY = "NON_ENGLISH_QUERY"
    FEEDBACK_CHITCHAT = "FEEDBACK_CHITCHAT"

class EscalationReason(str, Enum):
    LOW_INTENT_CONFIDENCE = "LOW_INTENT_CONFIDENCE"
    OUT_OF_DISTRIBUTION_ANOMALY = "OUT_OF_DISTRIBUTION_ANOMALY"
    PII_REQUIRED_DM_HANDOFF = "PII_REQUIRED_DM_HANDOFF"
    LEGAL_REPUTATIONAL_RISK = "LEGAL_REPUTATIONAL_RISK"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    NON_ENGLISH = "NON_ENGLISH"
    NONE = "NONE"

class Action(str, Enum):
    AUTO_HANDLE = "AUTO_HANDLE"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"

class TicketResult(BaseModel):
    tweet_id: str
    intent: Intent
    intent_confidence: float
    action: Action
    escalation_reason: EscalationReason
    draft_reply: Optional[str] = None
    verifier_retries: int = 0
    retrieval_scores: List[float] = []
