# Decision Log

1. **Empirical Taxonomy (k=6)**: Decided to run KMeans (k=6) on a 400-tweet sample of AmazonHelp instead of using top-down assumptions. This revealed that "Non-English Queries" (Spanish/French) were a massive cluster, which wasn't in the original hypothesis.
2. **Adding NON_ENGLISH_QUERY intent**: Added this explicitly to the taxonomy rather than treating it as OOD, because it represents a significant portion of volume.
3. **Escalating NON_ENGLISH**: Decided to hard-escalate all non-English queries in triage.py since building multi-lingual RAG was explicitly out of scope for v1.
4. **Different Judge Model**: Used Llama-3.1-8b-instant as the judge while Llama-3.3-70b-versatile is the generator. Decided to keep them different to reduce self-preference bias, though acknowledging a different family (Gemini) would be better.
5. **Pre-Tuning Data Split**: Decided to rigidly split the golden set into 50-tune and 150-holdout. Tuning thresholds on the exact same data you report metrics on is a classic trap; this decision protects the integrity of the 88% precision score.
6. **Hand-Labeling Baseline 2**: Decided to hand-label `baseline2_train_labels.json` instead of using keyword bootstrapping. Keyword bootstrapping would make Baseline 2 a reflection of my own heuristics rather than a true TF-IDF baseline.
7. **Grounding Viability Check**: Decided to run this before any RAG code was written to prove that AmazonHelp tweets actually contain substantive resolutions (>40%) rather than just "DM us" boilerplate.
8. **Rule-Based Triage (First Pass)**: Decided to use simple string matching ("lawsuit", "ssn") for legal/PII risks in `triage.py` rather than a second LLM call, to keep latency and cost down for v1.
9. **Single-Intent Restriction**: Decided to force the LLM to pick the *primary* intent rather than multi-label, simplifying the baseline comparisons and the threshold tuning logic.
10. **Vector Store Choice (Chroma)**: Decided to use a local persistent ChromaDB rather than a managed cloud vector DB, to ensure the repository remains runnable offline in under 15 minutes as per requirements.
