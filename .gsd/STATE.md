# STATE.md

**Current Phase**: Complete (Wave 4)
**Last Updated**: 2026-09-13

## Current Context
- Evaluation Harness fully reconstructed to enforce completeness, strict rate limiting, and all reporting requirements from PRD v3.
- Fast-path eval is running and correctly computing macro F1, comparisons against baselines, and a 3-axis judge score.

## Recent Accomplishments
- **Dynamic Model Selection**: Pre-flight checks verify available models from both Groq and Gemini SDKs directly, applying 15-minute quota filtering.
- **True Pacing & Backoff**: Replaced arbitrary delays with `60 / (RPM * 0.8)` computed pacing, explicit TPM/RPD tracker, and a 3-retry max exponential backoff cap in `src/api_utils.py`.
- **Checkpointing**: Every example's processing instantly saves to JSONL (`eval_results.jsonl`), permitting clean resume without losing API quota on duplicated tasks.
- **Metrics Computation**: Added Cohen's Kappa check, Baseline 1 & 2 integration in pipeline output, full F1 + confusion matrices, retrieval similarities, and Verifier tracking variables. Outputs directly to `evaluation/results/report_summary.md`.
- **Enforcing Splits**: Hard assertions added in `run_eval.py` and `tune_thresholds.py` explicitly blocking data contamination.
- **RAG Ablation & Sycophancy**: Added runnable scripts for Groundedness delta checking and Judge Sycophancy (Wrong-but-polite vs Correct-terse pairs) testing.

## Next Steps
- Review `evaluation/results/report_summary.md` generated after fast-path completion.
- Fill in `data/human_annotations.json` to calculate real Cohen's Kappa.
