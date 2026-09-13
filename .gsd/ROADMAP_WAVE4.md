# Wave 4 Summary

**Objective:** Full correction pass on Tripwire Evaluation Harness for Resilience, Completeness, and Correctness.

**Key Changes:**
1. **Dynamic Model Selection**: Pre-flight script will select Groq/Gemini models based on live endpoints and sufficient RPD quotas for a 150/40-item run.
2. **True Pacing**: `api_utils.py` updated to strictly enforce `60 / (RPM * 0.8)` delays and track RPD explicitly.
3. **Comprehensive Metrics**: `run_eval.py` will compute Macro F1, precision/recall, confusion matrix, 3-axis LLM judge (Groundedness, Actionability, Tone), verifier retry rates, and baseline comparisons (Base1 vs Base2 vs Champ).
4. **Resumability**: Robustly save full item states to `eval_results.jsonl`.
5. **Ablation & Calibration**: Add calibration bucketing, RAG ablation script, and judge sycophancy test.
6. **Split Enforcement**: Hard assertions in `tune_thresholds.py` and `run_eval.py` to prevent data contamination.
7. **Fast Path (<15 mins)**: Enforce a 40-item fast-path processing to meet Part 0 requirements.

**Verification:**
- Run `python evaluation/run_eval.py --fast` and ensure it completes in <15m.
- Check `evaluation/results/report_summary.md` for complete metric tables.
