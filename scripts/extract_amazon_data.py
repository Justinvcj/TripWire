import pandas as pd
import json
import random

print("Loading twcs.csv...")
df = pd.read_csv("data/twcs.csv")

amazon_responses = df[df['author_id'] == 'AmazonHelp']
valid_responses = amazon_responses.dropna(subset=['in_response_to_tweet_id'])

# Convert float to int then to str
customer_tweet_ids = valid_responses['in_response_to_tweet_id'].astype('Int64').astype(str).tolist()
df['tweet_id_str'] = df['tweet_id'].astype(str)
customer_tweets = df[df['tweet_id_str'].isin(customer_tweet_ids)]

print(f"Found {len(customer_tweets)} matching customer tweets.")

# Merge to get pairs
merged = pd.merge(customer_tweets, valid_responses, left_on='tweet_id_str', right_on=valid_responses['in_response_to_tweet_id'].astype('Int64').astype(str), suffixes=('_cust', '_amz'))

# Drop duplicates based on customer tweet ID to ensure unique pairs
merged = merged.drop_duplicates(subset=['tweet_id_str'])

pairs = []
for _, row in merged.iterrows():
    pairs.append({
        "tweet_id": str(row['tweet_id_cust']),
        "customer_text": str(row['text_cust']),
        "gold_reference_reply": str(row['text_amz'])
    })

print(f"Total valid conversational pairs after deduplication: {len(pairs)}")

random.seed(42)
random.shuffle(pairs)

historical = pairs[:2000]
with open("data/historical_pairs.json", "w", encoding="utf-8") as f:
    json.dump(historical, f, indent=2)

to_label = pairs[2000:2200]
with open("data/unlabeled_golden_set.json", "w", encoding="utf-8") as f:
    json.dump(to_label, f, indent=2)

print("Saved deduplicated data.")
