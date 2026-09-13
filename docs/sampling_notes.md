# Sampling and Labelling Methodology

## Data Source
The primary dataset used is the [Customer Support on Twitter](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter) Kaggle dataset.

## Sampling Strategy
1. **Brand Isolation**: We filtered the ~3M rows down to only those where `author_id == 'AmazonHelp'`, yielding ~155,000 viable Amazon responses.
2. **Conversation Matching**: We dropped any responses that were not direct replies to a customer (`in_response_to_tweet_id`), leaving us with pairs of `(Customer Query, Brand Resolution)`.
3. **Deduplication**: We strictly deduplicated by the customer's tweet ID to ensure one resolution per unique query.
4. **Random Selection (Seed 42)**: We shuffled the dataset and extracted a fixed window:
    - **Indices 0–2000**: Used as the unstructured historical resolutions for our ChromaDB (RAG retrieval).
    - **Indices 2000–2200 (N=200)**: Reserved purely as our Golden Evaluation Set.

## Labelling Methodology
Since this dataset is unlabeled out of the box, we require labels for both **Intent Classification** and **Triage Routing (Escalate vs Auto-Handle)**.
To build a scalable and unbiased golden set, we utilized Gemini 1.5 Flash as an automated labeler to map the 200 holdout examples against our defined empirical taxonomy.

### Intents:
1. `DELIVERY_SHIPPING_STATUS`: "Where is my package?"
2. `REFUND_CANCELLATION_BILLING`: "I need my money back."
3. `WRONG_OR_DEFECTIVE_ITEM`: "This arrived broken."
4. `NON_ENGLISH_QUERY`: Spanish/French/Portuguese support.
5. `FEEDBACK_CHITCHAT`: General anger, thanks, or unstructured complaints.

### Triage Actions:
1. `AUTO_HANDLE`: Standard policies apply.
2. `ESCALATE_TO_HUMAN`: Queries containing explicit PII, legal threats, or severe, multi-turn frustration.

**Splits**:
The 200 labelled examples were strictly separated into:
- `data/golden_tune_slice.json` (N=50): Used exclusively for prompt engineering, threshold tuning, and training Baseline 2.
- `data/golden_holdout_slice.json` (N=150): The untouchable holdout set used exclusively for the final evaluation harness run.
