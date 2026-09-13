import json
import pandas as pd
from evaluation.run_eval import generate_report

with open("data/golden_holdout_slice.json", "r", encoding="utf-8") as f:
    holdout = json.load(f)

holdout_dict = {str(item["tweet_id"]): item for item in holdout}

fixed_results = []
with open("data/eval_results.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        t_id = str(data["tweet_id"])
        if t_id in holdout_dict:
            data["gold_intent"] = holdout_dict[t_id]["gold_intent"]
            data["gold_action"] = holdout_dict[t_id]["gold_action"]
        fixed_results.append(data)

with open("data/eval_results.jsonl", "w", encoding="utf-8") as f:
    for data in fixed_results:
        f.write(json.dumps(data) + "\n")

generate_report("data/eval_results.jsonl", holdout)
print("Successfully patched eval_results.jsonl and regenerated report_summary.md")
