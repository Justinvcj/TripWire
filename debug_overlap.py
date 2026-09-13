import json
hum_data = json.load(open('data/human_annotations.json'))
ai_scores = {}
with open('data/eval_results_fast.jsonl', 'r') as f:
    for line in f:
        d = json.loads(line)
        scores = d.get('judge_scores', {})
        if scores and scores.get('groundedness') is not None:
            ai_scores[str(d['tweet_id'])] = scores
print("ai_scores len:", len(ai_scores))
