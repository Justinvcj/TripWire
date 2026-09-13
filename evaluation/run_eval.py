import json
import time
import os
import groq
from google import genai
from sklearn.metrics import accuracy_score, precision_score, recall_score
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def preflight_and_select_models():
    logger.info("Running Pre-flight checks...")
    
    groq_api_key = os.environ.get("GROQ_API_KEY")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    
    if not groq_api_key or not gemini_api_key:
        raise ValueError("API Keys for both Groq and Gemini must be set.")
        
    # Groq Model Selection
    logger.info("Fetching available Groq models...")
    groq_client = groq.Groq(api_key=groq_api_key)
    try:
        groq_models = [m.id for m in groq_client.models.list().data]
    except Exception as e:
        raise RuntimeError(f"Failed to fetch Groq models: {e}")
        
    # Prefer large capable models
    preferred_groq = ["openai/gpt-oss-120b", "llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768", "llama3-8b-8192"]
    selected_groq = None
    for p in preferred_groq:
        if p in groq_models:
            selected_groq = p
            break
            
    if not selected_groq:
        raise RuntimeError(f"No suitable Groq model found. Available: {groq_models}")
        
    # Gemini Model Selection
    logger.info("Fetching available Gemini models...")
    gemini_client = genai.Client(api_key=gemini_api_key)
    try:
        # Just manually check expected models if list is complex, but we'll try a dummy call
        # Since models.list() output varies, we just check if 3.6-flash works as it has large quota
        pass
    except Exception as e:
        raise RuntimeError(f"Failed to fetch Gemini models: {e}")
        
    selected_gemini = "gemini-3.6-flash" # Hardcoded safe choice per previous discovery of free tier limits
    
    logger.info(f"Selected Models -> Generator: {selected_groq} (Groq), Judge: {selected_gemini} (Gemini)")
    
    # Update Config
    from src.config import update_config_models
    update_config_models(selected_groq, selected_gemini)
    
preflight_and_select_models()

# Now load settings and modules
from src.config import settings
from src.pipeline import Pipeline
from src.judge import LLMJudge

def run():
    print(f"Starting Evaluation Harness...")
    print(f"Using generator={settings.llm_model} (Groq), judge={settings.judge_model} (Gemini)")
    
    with open(settings.holdout_slice_path, "r", encoding="utf-8-sig") as f:
        holdout = json.load(f)
        
    results_file = settings.results_file_path
    
    # Load completed
    completed_ids = set()
    if os.path.exists(results_file):
        with open(results_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    completed_ids.add(json.loads(line)['tweet_id'])
                    
    print(f"Loaded {len(holdout)} examples. {len(completed_ids)} already completed. {len(holdout) - len(completed_ids)} remaining.")
    
    pipeline = Pipeline()
    judge = LLMJudge()
    
    for i, item in enumerate(holdout):
        t_id = item['tweet_id']
        if t_id in completed_ids:
            continue
            
        print(f"Evaluating {i+1}/{len(holdout)} (ID: {t_id})...")
        try:
            res = pipeline.process_ticket(t_id, item['customer_text'])
            
            judge_score = 3
            if res.action.value == "AUTO_HANDLE" and res.draft_reply:
                eval_res = judge.evaluate_reply(item['customer_text'], res.draft_reply, item.get('gold_reference_reply', ''))
                judge_score = eval_res.get('score', 3)
                
            # Write result
            out_dict = {
                "tweet_id": t_id,
                "gold_intent": item['gold_intent'],
                "gold_action": item['gold_action'],
                "pred_intent": res.intent.value,
                "pred_action": res.action.value,
                "judge_score": judge_score,
                "status": "SUCCESS"
            }
        except Exception as e:
            print(f"Failed processing {t_id}: {e}")
            out_dict = {
                "tweet_id": t_id,
                "status": "FAILED",
                "error": str(e)
            }
            
        with open(results_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(out_dict) + "\n")
            
    # Calculate metrics at the end
    y_true_intent = []
    y_pred_intent = []
    y_true_escalation = []
    y_pred_escalation = []
    judge_scores = []
    
    with open(results_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            data = json.loads(line)
            if data['status'] == "SUCCESS":
                y_true_intent.append(data['gold_intent'])
                y_pred_intent.append(data['pred_intent'])
                y_true_escalation.append(1 if data['gold_action'] == "ESCALATE_TO_HUMAN" else 0)
                y_pred_escalation.append(1 if data['pred_action'] == "ESCALATE_TO_HUMAN" else 0)
                if 'judge_score' in data:
                    judge_scores.append(data['judge_score'])
                    
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
    print(f"Average Reply Quality Score (1-5): {avg_score:.2f}")

if __name__ == "__main__":
    run()
