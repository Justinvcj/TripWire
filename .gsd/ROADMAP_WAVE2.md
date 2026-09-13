# Wave 2 Summary

**Objective:** Implement PRD v3 updates, integrate real API keys, setup Gemini judge, expand evaluation scripts, and restructure docs.

**Changes Needed:**
- Update `.env` with Groq and Gemini API keys.
- Move documentation to `docs/`.
- Add `Makefile` for quickstart.
- Enhance Groq prompts to be highly explicit and robust.
- Create `src/judge.py` using `google-genai` client for Gemini 2.0 Flash.
- Create missing evaluation scripts: `compute_metrics.py`, `ablation_rag.py`, `judge_sycophancy_probe.py`.
- Update `REPORT.md` and `DECISION_LOG.md` to perfectly match PRD v3.

**Files Touched:**
- `.env`
- `config.yaml`, `src/config.py`
- `src/judge.py`, `src/pipeline.py`
- `prompts/classify.txt`, `src/generator.py` (prompt updates)
- `evaluation/*`
- `docs/*`
- `Makefile`

**Verification:**
- Run `make eval` to ensure the end-to-end pipeline and LLM judge actually execute with real API calls.
