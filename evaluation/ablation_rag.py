import json
import os
from src.config import settings
from src.pipeline import Pipeline
from src.judge import LLMJudge

def run_ablation():
    print("Running RAG Ablation (k=3 vs k=0)")
    with open(settings.holdout_slice_path, "r", encoding="utf-8-sig") as f:
        holdout = json.load(f)[:50]
        
    pipeline = Pipeline()
    judge = LLMJudge()
    
    delta_g = []
    
    for i, item in enumerate(holdout):
        print(f"Ablating {i+1}/50...")
        try:
            # Run k=3
            res_k3 = pipeline.process_ticket(item['tweet_id'], item['customer_text'])
            g_k3 = 3
            if res_k3.draft_reply:
                js = judge.evaluate_reply(item['customer_text'], res_k3.draft_reply, item.get('gold_reference_reply', ''))
                g_k3 = js.get("groundedness", 3)
                
            # Temporarily set k=0
            old_k = settings.retrieval_k
            settings.retrieval_k = 0
            res_k0 = pipeline.process_ticket(item['tweet_id'], item['customer_text'])
            g_k0 = 3
            if res_k0.draft_reply:
                js = judge.evaluate_reply(item['customer_text'], res_k0.draft_reply, item.get('gold_reference_reply', ''))
                g_k0 = js.get("groundedness", 3)
            settings.retrieval_k = old_k
            
            delta = g_k3 - g_k0
            delta_g.append(delta)
        except Exception as e:
            print("Error during ablation:", e)
            
    avg_delta = sum(delta_g)/len(delta_g) if delta_g else 0
    print(f"RAG Ablation Delta (k=3 vs k=0) Groundedness: +{avg_delta:.2f}")
    
    with open("evaluation/results/ablation.txt", "w") as f:
        f.write(f"Average Groundedness Delta: +{avg_delta:.2f}\n")

if __name__ == "__main__":
    run_ablation()
