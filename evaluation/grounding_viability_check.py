import json
import random
from datasets import load_dataset

def run():
    print("Loading dataset...")
    # Load dataset
    ds = load_dataset('gorkemsevinc/Customer_Support_on_Twitter', split='train')
    print(f"Total rows: {len(ds)}")
    
    # Filter for AmazonHelp tweets that are replies to customers
    # We want pairs of (customer_msg, brand_reply)
    # The dataset schema usually has: tweet_id, author_id, inbound, created_at, text, response_tweet_id, in_response_to_tweet_id
    
    # Let's extract a sample to examine the structure
    # Since dataset is huge, let's stream it or just grab a chunk
    pass

if __name__ == "__main__":
    run()
