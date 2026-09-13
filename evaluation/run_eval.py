import json
import time
import os
import argparse
import sys
import groq
from google import genai
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix
from sklearn.metrics import cohen_kappa_score
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Part 5: Assertions
from src.config import settings
assert "holdout" in settings.holdout_slice_path.lower(), "run_eval.py must only read the holdout slice to prevent data contamination."

def preflight_and_select_models(fast_path=False):
    logger.info("Running Pre-flight checks...")
    
    groq_api_key = os.environ.get("GROQ_API_KEY")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    
    if not groq_api_key or not gemini_api_key:
        raise ValueError("API Keys for both Groq and Gemini must be set.")
        
    groq_client = groq.Groq(api_key=groq_api_key)
    try:
        groq_models = [m.id for m in groq_client.models.list().data]
    except Exception as e:
        raise RuntimeError(f"Failed to fetch Groq models: {e}")
        
    preferred_groq = ["openai/gpt-oss-120b", "llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768", "llama3-8b-8192"]
    selected_groq = next((p for p in preferred_groq if p in groq_models), None)
            
    if not selected_groq:
        raise RuntimeError(f"No suitable Groq model found. Available: {groq_models}")
        
    gemini_client = genai.Client(api_key=gemini_api_key)
    
    selected_gemini = "gemini-3.6-flash"
    try:
        gemini_client.models.generate_content(
            model=selected_gemini,
            contents="Test"
        )
    except Exception as e:
        if "404" in str(e):
            selected_gemini = "gemini-3.6-flash"
            
    assert "gemini" in selected_gemini and "groq" not in selected_gemini, "Judge must be different provider!"
    
    n_items = 40 if fast_path else 150
    calls_per_item = 3
    total_calls = n_items * calls_per_item
    est_time = (total_calls * (60 / (settings.groq_rpm_limit * 0.8))) / 60
    
    print("\n" + "="*60)
    print("PRE-FLIGHT SUMMARY")
    print(f"Generator: {selected_groq} (Groq) | Judge: {selected_gemini} (Gemini)")
    print(f"Items to process: {n_items}")
    print(f"Est. calls needed: {total_calls}")
    print(f"Est. runtime at current pacing: ~{est_time:.1f} minutes")
    print("="*60 + "\n")
    
    from src.config import update_config_models
    update_config_models(selected_groq, selected_gemini)

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fast", action="store_true", help="Run 40-item fast path")
    args = parser.parse_args()
    
    preflight_and_select_models(fast_path=args.fast)
    
    from src.config import settings
    from src.pipeline import Pipeline
    from src.judge import LLMJudge
    from src.baseline import SimpleBaselineClassifier
    
    with open(settings.holdout_slice_path, "r", encoding="utf-8-sig") as f:
        holdout = json.load(f)
        
    if args.fast:
        holdout = holdout[:40]
        
    os.makedirs("evaluation/results", exist_ok=True)
    results_file = settings.results_file_path if not args.fast else settings.results_file_path.replace(".jsonl", "_fast.jsonl")
    
    completed_ids = set()
    if os.path.exists(results_file):
        with open(results_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    completed_ids.add(json.loads(line)['tweet_id'])
                    
    print(f"Loaded {len(holdout)} examples. {len(completed_ids)} already completed.")
    
    pipeline = Pipeline()
    judge = LLMJudge()
    
    try:
        b2_classifier = SimpleBaselineClassifier("data/golden_eval_set.csv")
    except:
        b2_classifier = None
    
    for i, item in enumerate(holdout):
        t_id = item['tweet_id']
        if t_id in completed_ids:
            continue
            
        print(f"Evaluating {i+1}/{len(holdout)} (ID: {t_id})...")
        try:
            b1_intent = "DELIVERY_SHIPPING_STATUS"
            b1_action = "ESCALATE_TO_HUMAN" if len(item['customer_text']) > 140 else "AUTO_HANDLE"
            
            if b2_classifier:
                b2_intent = b2_classifier.predict(item['customer_text']).value
            else:
                b2_intent = "DELIVERY_SHIPPING_STATUS"
            b2_action = "ESCALATE_TO_HUMAN" if "lawsuit" in item['customer_text'].lower() else "AUTO_HANDLE"
            
            res = pipeline.process_ticket(t_id, item['customer_text'])
            
            judge_scores = {"groundedness": 3, "actionability": 3, "tone": 3}
            if res.action.value == "AUTO_HANDLE" and res.draft_reply:
                judge_scores = judge.evaluate_reply(item['customer_text'], res.draft_reply, item.get('gold_reference_reply', ''))
                
            out_dict = {
                "tweet_id": t_id,
                "gold_intent": item['gold_intent'],
                "gold_action": item['gold_action'],
                "b1_intent": b1_intent,
                "b1_action": b1_action,
                "b2_intent": b2_intent,
                "b2_action": b2_action,
                "champ_intent": res.intent.value,
                "champ_action": res.action.value,
                "champ_confidence": res.intent_confidence,
                "verifier_retries": res.verifier_retries,
                "retrieval_scores": res.retrieval_scores,
                "judge_scores": judge_scores,
                "status": "SUCCESS"
            }
        except Exception as e:
            logger.error(f"Failed processing {t_id}: {e}")
            out_dict = {
                "tweet_id": t_id,
                "status": "FAILED",
                "error": str(e)
            }
            
        with open(results_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(out_dict) + "\n")
            
    generate_report(results_file, holdout)

def generate_report(results_file, holdout_data):
    from src.config import settings
    
    if not os.path.exists(settings.human_annotations_path):
        with open(settings.human_annotations_path, "w", encoding="utf-8") as f:
            template = [{"tweet_id": h['tweet_id'], "human_groundedness": None} for h in holdout_data[:50]]
            json.dump(template, f, indent=2)
        print(f"Generated human annotation template at {settings.human_annotations_path}")
            
    y_true_intent, y_pred_intent = [], []
    y_true_esc, y_pred_esc = [], []
    y_b1_intent, y_b2_intent = [], []
    y_b1_esc, y_b2_esc = [], []
    
    g_scores, a_scores, t_scores = [], [], []
    verifier_passes, verifier_retries, verifier_fails = 0, 0, 0
    sim_scores = []
    
    with open(results_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            data = json.loads(line)
            if data['status'] == "SUCCESS":
                y_true_intent.append(data['gold_intent'])
                y_pred_intent.append(data['champ_intent'])
                y_b1_intent.append(data['b1_intent'])
                y_b2_intent.append(data['b2_intent'])
                
                y_true_esc.append(1 if data['gold_action'] == "ESCALATE_TO_HUMAN" else 0)
                y_pred_esc.append(1 if data['champ_action'] == "ESCALATE_TO_HUMAN" else 0)
                y_b1_esc.append(1 if data['b1_action'] == "ESCALATE_TO_HUMAN" else 0)
                y_b2_esc.append(1 if data['b2_action'] == "ESCALATE_TO_HUMAN" else 0)
                
                js = data.get('judge_scores', {})
                if 'groundedness' in js:
                    g_scores.append(js['groundedness'])
                    a_scores.append(js['actionability'])
                    t_scores.append(js['tone'])
                    
                vr = data.get('verifier_retries', 0)
                if data['champ_action'] == "ESCALATE_TO_HUMAN" and vr >= settings.max_verifier_retries:
                    verifier_fails += 1
                elif vr == 0:
                    verifier_passes += 1
                else:
                    verifier_retries += 1
                    
                sim_scores.extend(data.get('retrieval_scores', []))
                
    if not y_true_intent:
        print("No successful results found.")
        return

    f1 = f1_score(y_true_intent, y_pred_intent, average='macro', zero_division=0)
    prec_esc = precision_score(y_true_esc, y_pred_esc, zero_division=0)
    rec_esc = recall_score(y_true_esc, y_pred_esc, zero_division=0)
    
    f1_b1 = f1_score(y_true_intent, y_b1_intent, average='macro', zero_division=0)
    prec_b1 = precision_score(y_true_esc, y_b1_esc, zero_division=0)
    
    f1_b2 = f1_score(y_true_intent, y_b2_intent, average='macro', zero_division=0)
    prec_b2 = precision_score(y_true_esc, y_b2_esc, zero_division=0)
    
    avg_g = sum(g_scores)/len(g_scores) if g_scores else 0
    avg_a = sum(a_scores)/len(a_scores) if a_scores else 0
    avg_t = sum(t_scores)/len(t_scores) if t_scores else 0
    
    avg_sim = sum(sim_scores)/len(sim_scores) if sim_scores else 0
    
    
    
    
    
    # Check human annotations
    kappa_msg = "- AWAITING HUMAN LABELS. Please populate `data/human_annotations.json` with 50 scored examples."
    try:
        with open(settings.human_annotations_path, "r", encoding="utf-8") as f:
            hum_data = json.load(f)
            
        ai_scores = {}
        target_path = results_file
        if os.path.exists(target_path):
            with open(target_path, "r", encoding="utf-8") as f:
                for line in f:
                    d = json.loads(line)
                    scores = d.get("judge_scores", {})
                    if scores and scores.get("groundedness") is not None:
                        ai_scores[d["tweet_id"]] = scores
                    
            h_arr = []
            a_arr = []
            
            for h in hum_data:
                tid = h["tweet_id"]
                if h.get("human_groundedness") is not None and h.get("human_groundedness") > 0:
                    if tid in ai_scores and ai_scores[tid].get("groundedness") is not None:
                        h_arr.append(h["human_groundedness"])
                        a_arr.append(round(ai_scores[tid]["groundedness"]))
                        
            if len(h_arr) > 0:
                k = cohen_kappa_score(h_arr, a_arr)
                kappa_msg = f"- Groundedness Kappa: {k:.2f} (based on {len(h_arr)} overlapping graded items)"
    except Exception as e:
        print("Kappa computation error:", e)
        pass
    report_md = f"""# Tripwire Evaluation Summary

## 1. Classification Metrics (Champion)
- Macro F1: {f1:.2f}
- Escalation Precision: {prec_esc:.2f}
- Escalation Recall: {rec_esc:.2f}

## 2. Retrieval & Grounding
- Average Retrieval Similarity: {avg_sim:.2f}

## 3. LLM-as-Judge
- Groundedness (1-5): {avg_g:.2f}
- Actionability (1-5): {avg_a:.2f}
- Tone (1-5): {avg_t:.2f}

## 4. Verifier Tracking
- Passed on first try: {verifier_passes}
- Passed after retry: {verifier_retries}
- Escalated (Verification Failed): {verifier_fails}

## 5. Human Agreement (Cohen's Kappa)
{kappa_msg}

## 6. Baseline Comparisons
| Metric | Base 1 | Base 2 | Champion |
|---|---|---|---|
| Intent Macro F1 | {f1_b1:.2f} | {f1_b2:.2f} | {f1:.2f} |
| Escalation Prec | {prec_b1:.2f} | {prec_b2:.2f} | {prec_esc:.2f} |
"""

    with open("evaluation/results/report_summary.md", "w", encoding="utf-8") as f:
        f.write(report_md)
        
    print("\nEvaluation complete. Report generated at evaluation/results/report_summary.md")

if __name__ == "__main__":
    run()
