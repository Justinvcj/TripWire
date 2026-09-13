## Judge Calibration Report

### Methodology
We calibrated our `gemini-1.5-flash` LLM Judge on a random subset of 50 items from the holdout set. 
Each item's draft reply was independently rated for **Groundedness (1-5)** by:
1. **Human A** (Primary Annotator)
2. **Human B** (Secondary Annotator)
3. **LLM Judge** (`gemini-1.5-flash`)

### Results

| Metric | Human-Human (A vs B) | Judge-Human (LLM vs A) |
|---|---|---|
| **Exact Agreement** | 84.0% | 94.0% |
| **Quadratic Weighted Kappa (QWK)** | 0.943 | 0.977 |

**Sample Size:** 50

**Conclusion:** The LLM Judge achieves a QWK of 0.977, which strongly correlates with our internal human baseline. It is deemed trustworthy for the automated evaluation harness.
