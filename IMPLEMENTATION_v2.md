# Implementation Plan v2 — "Warden"

Companion to `ARCHITECTURE_v2.md` and `PRD_v3.md`. This supersedes the v1 build order — two new steps are inserted at the very front (before any pipeline code), and two existing steps are modified (judge config, threshold tuning data source). Everything else from v1's implementation plan (schemas, preprocessor, vector store, classifier, generator, triage, pipeline, eval scripts) is unchanged in substance; only the inputs feeding them differ.

---

## 0. Environment & Dependencies

Same `requirements.txt` as v1 — no new libraries needed for any of the fixes. The taxonomy discovery step can reuse `sentence-transformers` + `scikit-learn` (KMeans) already in the stack; no new dependency.

`config.yaml` now includes:
```yaml
llm_model: "llama-3.3-70b-versatile"
judge_model: "llama-3.1-8b-instant"
confidence_threshold: 0.75     # placeholder until tune_thresholds.py runs on the tune slice
similarity_threshold: 0.60     # placeholder until tune_thresholds.py runs on the tune slice
escalation_precision_floor: 0.80
retrieval_k: 3
max_reply_chars: 280
max_verifier_retries: 1
tune_slice_path: "./data/golden_tune_slice.json"
holdout_slice_path: "./data/golden_holdout_slice.json"
```

---

## STEP A (new, do this first, before any src/ code) — Grounding Viability Check

`evaluation/grounding_viability_check.py`:
```python
def run():
    """
    Loads 100 random (customer_msg, brand_reply) pairs from raw_sample.csv.
    Prints each pair to console/CSV for manual review.
    You (the human) tag each reply: SUBSTANTIVE or BOILERPLATE.
    Script tallies the split and writes data/grounding_viability_notes.md
    with the percentage and 3-5 representative examples of each.
    """
```
This is manual labeling work wrapped in a script for reproducibility, not an automated classifier — don't over-build it. Output is one short markdown file with a number and a few examples. This gates nothing in code; it gates your understanding of what you're about to build, and gives you the paragraph for PRD §3/§11.

**Do this before writing `vector_store.py` for real** — if boilerplate dominates, you still build the same RAG pipeline, but you walk into the interview already knowing its real limitation instead of discovering it when a reviewer asks "how grounded are these really?"

---

## STEP B (new, do this second) — Taxonomy Discovery

`evaluation/discover_taxonomy.py`:
```python
def run(sample_size: int = 400):
    """
    1. Sample `sample_size` random @AmazonHelp customer messages.
    2. Embed with the same MiniLM model used for retrieval.
    3. Run KMeans (k=6 as a starting point, matching the v1 hypothesis;
       also try k=5 and k=8 and compare silhouette scores).
    4. Print the top 15 messages closest to each cluster centroid.
    5. YOU manually read each cluster's representative messages and:
       - name the cluster
       - decide whether it matches one of the six v1 hypothesis categories,
         should be merged with another cluster, or is a new category
    6. Write the final taxonomy to data/taxonomy_final.json:
       {"intents": [{"name": "...", "description": "...", "source_cluster": N}]}
    """
```
This is a human-in-the-loop clustering pass, not a fully automated pipeline — the clustering is a starting point for you to read, not a label generator you trust blindly. Budget for actually reading ~400 messages; this is real work, not a script you run and forget.

**Only after this step**, finalize `Intent` enum in `src/schemas.py` using `data/taxonomy_final.json`'s output. If it matches the v1 hypothesis exactly, say so in the decision log ("confirmed empirically") — that's a legitimate and honest outcome, not a wasted step.

---

## 1. `src/schemas.py`

Same models as v1, **except** the `Intent` enum is written using Step B's output, not the v1 hypothesis directly. Test unchanged from v1 (invalid enum rejection, `TicketResult` round-trip).

---

## 2. `src/config.py`

Same as v1, plus load `judge_model`, `tune_slice_path`, `holdout_slice_path` from `config.yaml`. **Add one runtime assertion** at settings load time:
```python
assert settings.judge_model != settings.llm_model, \
    "Judge must use a different model than the generator to avoid self-preference bias (see ARCHITECTURE_v2 §4)"
```
This is a one-line guardrail that makes the fix impossible to accidentally undo later.

---

## 3. `src/preprocessor.py`, 4. `src/vector_store.py`

Unchanged from v1. Build and test exactly as before.

---

## 5. `src/classifier.py`

Same three-classifier structure as v1. **Two changes:**
- `MajorityClassifier` (Baseline 1) computes its majority class from the actual golden set / raw sample distribution using the *final* taxonomy — don't hardcode `ORDER_STATUS_TRACKING` as the assumed majority; check it.
- `TfidfLogRegClassifier` (Baseline 2) trains on `data/baseline2_train_labels.json` — a **hand-labelled** slice (~200-300 examples you label yourself, separate from both the golden set and the taxonomy-discovery sample). `evaluation/train_baseline2.py` must load this file and fail loudly if it doesn't exist — do not let it silently fall back to keyword-heuristic labels.

Champion classifier prompt (`prompts/classify.txt`) — same structure as v1, but the intent list and few-shot examples are filled in from `data/taxonomy_final.json`, not written by hand from assumption.

---

## 6. `src/generator.py`

Unchanged from v1 (draft prompt, verify prompt, `draft_with_verification` retry logic). The verifier prompt (`prompts/verify.txt`) is unchanged in wording, but its runtime model is now `judge_model`-distinct... actually, clarify: **the verifier is part of the generator's own self-check and should stay on the same model as the generator** — it's checking the draft's own internal consistency against its own retrieved context, not producing an independent quality score. The **judge** (Section 9, `judge.py`) is the separate scoring step for evaluation reporting, and that's the one that must be a different model. Don't conflate the two — verifier = same-model self-check at inference time; judge = different-model evaluation at eval time. Document this distinction explicitly in `DECISION_LOG.md` since it's a subtle point worth being able to explain.

---

## 7. `src/triage.py`, 8. `src/pipeline.py`

Unchanged from v1.

---

## 9. `evaluation/` scripts — updated data sources

1. **`compute_metrics.py`** — unchanged logic, but now always called with an explicit `dataset_path` argument rather than a hardcoded filename, so it's obvious at every call site whether you're computing metrics on the tune slice or the holdout slice.
2. **`tune_thresholds.py`** — **reads `settings.tune_slice_path` (50 examples) only.** Sweeps thresholds, picks the point maximizing recall at the precision floor, writes back to `config.yaml`. Never touches the holdout slice. Add an assertion at the top of the script: `assert "tune" in dataset_path`, as a dumb but effective guard against accidentally pointing it at the holdout file.
3. **`run_eval.py`** — **reads `settings.holdout_slice_path` (150 examples) only** for the numbers that go in the final report. If you want a smaller/faster sanity run during development, use `--fast` to take a random subset *of the holdout slice*, not a separate leak-prone sample.
4. **`ablation_rag.py`, `judge_sycophancy_probe.py`** — run against the holdout slice (or the 50-example judge subset, itself drawn from holdout, not tune).
5. **`judge.py`** — instantiates its model from `settings.judge_model`, never `settings.llm_model`. Import-time assertion from Section 2 catches any regression here.

**Splitting script** (`evaluation/split_golden_set.py`, new, small): takes the labelled 200-example `golden_eval_set.json`, randomly splits into 50/150 (fixed random seed, documented), writes `golden_tune_slice.json` and `golden_holdout_slice.json`. Run once, immediately after labeling is complete, before any tuning or evaluation touches the data.

---

## 10. `Makefile` — updated targets

```makefile
setup:
	pip install -r requirements.txt

grounding-check:
	python evaluation/grounding_viability_check.py

discover-taxonomy:
	python evaluation/discover_taxonomy.py

index:
	python -m src.vector_store --build

train-baseline2:
	python evaluation/train_baseline2.py

split-golden:
	python evaluation/split_golden_set.py

tune:
	python evaluation/tune_thresholds.py   # reads tune slice only, asserted in-script

eval:
	python evaluation/run_eval.py --fast   # holdout slice, fast subset

eval-full:
	python evaluation/run_eval.py          # full holdout slice

ablation:
	python evaluation/ablation_rag.py

judge-check:
	python evaluation/judge_sycophancy_probe.py

test:
	pytest tests/ -v
```

---

## 11. Testing Strategy — additions

All v1 tests unchanged and still required. **Add:**
- `tests/test_config.py::test_judge_generator_separation` — asserts `Settings()` raises/fails if `judge_model == llm_model`.
- `tests/test_split.py` — asserts `split_golden_set.py` produces exactly 50 + 150 with no overlap in `tweet_id` between the two files.
- `tests/test_baseline2_labels.py` — asserts `train_baseline2.py` raises a clear error if `baseline2_train_labels.json` is missing, rather than silently falling back to any heuristic.

---

## 12. Build Order Recap

**Grounding viability check → taxonomy discovery → finalize `Intent` enum in `schemas.py` → `config.py` (with judge/generator assertion) → `preprocessor.py` → `vector_store.py` (+ `make index`) → hand-label golden set against final taxonomy → `split_golden_set.py` → hand-label Baseline-2 clean slice → `classifier.py` (all 3) → `generator.py` (draft + verify) → `triage.py` → `pipeline.py` → `compute_metrics.py` → `tune_thresholds.py` (tune slice) → `run_eval.py` (holdout slice) → ablation + sycophancy probe → report + decision log, including the grounding-viability and taxonomy-discovery findings as first-class report content, not footnotes.**

The two new steps at the front are not optional preamble — they're what the report's problem-framing section is supposed to be built on, per the assignment's own wording.
