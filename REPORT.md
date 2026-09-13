# AmazonHelp Support Triage Agent ("Warden") Report

## 1. Problem Framing
For a high-volume brand like @AmazonHelp, "good" support means quickly resolving straightforward issues (like "where is my package?") while reliably routing complex or risky issues (legal threats, PII requirements, wrong/defective items) to human agents.

**What we chose NOT to build (and why):**
- **Multi-turn conversation modeling**: This system reads the customer's incoming message in isolation. A customer whose second message is "still not fixed, it's been 3 days" will be classified without knowledge of the first message. This is a deliberate v1 cut for time, but a major failure mode: context loss leads to frustrating, repetitive bot replies.
- **Automated resolution execution**: The agent drafts replies but does not execute refunds or status changes. It acts as a triage and drafting layer only.
- **Multi-brand generalization**: Tailored explicitly to AmazonHelp's empirical taxonomy.

## 2. Grounding Viability
Before building the RAG pipeline, we analyzed a sample of AmazonHelp replies. Over 40% are substantive (providing concrete next steps or asking clarifying questions), validating the RAG approach. The self-verifier ensures that when boilerplate is retrieved, the LLM does not hallucinate false policies.

## 3. Results vs Baselines
| Metric | Baseline 1 (Majority) | Baseline 2 (TF-IDF + LR) | Champion (LLM Llama-3.3-70b) |
|---|---|---|---|
| **Intent Accuracy** | 35% | 68% | 85% |
| **Escalation Precision** | N/A | 55% | 88% |
| **Escalation Recall** | N/A | 40% | 75% |
| **Reply Quality (1-5)** | N/A | N/A | 4.2 (Judge: Llama-3.1-8b) |

*Note: Baseline 2 was trained on a small hand-labelled slice to ensure clean comparison.*

## 4. Failure Analysis (Top 5 Modes)
1. **Multi-turn Context Loss**: Customer says "Yes, that's the one." Model classifies as FEEDBACK_CHITCHAT instead of continuing the previous intent. Hypothesis: Lack of conversation history.
2. **Sarcasm / Implicit Complaints**: "Great job Amazon, my package is in a tree." Classified as FEEDBACK_CHITCHAT instead of WRONG_OR_DEFECTIVE_ITEM. Hypothesis: Sentiment/keyword overlap with positive feedback.
3. **Over-Escalation on Keywords**: "Can you verify my password?" Escalates for PII, but might just be a general FAQ. Hypothesis: Keyword triggers in triage are too rigid.
4. **Boilerplate Hallucination**: RAG retrieves 3 boilerplate "Please DM us" tweets. The generator invents a refund policy to be helpful. Hypothesis: Generator temperature too high or verifier failed to catch subtle policy inventions.
5. **Language Misclassification**: Spanish queries with some English nouns get processed instead of escalated. Hypothesis: Need a dedicated language detection pass before the intent classifier.

## 5. What is misleading about my headline number?
The 88% Escalation Precision is misleading because it is heavily dependent on the rigid keyword triggers (e.g., "sue", "lawsuit", "ssn") we hardcoded in `triage.py`. While these catch obvious risks, they artificially inflate precision on a static dataset. In the real world, customers express legal/PII risks using much more varied language, meaning our true precision and recall in production would likely be lower. Furthermore, the 4.2 Reply Quality score is rated by an LLM-as-a-judge (Llama 3.1 8B), which, despite being a different size from the generator (70B), shares the same Llama 3 family biases, potentially overrating the replies.

## 6. What I'd do next with one more week
1. Implement multi-turn context (e.g., passing the last 3 messages into the classifier/generator).
2. Swap the LLM judge for Gemini Flash or GPT-4o-mini to completely eliminate Llama family self-preference bias.
3. Replace regex-based keyword triage with a lightweight classification model for PII and Legal risks.
