import json
import random
import os
import pandas as pd
from datasets import load_dataset

def run():
    print("Loading dataset SunidhiSriram/twcs...")
    ds = load_dataset('SunidhiSriram/twcs', split='train')
    
    df = ds.to_pandas()
    
    # create a lookup for all tweets by tweet_id
    # tweet_id is usually a float or int or string depending on parsing. Let's cast to string carefully.
    
    def safe_str(x):
        if pd.isna(x): return None
        try:
            return str(int(float(x)))
        except:
            return str(x)
            
    df['tweet_id_str'] = df['tweet_id'].apply(safe_str)
    df['in_response_to_tweet_id_str'] = df['in_response_to_tweet_id'].apply(safe_str)
    
    lookup = dict(zip(df['tweet_id_str'], df['text']))
    
    amazon_replies = df[(df['author_id'] == 'AmazonHelp') & df['in_response_to_tweet_id_str'].notna()]
    
    pairs = []
    for _, row in amazon_replies.iterrows():
        customer_id = row['in_response_to_tweet_id_str']
        if customer_id in lookup:
            pairs.append({
                'tweet_id': row['tweet_id_str'],
                'customer_text': lookup[customer_id],
                'brand_reply': row['text']
            })
            
    print(f"Found {len(pairs)} AmazonHelp conversations.")
    
    random.seed(42)
    random.shuffle(pairs)
    
    viability_pairs = pairs[:100]
    taxonomy_pairs = pairs[100:500]
    
    os.makedirs('data', exist_ok=True)
    with open('data/viability_sample.json', 'w', encoding='utf-8') as f:
        json.dump(viability_pairs, f, indent=2, ensure_ascii=False)
        
    with open('data/taxonomy_sample.json', 'w', encoding='utf-8') as f:
        json.dump(taxonomy_pairs, f, indent=2, ensure_ascii=False)
        
    print("Wrote viability_sample.json and taxonomy_sample.json")

if __name__ == "__main__":
    run()
