import json
import random
import os
import pandas as pd
from datasets import load_dataset

def run():
    print("Loading dataset...")
    ds = load_dataset('gorkemsevinc/Customer_Support_on_Twitter', split='train')
    
    df = ds.to_pandas()
    
    print("Filtering for AmazonHelp pairs...")
    amazon_replies = df[df['author_id'] == 'AmazonHelp'].dropna(subset=['in_response_to_tweet_id'])
    
    df_customers = df[['tweet_id', 'text', 'author_id']].rename(columns={
        'tweet_id': 'in_response_to_tweet_id',
        'text': 'customer_text',
        'author_id': 'customer_author'
    })
    
    merged = pd.merge(amazon_replies, df_customers, on='in_response_to_tweet_id', how='inner')
    print(f"Found {len(merged)} AmazonHelp conversations.")
    
    # For Viability Check (100 pairs)
    sampled_viability = merged.sample(n=min(100, len(merged)), random_state=42)
    viability_pairs = []
    for _, row in sampled_viability.iterrows():
        viability_pairs.append({
            'tweet_id': row['tweet_id'],
            'customer_text': row['customer_text'],
            'brand_reply': row['text']
        })
        
    os.makedirs('data', exist_ok=True)
    with open('data/viability_sample.json', 'w', encoding='utf-8') as f:
        json.dump(viability_pairs, f, indent=2, ensure_ascii=False)
        
    # For Taxonomy Discovery (400 pairs)
    sampled_taxonomy = merged.sample(n=min(400, len(merged)), random_state=123)
    taxonomy_pairs = []
    for _, row in sampled_taxonomy.iterrows():
        taxonomy_pairs.append({
            'tweet_id': row['tweet_id'],
            'customer_text': row['customer_text']
        })
        
    with open('data/taxonomy_sample.json', 'w', encoding='utf-8') as f:
        json.dump(taxonomy_pairs, f, indent=2, ensure_ascii=False)
        
    print("Wrote viability_sample.json and taxonomy_sample.json")

if __name__ == "__main__":
    run()
