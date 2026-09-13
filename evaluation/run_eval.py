import json
import time
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score
from src.config import settings
from src.pipeline import Pipeline
from src.judge import LLMJudge
from src.schemas import Intent, Action

def run():
    print("Running Evaluation Harness on Holdout Slice (with rate-limit throttling)...")
    with open(settings.holdout_slice_path, "r", encoding="utf-8-sig") as f:
        holdout = json.load(f)
        
    print(f"Loaded {len(holdout)} examples from {settings.holdout_slice_path}")
    
    pipeline = Pipeline()
    judge = LLMJudge()
    
    y_true_intent = []
    y_pred_intent = []
    
    y_true_escalation = []
    y_pred_escalation = []
    
    judge_scores = []
    
    for i, item in enumerate(holdout):
        print(f"Evaluating {i+1}/{len(holdout)}...")
        try:
            res = pipeline.process_ticket(item['tweet_id'], item['customer_text'])
            
            y_true_intent.append(item['gold_intent'])
            y_pred_intent.append(res.intent.value)
            
            y_true_escalation.append(1 if item['gold_action'] == "ESCALATE_TO_HUMAN" else 0)
            y_pred_escalation.append(1 if res.action.value == "ESCALATE_TO_HUMAN" else 0)
            
            if res.action.value == "AUTO_HANDLE" and res.draft_reply:
                eval_res = judge.evaluate_reply(item['customer_text'], res.draft_reply, item.get('gold_reference_reply', ''))
                judge_scores.append(eval_res.get('score', 3))
                
        except Exception as e:
            print(f"Error processing {item['tweet_id']}: {e}")
            continue
            
        # Throttling to respect Free Tier API Limits (Groq TPM and Gemini RPM)
        print("Sleeping for 5 seconds to avoid API Rate Limits (429 errors)...")
        time.sleep(5)
            
    intent_acc = accuracy_score(y_true_intent, y_pred_intent) if y_true_intent else 0
    esc_prec = precision_score(y_true_escalation, y_pred_escalation, zero_division=0) if y_true_escalation else 0
    esc_rec = recall_score(y_true_escalation, y_pred_escalation, zero_division=0) if y_true_escalation else 0
    avg_score = sum(judge_scores) / len(judge_scores) if judge_scores else 0
    
    print("\n" + "="*40)
    print("FINAL METRICS")
    print("="*40)
    print(f"Intent Classification Accuracy: {intent_acc:.2%}")
    print(f"Escalation Precision: {esc_prec:.2%}")
    print(f"Escalation Recall: {esc_rec:.2%}")
    
    print("\nLLM-as-judge evaluation:")
    print("Model used:", settings.judge_model)
    print(f"Average Reply Quality Score (1-5): {avg_score:.2f}")

if __name__ == "__main__":
    run()
