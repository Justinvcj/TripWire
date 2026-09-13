import json

data = []
for i in range(50):
    data.append({
        "tweet_id": f"tune_{i}",
        "customer_text": f"Where is my package? {i}",
        "gold_intent": "DELIVERY_SHIPPING_STATUS",
        "gold_action": "AUTO_HANDLE",
        "gold_escalation_reason": "NONE",
        "gold_reference_reply": "Your package is on its way."
    })
with open("data/golden_tune_slice.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

data_holdout = []
for i in range(150):
    data_holdout.append({
        "tweet_id": f"holdout_{i}",
        "customer_text": f"Broken item {i}",
        "gold_intent": "WRONG_OR_DEFECTIVE_ITEM",
        "gold_action": "ESCALATE_TO_HUMAN",
        "gold_escalation_reason": "VERIFICATION_FAILED",
        "gold_reference_reply": "Please DM us for a replacement."
    })
with open("data/golden_holdout_slice.json", "w", encoding="utf-8") as f:
    json.dump(data_holdout, f, indent=2)
