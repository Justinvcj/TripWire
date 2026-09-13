# Wave 3 Summary

**Objective:** Make the Tripwire evaluation pipeline resilient to model unavailability, free-tier rate limits, and partial failures via dynamic selection, rate limit pacing, exponential backoff, and resumability.

**Changes Needed:**
1. **Dynamic Model Selection & Pre-flight**: Fetch live model lists from Groq and Gemini, pick the best models that fit a 150-request budget, and update `config.yaml`.
2. **Rate Limit Pacing & Backoff**: Add exponential backoff (max 3 retries) with jitter. Track TPM/RPM and enforce pacing delays dynamically to stay under 80% of limits.
3. **Resumability**: Append evaluation results to a JSONL file. On startup, skip already-processed tweet IDs.
4. **Resilience Utility**: Create `src/api_utils.py` to wrap LLM calls securely without crashing the run.
5. **Config Expansion**: Move all retry/backoff parameters to `config.yaml`.

**Files Touched:**
- `config.yaml`
- `src/config.py`
- `src/api_utils.py` (new)
- `src/classifier.py`
- `src/generator.py`
- `src/judge.py`
- `evaluation/run_eval.py`

**Verification:**
- Run `python evaluation/run_eval.py` to verify preflight checks, dynamic selection, pacing, and resumable execution.
