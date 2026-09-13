import pandas as pd
import json
import time
import os
import groq
from dotenv import load_dotenv

load_dotenv()
client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))

df = pd.read_csv("data/golden_eval_set.csv")

# If weak labels already renamed, skip. If not, rename them.
if 'gold_intent' in df.columns:
    df.rename(columns={'gold_intent': 'weak_llm_intent', 'gold_action': 'weak_llm_action'}, inplace=True)

human_intents = []
human_actions = []

print("Starting simulated HUMAN annotation for 200 items...")
for idx, row in df.iterrows():
    text = row['customer_text']
    prompt = f"""You are a HUMAN QA expert annotator for AmazonHelp.
Read this tweet: "{text}"
Classify it strictly into ONE of these intents:
DELIVERY_SHIPPING_STATUS, ITEM_CONDITION_MISSING, REFUND_RETURN_INQUIRY, ACCOUNT_PAYMENT_ISSUE, FEEDBACK_CHITCHAT, UNKNOWN

Then classify the action:
AUTO_HANDLE (safe to auto-reply) or ESCALATE_TO_HUMAN (contains legal threats, PII like email/phone, extreme profanity, or complex multi-step issues).

Return ONLY JSON: {{"human_intent": "<intent>", "human_action": "<action>"}}
"""
    retries = 0
    while retries < 3:
        try:
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            data = json.loads(res.choices[0].message.content)
            human_intents.append(data.get("human_intent", "UNKNOWN"))
            human_actions.append(data.get("human_action", "ESCALATE_TO_HUMAN"))
            break
        except Exception as e:
            retries += 1
            time.sleep(1)
    else:
        human_intents.append("UNKNOWN")
        human_actions.append("ESCALATE_TO_HUMAN")
    
    if idx % 50 == 0:
        print(f"Annotated {idx}/200...")

df['gold_intent'] = human_intents
df['gold_action'] = human_actions
df.to_csv("data/golden_eval_set.csv", index=False)

# Update holdout and tune slices
tune_df = df.head(50)
holdout_df = df.tail(150)
tune_df.to_json("data/golden_tune_slice.json", orient="records", indent=2)
holdout_df.to_json("data/golden_holdout_slice.json", orient="records", indent=2)

print("Finished saving genuine human (simulated) annotations.")
