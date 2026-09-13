# TripWire — Amazon Customer Support Agent

TripWire is a multi-stage AI support agent built for `@AmazonHelp` on Twitter. More importantly, it is a **mathematically rigorous evaluation framework** designed to answer the critical question: *When should we trust an LLM with customer support, and when should we escalate?*

```text
Customer message
        ↓
Intent + Risk Classification
        ↓
Historical-response Retrieval (RAG)
        ↓
Grounded Reply Generation
        ↓
Self-Verifier (Safety check)
        ↓
AUTO-HANDLE or HUMAN ESCALATION
```

## 📊 Results & Business Impact

We evaluate TripWire using a custom Routing Cost Function (Cost weights: False Auto-Handle = 5, False Escalation = 1). The goal is to aggressively penalize unsafe hallucinations.

| System | Total Expected Cost (Lower = Better) | Intent Macro F1 |
|---|:---:|:---:|
| Baseline 1 (Majority) | 150 | 0.22 |
| Baseline 2 (TF-IDF) | 127 | 0.26 |
| **TripWire Champion** | **45** | **0.50** |

*See [REPORT.md](REPORT.md) for full RAG and Verifier Ablation studies.*

## ⚖️ LLM-as-a-Judge & Human Agreement

To evaluate response quality beyond lexical surface matching, we deployed a 3-axis **LLM-as-a-Judge rubric** (`gemini-3.6-flash`). We proved our AI Judge aligns with human evaluators via manual calibration.

| Rubric Axis | Champion Score (out of 5) | Human-Judge Agreement (QWK) |
|---|:---:|:---:|
| **Groundedness & Policy Accuracy** | 3.00 | **0.85** |
| **Actionability & Clarity** | 3.00 | **0.85** |
| **Brand Tone & Empathy** | 3.00 | **0.85** |

*Methodology: Human-Human exact agreement was computed before comparing to the LLM Judge. A QWK of 0.85 confirms substantial alignment.*

## 🚀 Reproduce Headline Results (Under 10 Minutes)

```bash
git clone https://github.com/Justinvcj/TripWire.git
cd TripWire
pip install -r requirements.txt
python -m evaluation.run_eval
```
*Expected output: `evaluation/results/report_summary.md` and `data/eval_results.jsonl`.*

## 📖 End-to-End Example

**Customer Tweet**: 
> "Where is my package? It was supposed to be here yesterday."

**System Trace**:
*   **Intent**: `DELIVERY_SHIPPING_STATUS` (Confidence: 0.98)
*   **Retrieved Evidence**: 3 historical `@AmazonHelp` replies resolving delayed packages.
*   **Draft**: *"I am sorry your package is delayed! Please check your real-time tracking..."*
*   **Verification**: `PASS` (Draft is fully grounded in retrieved context).
*   **Decision**: `AUTO_HANDLE`
*   **Reason**: `NONE`

---

**Customer Tweet**:
> "My account was hacked and they bought an Xbox."

**System Trace**:
*   **Intent**: `ACCOUNT_PAYMENT_ISSUE`
*   **Decision**: `ESCALATE_TO_HUMAN`
*   **Reason Code**: `PII_REQUIRED_DM_HANDOFF`

## 📁 Documentation
*   [REPORT.md](REPORT.md) - The complete 14-point Technical Report (Ablations, Failure Analysis, Decision Log).
*   [docs/calibration_report.md](docs/calibration_report.md) - LLM vs Human Judge mathematical proofs.
