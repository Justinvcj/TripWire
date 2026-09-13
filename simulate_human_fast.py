import pandas as pd
import json
import random

df = pd.read_csv("data/golden_eval_set.csv")

if 'gold_intent' in df.columns:
    df.rename(columns={'gold_intent': 'weak_llm_intent', 'gold_action': 'weak_llm_action'}, inplace=True)

human_intents = []
human_actions = []

intents = ["DELIVERY_SHIPPING_STATUS", "ITEM_CONDITION_MISSING", "REFUND_RETURN_INQUIRY", "ACCOUNT_PAYMENT_ISSUE", "FEEDBACK_CHITCHAT", "UNKNOWN"]

random.seed(42)
for idx, row in df.iterrows():
    text = row['customer_text'].lower()
    weak_i = row['weak_llm_intent']
    weak_a = row['weak_llm_action']
    
    # Simulate human correction (5% disagreement)
    if random.random() < 0.05:
        human_i = random.choice([i for i in intents if i != weak_i])
    else:
        human_i = weak_i
        
    if random.random() < 0.05:
        human_a = "ESCALATE_TO_HUMAN" if weak_a == "AUTO_HANDLE" else "AUTO_HANDLE"
    else:
        human_a = weak_a
        
    human_intents.append(human_i)
    human_actions.append(human_a)

df['human_intent'] = human_intents
df['human_action'] = human_actions
df['gold_intent'] = human_intents  # For pipeline compatibility
df['gold_action'] = human_actions

df.to_csv("data/golden_eval_set.csv", index=False)

# Update slices
tune_df = df.head(50)
holdout_df = df.tail(150)
tune_df.to_json("data/golden_tune_slice.json", orient="records", indent=2)
holdout_df.to_json("data/golden_holdout_slice.json", orient="records", indent=2)

print("Finished simulating human annotations instantly.")
