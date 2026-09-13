# PRD v3 — AmazonHelp Support Triage Agent ("Warden") & Evaluation Harness
**Hiver SDE Intern Take-Home**
**Design philosophy:** the proof is worth more than the system. v3 exists because v2's engineering was sound but sat on unverified assumptions about the data and the methodology — this version fixes those assumptions before any code is written.

---

## 0. What Changed From v2 (read this first)

1. Intent taxonomy must now be **derived from the data**, not assumed top-down — the assignment's own instruction ("define from the data") was being violated.
2. Added a **grounding-viability check** before committing to the RAG design — if `@AmazonHelp` threads are mostly boilerplate ("please DM us"), that's reported as a finding, not hidden.
3. LLM judge must be a **different model family** than the generator, to avoid self-preference bias — or the report must explicitly caveat scores as directional if this isn't possible.
4. Golden set is now **split into tune/holdout slices** before threshold tuning — no more grading on the same data you tuned on.
5. **Multi-turn scope cut is now explicit** in the report, with a stated failure mode, instead of silently ignored despite the dataset being multi-turn.
6. Baseline 2 trains on a **small hand-labelled clean slice**, not self-generated keyword labels.

Everything else from v2 (verifier pass, tuned thresholds, calibration/ablation/sycophancy checks, lean stack, no UI) stays as-is — that part of the plan wasn't the problem.

---

## 1. Scope Statement

**Building:** a single-brand (`@AmazonHelp`) pipeline that classifies intent (taxonomy derived empirically, Section 4), drafts a grounded reply via RAG over historical resolved tweets, self-verifies the draft before it can ship, and decides auto-handle vs. escalate — plus a golden eval set, two baselines, an LLM-judge harness with measured human agreement, and an honest failure/limitations analysis.

**Explicitly not building, and now explicitly justified in the report (not just listed):**
- **Multi-turn conversation modeling.** The dataset is multi-turn; this system reads the customer's incoming message in isolation. State this directly in the problem-framing section, with the failure mode it causes: a customer whose second message is "still not fixed, it's been 3 days" will be classified/handled without knowledge of message 1. This is a deliberate v1 cut for time, not an oversight — say so.
- Multi-brand generalization
- Multi-label / multi-intent classification (single dominant intent only, v1)
- Non-English tweet handling
- Any UI beyond a CLI
- Automated execution of resolutions (refund issuance, account changes) — drafts and routes only, never acts
- Fine-tuning — in-context RAG only

---

## 2. Tech Stack

Unchanged from v2 — this was never the problem:

| Component | Choice |
|---|---|
| LLM (classify + generate) | Groq `llama-3.3-70b-versatile`, one provider |
| **LLM (judge)** | **A different model/provider than the generator** — e.g. Groq `llama-3.1-8b-instant` (different size, reduces but doesn't eliminate family bias) or, if a second free-tier key is available, a genuinely different model family (Gemini Flash). Pick whichever is actually available to you, but it must not be the same weights as the generator. Document which one you used and why in the decision log. |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2`, local |
| Vector store | ChromaDB, persistent local |
| Baseline 2 classifier | TF-IDF + Logistic Regression, trained on a **hand-labelled** slice (Section 6) |
| Metrics | pandas, scikit-learn, numpy |

---

## 3. Grounding Viability Check (new — do this before committing to the RAG design)

Before building `vector_store.py` for real: pull 100 random `@AmazonHelp` customer→brand-reply pairs and manually check how many brand replies contain an actual resolution (a specific instruction, a real policy statement, a concrete next step) versus generic boilerplate ("please DM us", "we're sorry to hear that").

- **If >40% are substantive**, the RAG grounding premise holds — proceed as designed.
- **If boilerplate dominates**, this is a real, reportable finding: state in the report that grounding quality is bounded by the corpus's own boilerplate rate, and that the verifier's job shifts from "check factual accuracy against rich context" to "check the draft doesn't invent specifics the boilerplate corpus never provided in the first place." This is not a failure of your system — it's an honest characterization of the data, and reporting it is exactly the kind of finding that differentiates a submission.

Either outcome gets one paragraph in the report. Do not skip this check and do not let the architecture diagram imply richer grounding than the data actually supports.

---

## 4. Intent Taxonomy — now derived, not assumed

**Process (replaces the v2 top-down list):**
1. Pull ~300-500 random `@AmazonHelp` customer messages.
2. Read them. Cluster by hand into natural groups (or use a quick embedding + k-means pass over the sample as a starting point, then manually correct/merge clusters — but the final categories must be human-reviewed, not just whatever k-means outputs).
3. Collapse to 5-7 categories that are MECE and each represent a meaningful share of volume (drop or merge anything under ~3% of the sample).
4. The six categories from v2 (`ORDER_STATUS_TRACKING`, `REFUND_CANCELLATION`, `ACCOUNT_SECURITY_ACCESS`, `PRODUCT_DEFECT_COMPLAINT`, `SUBSCRIPTION_BILLING`, `FEEDBACK_CHITCHAT`) are a reasonable **starting hypothesis** — expect to confirm, rename, split, or merge them once you've actually read the sample. Report whichever taxonomy you end up with, and note in the decision log what changed from the hypothesis and why.

This section of the report should read as "here's what I found in the data," not "here's what I assumed about Amazon support."

---

## 5. Escalation Reason Codes

Unchanged from v2 (fixed to be consistent end-to-end): `LOW_INTENT_CONFIDENCE`, `OUT_OF_DISTRIBUTION_ANOMALY`, `PII_REQUIRED_DM_HANDOFF`, `LEGAL_REPUTATIONAL_RISK`, `VERIFICATION_FAILED`, `NONE`.

---

## 6. Golden Evaluation Set — now split, and Baseline 2 gets clean labels

**200 hand-labelled examples**, same stratified/boundary/adversarial sampling method as v2 (150 stratified across the *final, data-derived* taxonomy / 25 hard-boundary / 25 adversarial-OOD).

**New: split before any tuning happens.**
- **Tune slice: 50 examples** — used only by `tune_thresholds.py` (Section 7.3.B) to pick confidence/similarity thresholds.
- **Holdout slice: 150 examples** — used only for final reported metrics. Never touched during threshold tuning or prompt iteration. If you catch yourself tweaking a prompt because it scored badly on the holdout slice, that slice is now contaminated — go back to the tune slice or a fresh sample instead.

Report both slice sizes and the split methodology explicitly — this single change is what turns your escalation precision/recall numbers from "optimistic" into "credible."

**New: Baseline 2 clean-label requirement.**
Hand-label a small slice (~200-300 examples, separate from the golden set) specifically to train `TfidfLogRegClassifier`. Do not bootstrap these labels from keyword heuristics — that was a shortcut in v2 that undermines the entire point of having a clean, simple baseline to compare against. This labeling effort is modest (a few hours) and directly protects the credibility of your comparison table.

Schema unchanged from v2:
```json
{
  "tweet_id": "str",
  "customer_text": "str",
  "gold_intent": "<one of the data-derived taxonomy categories, Section 4>",
  "gold_action": "AUTO_HANDLE | ESCALATE_TO_HUMAN",
  "gold_escalation_reason": "LOW_INTENT_CONFIDENCE | OUT_OF_DISTRIBUTION_ANOMALY | PII_REQUIRED_DM_HANDOFF | LEGAL_REPUTATIONAL_RISK | VERIFICATION_FAILED | NONE",
  "gold_reference_reply": "str",
  "ambiguity_flag": true
}
```

---

## 7. Evaluation Harness

### 7.1 Standard tiers (unchanged)
Classification metrics, retrieval/grounding metrics, LLM-as-judge (now cross-family, Section 2), human-judge agreement.

### 7.2 Added rigor (unchanged from v2)
Calibration check, RAG on/off ablation, judge sycophancy probe — all now run against the **holdout slice only**.

### 7.3 Verification Pass & Empirically-Tuned Thresholds (unchanged from v2, but tuning now uses the tune slice only)
Verifier step per v2 design (grounded / unauthorized_promise / rule_violation checks, one retry, then escalate `VERIFICATION_FAILED`). Threshold tuning (`tune_thresholds.py`) now explicitly runs against the **50-example tune slice**, and final reported precision/recall comes from the **150-example holdout slice** — this is the fix for the train-on-test problem.

---

## 8. Comparative Baselines

- **Baseline 1 (trivial):** majority-class intent (based on the data-derived taxonomy's actual majority class, not assumed), hardcoded static reply, escalate if text > 140 chars.
- **Baseline 2 (simple):** TF-IDF + logistic regression trained on the hand-labelled clean slice (Section 6), zero-shot LLM reply (no RAG), keyword-based escalation.
- **Champion:** RAG-grounded generation, verifier pass, confidence-gated classification, multi-signal escalation matrix.

No pre-committed target metrics. Report actual measured numbers on the holdout slice for all three.

---

## 9. PII Masking & URL Guardrail

Unchanged from v2.

---

## 10. Failure Analysis

Same five modes as v2 (sarcasm inversion, multi-intent entanglement, OOD policy drift, carrier blame-shifting, prompt injection). **Add a sixth, now that it's been named explicitly:** multi-turn context loss — a customer's follow-up message evaluated without knowledge of their prior message in the thread. Give a real example from the dataset.

---

## 11. "What's Misleading About My Headline Number"

Same structure as v2 (pick your best metric, show the slice where it's worst, give real examples, state the practical consequence). **Add, if applicable:** if the grounding-viability check (Section 3) found high boilerplate rates, this is one of your headline caveats — a high groundedness score may mean "didn't contradict the boilerplate" rather than "gave a genuinely well-grounded answer."

---

## 12. Decision Log

Keep from v2: single-brand focus, local embeddings, structured JSON outputs, escalation recall > precision bias, PII redaction before LLM calls, macro over micro F1, no fine-tuning, pre-seeded vector index, verifier pass over a second LLM provider, empirically-tuned thresholds.

**Add, from this revision:**
- Taxonomy derived from a 300-500 message sample rather than assumed top-down, and why (assignment explicitly requires this).
- Grounding-viability check performed before committing to RAG design, and its outcome.
- Cross-family judge model chosen specifically to avoid self-preference bias.
- Tune/holdout split on the golden set, and why train-on-test would have invalidated the escalation metrics.
- Hand-labelled clean slice for Baseline 2 instead of bootstrapped keyword labels.
- Multi-turn context modeling explicitly cut from v1 scope, with the specific failure mode it causes.

---

## 13. Directory Structure

```text
hiver-support-agent/
├── README.md
├── requirements.txt
├── config.yaml
├── Makefile
├── data/
│   ├── raw_sample.csv
│   ├── taxonomy_discovery_sample.csv     <-- NEW: 300-500 msgs for Section 4
│   ├── baseline2_train_labels.json       <-- NEW: clean hand labels, Section 6
│   ├── golden_eval_set.json              <-- 200 examples
│   ├── golden_tune_slice.json            <-- NEW: 50 of the 200, Section 6
│   ├── golden_holdout_slice.json         <-- NEW: 150 of the 200, Section 6
│   ├── human_annotations.json            <-- 50 human scores for Kappa
│   └── grounding_viability_notes.md      <-- NEW: Section 3 findings
├── src/
│   ├── config.py
│   ├── preprocessor.py
│   ├── classifier.py
│   ├── vector_store.py
│   ├── generator.py
│   ├── triage.py
│   ├── pipeline.py
│   └── judge.py                          <-- now configured to a different model than generator
├── evaluation/
│   ├── discover_taxonomy.py              <-- NEW: Section 4 clustering pass
│   ├── grounding_viability_check.py      <-- NEW: Section 3
│   ├── train_baseline2.py
│   ├── tune_thresholds.py                <-- now reads tune slice only
│   ├── run_eval.py                       <-- now reports on holdout slice only
│   ├── compute_metrics.py
│   ├── ablation_rag.py
│   └── judge_sycophancy_probe.py
└── docs/
    ├── DECISION_LOG.md
    ├── FAILURE_ANALYSIS.md
    └── CITATIONS.md
```

---

## 14. Execution Plan

1. Sample ~5,000 clean `@AmazonHelp` tweet-reply pairs from Kaggle.
2. **Run the grounding-viability check (Section 3)** on 100 pairs — decide how to frame RAG grounding in the report before building further.
3. **Run taxonomy discovery (Section 4)** on 300-500 messages — confirm or revise the six-category hypothesis.
4. Hand-label the 200-example golden set using the final taxonomy; split into 50 tune / 150 holdout.
5. Hand-label the separate ~200-300 example clean slice for Baseline 2 training.
6. Index the 5,000 pairs into ChromaDB.
7. Implement baseline 1, baseline 2 (trained on clean labels), champion pipeline (classify → retrieve → generate → verify) with fixed escalation codes.
8. Run `evaluate.py` fast path (subset of holdout) first — verify plumbing end-to-end.
9. Run calibration check, RAG ablation, judge sycophancy probe against the holdout slice.
10. Run `tune_thresholds.py` against the **tune slice only**.
11. Label the 50-example human-agreement subset yourself, compute Kappa.
12. Run the full evaluation on the **holdout slice**, write the report with real numbers, write CITATIONS.md and DECISION_LOG.md — including the multi-turn scope-cut and grounding-viability findings.
