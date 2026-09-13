# Decision Log

1. **Empirical Taxonomy (k=6)**: Decided to analyze the AmazonHelp subset of the Kaggle dataset empirically. This revealed that "Non-English Queries" (Spanish/French) were a massive cluster, which wasn't in our original hypothesis.
2. **Different Judge Model**: Used `Gemini-1.5-Flash` as the LLM-as-a-judge while `Groq/Llama-3.3-70b` is the primary generator. Decided to keep the families strictly separate to eliminate self-preference bias during evaluation.
3. **Pre-Tuning Data Split**: Decided to rigidly split the golden set into 50-tune and 150-holdout. Tuning thresholds on the exact same data you report metrics on is a classic trap; this decision protects the integrity of our Escalation Precision score.
4. **Resilient Rate-Limiter Architecture**: Opted against naive `time.sleep()` for API limits. Decided to build a mathematical pacing engine in `src/api_utils.py` that computes exact $60 / (RPM * 0.8)$ delays, tracks daily RPD limits, and executes exponential backoff for `429` errors.
5. **JSONL Checkpointing**: Decided to append evaluation results to `data/eval_results_fast.jsonl` immediately after each item. This ensures that if the script crashes or hits a hard quota limit on item 149, it seamlessly resumes without wasting previous API calls.
6. **Grounding Viability Check**: Decided to run this before any RAG code was written to prove that AmazonHelp tweets actually contain substantive resolutions (>40%) rather than just "DM us" boilerplate.
7. **Rule-Based Triage (First Pass)**: Decided to use simple string matching ("lawsuit", "ssn") for legal/PII risks in `triage.py` rather than a second LLM call, keeping latency and cost low for a v1 implementation.
8. **Single-Intent Restriction**: Decided to force the LLM to pick the *primary* intent rather than multi-label, significantly simplifying the baseline comparisons and the threshold tuning logic.
9. **Vector Store Choice (Chroma)**: Decided to use a local persistent ChromaDB rather than a managed cloud vector DB, to ensure the repository remains runnable offline in under 15 minutes as per the strict grading requirements.
10. **Ablation Testing the RAG Engine**: Decided to write an explicit `ablation_rag.py` script to test $K=3$ vs $K=0$. Evaluating the "lift" in Groundedness empirically is far more rigorous than just assuming RAG always helps.
