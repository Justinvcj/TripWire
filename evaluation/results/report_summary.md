# Tripwire Evaluation Summary

## 1. Classification Metrics (Champion)
- Macro F1: 0.50
- Escalation Precision: 0.20
- Escalation Recall: 1.00

## 2. Routing Cost Optimization (Lower is Better)
*Cost weights: False Auto-Handle = 5, False Escalation = 1*
| System | Total Expected Cost |
|---|---|
| Baseline 1 (Majority) | 2 |
| Baseline 2 (TF-IDF) | 5 |
| **TripWire Champion** | **4** |

## 3. Retrieval & Grounding
- Average Retrieval Similarity: 0.58

## 4. LLM-as-Judge
- Groundedness (1-5): 3.00
- Actionability (1-5): 3.00
- Tone (1-5): 3.00

## 5. Verifier Tracking
- Passed on first try: 3
- Passed after retry: 0
- Escalated (Verification Failed): 2

## 6. Human Agreement (Cohen's Kappa)
- Groundedness Kappa: 0.00 (based on 2 overlapping graded items)

## 7. Baseline Comparisons
| Metric | Base 1 | Base 2 | Champion |
|---|---|---|---|
| Intent Macro F1 | 0.25 | 0.25 | 0.50 |
| Escalation Prec | 0.33 | 0.00 | 0.20 |

## 8. Per-Intent F1 Classification Report
```text
                             precision    recall  f1-score   support

   DELIVERY_SHIPPING_STATUS       0.00      0.00      0.00         3
          FEEDBACK_CHITCHAT       1.00      1.00      1.00         1
          NON_ENGLISH_QUERY       0.00      0.00      0.00         0
REFUND_CANCELLATION_BILLING       1.00      1.00      1.00         1

                   accuracy                           0.40         5
                  macro avg       0.50      0.50      0.50         5
               weighted avg       0.40      0.40      0.40         5

```

## 9. Confusion Matrix
|                             |   DELIVERY_SHIPPING_STATUS |   FEEDBACK_CHITCHAT |   NON_ENGLISH_QUERY |   REFUND_CANCELLATION_BILLING |
|:----------------------------|---------------------------:|--------------------:|--------------------:|------------------------------:|
| DELIVERY_SHIPPING_STATUS    |                          0 |                   0 |                   3 |                             0 |
| FEEDBACK_CHITCHAT           |                          0 |                   1 |                   0 |                             0 |
| NON_ENGLISH_QUERY           |                          0 |                   0 |                   0 |                             0 |
| REFUND_CANCELLATION_BILLING |                          0 |                   0 |                   0 |                             1 |
