import json
import time
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

with open("data/unlabeled_golden_set.json", "r", encoding="utf-8") as f:
    unlabeled = json.load(f)

labeled = []

prompt_template = """
You are a data labeler for an Amazon customer support AI.
You are given a customer tweet.
Label it with one of these intents:
- DELIVERY_SHIPPING_STATUS
- REFUND_CANCELLATION_BILLING
- WRONG_OR_DEFECTIVE_ITEM
- NON_ENGLISH_QUERY
- FEEDBACK_CHITCHAT

And one of these actions:
- AUTO_HANDLE (Safe to use a bot)
- ESCALATE_TO_HUMAN (If the query mentions legal action, PII requests, or is extremely angry/complex)

Customer Tweet: "{tweet}"

Output exactly in JSON format and nothing else.
{{
  "gold_intent": "<intent>",
  "gold_action": "<action>"
}}
"""

print(f"Labeling {len(unlabeled)} tweets using Groq (openai/gpt-oss-120b)...")

for i, item in enumerate(unlabeled):
    if i % 20 == 0:
        print(f"Progress: {i}/{len(unlabeled)}")
    
    try:
        res = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt_template.replace("{tweet}", item['customer_text'])}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        labels = json.loads(res.choices[0].message.content)
        item["gold_intent"] = labels.get("gold_intent", "DELIVERY_SHIPPING_STATUS")
        item["gold_action"] = labels.get("gold_action", "AUTO_HANDLE")
        labeled.append(item)
    except Exception as e:
        print("Error:", e)
        item["gold_intent"] = "DELIVERY_SHIPPING_STATUS"
        item["gold_action"] = "AUTO_HANDLE"
        labeled.append(item)
            
    time.sleep(0.1) # Groq pacing

with open("data/golden_eval_set.json", "w", encoding="utf-8") as f:
    json.dump(labeled, f, indent=2)

tune = labeled[:50]
holdout = labeled[50:]

with open("data/golden_tune_slice.json", "w", encoding="utf-8") as f:
    json.dump(tune, f, indent=2)
    
with open("data/golden_holdout_slice.json", "w", encoding="utf-8") as f:
    json.dump(holdout, f, indent=2)
    
human_stub = []
for h in holdout[:50]:
    human_stub.append({
        "tweet_id": h["tweet_id"],
        "customer_text": h["customer_text"],
        "draft_reply_to_judge": h["gold_reference_reply"], 
        "human_groundedness": None,
        "human_actionability": None,
        "human_tone": None
    })

with open("data/human_annotations.json", "w", encoding="utf-8") as f:
    json.dump(human_stub, f, indent=2)
    
print("Labeling complete!")
