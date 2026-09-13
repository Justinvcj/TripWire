# Tripwire Evaluation Summary

## 1. Classification Metrics (Champion)
- Macro F1: 0.50
- Escalation Precision: 0.00
- Escalation Recall: 0.00

## 2. Retrieval & Grounding
- Average Retrieval Similarity: 0.58

## 3. LLM-as-Judge
- Groundedness (1-5): 3.00
- Actionability (1-5): 3.00
- Tone (1-5): 3.00

## 4. Verifier Tracking
- Passed on first try: 3
- Passed after retry: 0
- Escalated (Verification Failed): 1

## 5. Human Agreement (Cohen's Kappa)
- Groundedness Kappa: 0.00 (based on 1 overlapping graded items)

## 6. Baseline Comparisons
| Metric | Base 1 | Base 2 | Champion |
|---|---|---|---|
| Intent Macro F1 | 0.22 | 1.00 | 0.50 |
| Escalation Prec | 0.00 | 0.00 | 0.00 |
