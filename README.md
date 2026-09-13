# TripWire: AmazonHelp Triage Agent ("Warden")

An AI customer support agent for `@AmazonHelp` that classifies intent, drafts historically-grounded replies (RAG), and decides when to escalate.

## Quickstart (Reproduce in < 15 mins)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Ensure you have `datasets`, `pandas`, `scikit-learn`, `sentence-transformers`, `chromadb`, `groq`, `pydantic-settings` installed).*

2. **Set API Key**:
   Create a `.env` file in the root directory:
   ```
   GROQ_API_KEY=your_key_here
   ```

3. **Train Baseline 2**:
   ```bash
   python evaluation/train_baseline2.py
   ```

4. **Tune Thresholds** (Simulated):
   ```bash
   python evaluation/tune_thresholds.py
   ```

5. **Run Evaluation Harness**:
   ```bash
   python evaluation/run_eval.py
   ```
   *This outputs metrics to the console and `data/evaluation_results.txt`.*

## Deliverables Checklist
- [x] **Repo with runnable pipeline**: See `src/pipeline.py` and `evaluation/run_eval.py`.
- [x] **Golden evaluation set**: 200 hand-labelled examples split into tune (`data/golden_tune_slice.json`) and holdout (`data/golden_holdout_slice.json`).
- [x] **Evaluation harness**: Handled in `evaluation/run_eval.py` (simulates LLM-as-a-judge & metrics).
- [x] **Report**: See `REPORT.md`.
- [x] **Decision log**: See `DECISION_LOG.md`.
