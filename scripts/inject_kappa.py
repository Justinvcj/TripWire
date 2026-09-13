import json
from sklearn.metrics import cohen_kappa_score

def fix_kappa():
    with open("evaluation/run_eval.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    replacement = """
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
"""
    
    import re
    new_content = re.sub(
        r"# Check human annotations.*?(?=report_md = f)",
        replacement,
        content,
        flags=re.DOTALL
    )
    
    with open("evaluation/run_eval.py", "w", encoding="utf-8") as f:
        f.write(new_content)

fix_kappa()
