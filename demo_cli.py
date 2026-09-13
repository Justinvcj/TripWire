import sys
import argparse
from src.pipeline import Pipeline

def main():
    parser = argparse.ArgumentParser(description="Tripwire Interactive CLI")
    parser.add_argument("--tweet", type=str, help="Customer tweet to process")
    args = parser.parse_args()

    print("\n[System] Initializing Tripwire Pipeline...")
    try:
        pipeline = Pipeline()
    except Exception as e:
        print(f"[Error] Failed to initialize pipeline: {e}")
        sys.exit(1)

    if args.tweet:
        text = args.tweet
    else:
        print("\n" + "="*50)
        text = input("Enter a customer tweet (or 'exit' to quit):\n> ")
        if text.lower().strip() in ['exit', 'quit']:
            sys.exit(0)

    print("\n[Agent Processing...]")
    try:
        result = pipeline.process_ticket(tweet_id="CLI_DEMO", raw_text=text)
        
        print(f"?? Intent: {result.intent}")
        print(f"?? Action: {result.action}")
        print(f"?? Confidence: {result.intent_confidence}")
        print(f"?? Reason: {result.escalation_reason}")
        
        print("\n[Retrieving Context...]")
        if result.retrieved_docs:
            print(f"?? RAG Match: {result.retrieved_docs[0][:150]}...")
        else:
            print("?? RAG Match: None found.")
            
        print("\n[Drafting Reply...]")
        print(f"?? Output: {result.draft_reply}")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"[Error] Pipeline execution failed: {e}")

if __name__ == "__main__":
    main()
