# Architecture v2 — "Warden": AmazonHelp Support Triage Agent

Companion to `PRD_v3.md`. Updates from v1: a taxonomy-discovery stage precedes indexing, a grounding-viability check gates the RAG design, the judge is architecturally separated from the generator (different model), and the golden set is split before it touches the tuning pipeline. The stack and interface philosophy are unchanged — the fixes are about what feeds the pipeline and how it's evaluated, not about adding subsystems.

---

## 1. Stack (unchanged from v1 — this was never the problem)

Python 3.11, Groq for generation, a **separate model for judging** (new — see Section 4), local `all-MiniLM-L6-v2` embeddings, ChromaDB persistent local store, Pydantic schemas, plain modules + Makefile, no web framework, no orchestration library, scikit-learn for baselines. Rationale table is unchanged from v1's Section 1 — nothing here needed to change, the gaps were upstream of the stack.

---

## 2. Component Diagram (updated — two new offline stages before the runtime pipeline)

```
                         ┌─────────────────────────────┐
                         │   Kaggle raw dataset (CSV)   │
                         └──────────────┬───────────────┘
                                        │ offline, one-time
                                        ▼
                         ┌─────────────────────────────┐
                         │  data/prepare.py             │
                         │  - filter to @AmazonHelp     │
                         │  - pair customer msg + reply │
                         │  - subsample ~5,000 pairs    │
                         └──────────────┬───────────────┘
                                        │
              ┌─────────────────────────┼──────────────────────────┐
              ▼                         ▼                          ▼
┌───────────────────────────┐ ┌────────────────────────┐ ┌───────────────────────────┐
│ evaluation/                 │ │ evaluation/              │ │ src/vector_store.py        │
│ grounding_viability_check.py│ │ discover_taxonomy.py     │ │ - embed pairs (MiniLM)     │
│ NEW — sample 100 pairs,     │ │ NEW — cluster 300-500    │ │ - write to ChromaDB        │
│ manually rate boilerplate   │ │ messages, human-review   │ │                            │
│ vs. substantive resolution  │ │ clusters -> final         │ │                            │
│ -> grounding_viability_     │ │ taxonomy (confirms or     │ │                            │
│    notes.md (PRD §3)        │ │ revises the 6-category    │ │                            │
│                              │ │ hypothesis, PRD §4)       │ │                            │
└──────────────┬───────────────┘ └──────────────┬────────────┘ └──────────────┬─────────────┘
               │  informs report framing         │  feeds Intent enum          │
               │  (does NOT block build)          ▼                            │
               │                     ┌─────────────────────────┐              │
               │                     │ src/schemas.py :: Intent │              │
               │                     │ enum finalized here      │              │
               │                     └─────────────────────────┘              │
               │                                                              │
               └──────────────────────────┬───────────────────────────────────┘
                                          ▼
                         ┌─────────────────────────────────────┐
                         │ data/golden_eval_set.json (200)       │
                         │ hand-labelled against final taxonomy  │
                         │        │                              │
                         │        ▼                              │
                         │ SPLIT (new, PRD §6):                  │
                         │  - golden_tune_slice.json (50)         │
                         │  - golden_holdout_slice.json (150)     │
                         └───────────────┬───────────────────────┘
                                         │
                                         ▼
     ┌─────────────────────────────────────────────────────────────┐
     │                     RUNTIME PIPELINE (per tweet)              │
     │  [unchanged from v1 — see below]                              │
     └─────────────────────────────────────────────────────────────┘
                    │
                    ▼
     ┌─────────────────────────────────────────────────────────────┐
     │ evaluation/tune_thresholds.py                                 │
     │  reads golden_tune_slice.json ONLY -> writes config.yaml      │
     ├─────────────────────────────────────────────────────────────┤
     │ evaluation/run_eval.py                                        │
     │  reads golden_holdout_slice.json ONLY -> final reported       │
     │  metrics, calibration, ablation, sycophancy probe              │
     └─────────────────────────────────────────────────────────────┘
```

**Runtime pipeline** (unchanged from v1's Section 2 diagram): redact PII → classify → retrieve → draft → verify (regenerate once on failure, else escalate `VERIFICATION_FAILED`) → triage decision → `TicketResult`.

The key structural change: **two offline analysis stages now sit upstream of the taxonomy and the RAG design commitment**, and **the golden set is partitioned before it reaches any tuning code**. Neither adds a runtime dependency — `discover_taxonomy.py` and `grounding_viability_check.py` are one-time scripts whose *output* (a finalized `Intent` enum, and a paragraph in the report) feeds the rest of the system. They are not services the pipeline calls at inference time.

---

## 3. Interface Boundaries

Unchanged from v1 (`IntentClassifier`, `Retriever`, `ReplyGenerator`, `TriageEngine` protocols in `src/interfaces.py`) — this abstraction was correct and doesn't need revision. The fixes in this version are about what data and which models sit behind these interfaces, not the interfaces themselves.

**One addition:** `ReplyGenerator` and the judge are now explicitly required to resolve to *different* concrete models via `config.py` (Section 4 below) — enforce this with an assertion at startup (`assert settings.judge_model != settings.llm_model`), so a future config change can't silently reintroduce the self-preference bias problem.

---

## 4. Judge/Generator Model Separation (new)

```python
class Settings(BaseSettings):
    llm_model: str = "llama-3.3-70b-versatile"       # generator + classifier
    judge_model: str = "llama-3.1-8b-instant"        # judge — deliberately different
    # If a second provider/key is available, prefer a genuinely different family
    # (e.g. Gemini Flash) over a same-family different-size model — size alone
    # only partially mitigates self-preference bias.
```
`judge.py` takes its own model setting, never defaults to `llm_model`. This is a two-line change with a real methodological consequence: it stops the system from grading its own homework at the model level, on top of the tune/holdout split stopping it at the data level.

---

## 5. Data Contracts

Unchanged from v1 (`Intent`, `EscalationReason`, `ClassificationResult`, `RetrievedPair`, `DraftReply`, `VerifierResult`, `TriageDecision`, `TicketResult` — all in `src/schemas.py`), **except**: the `Intent` enum's members are no longer fixed in this document. They're finalized only after `discover_taxonomy.py` runs (PRD §4) — write the enum last, once you know what it actually contains. Don't hardcode the six v1 category names into `schemas.py` until the discovery pass confirms or revises them.

---

## 6. Configuration

Same structure as v1 (`Settings(BaseSettings)`, `.env` for secrets, `config.yaml` for tunables), plus:
```yaml
judge_model: "llama-3.1-8b-instant"     # NEW — see Section 4
tune_slice_path: "./data/golden_tune_slice.json"       # NEW
holdout_slice_path: "./data/golden_holdout_slice.json" # NEW
```
`tune_thresholds.py` and `run_eval.py` read these paths explicitly rather than both pointing at `golden_eval_set.json` — this is what makes the tune/holdout separation enforced in code, not just a convention someone can forget.

---

## 7. Extension Points

Unchanged from v1 (API wrapper via `pipeline.py`'s pure function, second brand via config swap, multi-label via schema change, provider swap via the Protocol interfaces). **Add one:** multi-turn context. If this is picked up later, the seam is `pipeline.py::process_ticket` — change its signature to accept `thread_history: list[str]` instead of a single `text`, and thread that through to the classifier/generator prompts. Not built in v1 (PRD §1 explicitly cuts it), but the function boundary is already where that change would land, so it's not an architectural surprise later.

---

## 8. What Stays Deliberately Simple

The escalation matrix (`triage.py`) is still plain `if` branches, not a rules engine — five/six conditions don't warrant one. The taxonomy-discovery and grounding-viability scripts are one-time analysis tools, not scheduled jobs or monitored services — they inform a decision made once before the build, not a recurring pipeline stage. Resist turning either into more than that.
