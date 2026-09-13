# [PROJECT NAME — TBD] — Readiness, Testing & Interview Playbook

Companion to `PRD_v3.md`, `ARCHITECTURE_v2.md`, and `IMPLEMENTATION_v2.md`. Those three answer "what are we building and how." This answers three separate questions: **is it done, is it tested right, and how do you actually win the room with it.** Read this last, right before you submit and right before the interview.

---

## 1. Is This It, or More Development?

**This is it, architecturally.** Adding anything else now would undo the exact discipline the whole design process was built on — the entire point of cutting the fallback chains, the UI, and the encrypted cache was to stop doing that. What's left isn't features. It's finishing moves:

- Write the actual README/report with **real measured numbers** — this literally cannot be done until the system has been run for real, so it's the last step, not a parallel one.
- Fill in `CITATIONS.md` and `DECISION_LOG.md` with your real decisions — not placeholders, not the generic versions drafted during planning.
- Do a final **cold read** of your own code, start to finish, as if you were the interviewer. Anywhere you hesitate to explain a line in one sentence is a line to either simplify or genuinely understand before submission.

**No more architecture.** At this stage, building further is a stalling tactic dressed up as progress. If you notice the urge to add "just one more thing," treat that urge as a signal to stop and finish, not a signal to keep building.

---

## 2. How You Know It's Operational

Not "it runs without crashing." Operational means you can point at *evidence* for each item below — not assume it, not say "should work."

| # | Check | Evidence required |
|---|---|---|
| 1 | `make eval` completes end-to-end on the fast path with no manual intervention | You've actually timed it. The number in the README is measured, not estimated. |
| 2 | All six triage branches have fired at least once | A real or deliberately constructed input that triggered each one, including `VERIFICATION_FAILED` — if that branch has never fired in a live run, you don't have a verifier, you have unused code. |
| 3 | Thresholds in `config.yaml` are the tuned values | They came out of `tune_thresholds.py`, not the 0.75/0.60 placeholders. If you submit with placeholders still in place, say so explicitly in the report rather than let it look tuned. |
| 4 | Cohen's Kappa is real | A number computed from your own 50-label human pass against the judge — whatever it turns out to be, not a target you hit. |
| 5 | `pytest tests/` is green | Including the three verifier tests specifically: clean pass, fabricated-claim catch, rule-violation catch. |

**If any of these five is "not yet, but it should work" — it is not operational yet.** Don't submit on "should."

---

## 3. How to Test It the Right Way

Layer it. Running the eval script once and calling it done is not testing — it's a demo.

1. **Unit level.** Each module's own tests, mocked LLM calls, runs in seconds, catches broken interfaces immediately. This is your safety net for live modification during the interview.
2. **Golden-set level.** The real eval, on real (unmocked) API calls — fast subset first, full holdout set only once the fast path is clean.
3. **Adversarial self-test.** Feed the system 5–10 tweets *not* in the golden set, deliberately constructed to try to break the verifier or the escalation logic — a fake order number formatted slightly off from your regex, a sarcastic compliment, a prompt-injection attempt. This is the test that catches overfitting to your own golden set. A system that only works on the data it was tuned against isn't proven, it's memorized.
4. **Ablation and sycophancy probe.** Not optional extras — part of "tested right," not a bonus round.

**The failure mode to actively avoid:** tuning thresholds and prompts against the golden set, then evaluating only on that same golden set. That's grading your own exam. The tune/holdout split and the adversarial self-test above are what stop that from happening — use both, not just one.

---

## 4. How This Actually Wins the Intern Spot

The system does not win it. **You, being able to defend every choice without notes — including the choices that didn't work — win it.**

### Know your own numbers cold, including the bad ones
If Baseline 2 beats the champion on some axis, or Kappa lands at 0.55 instead of some target you hoped for, say it out loud before they ask. In a format where they explicitly told you they'll ask you to explain and modify your own code live, unprompted honesty about your own limitations reads as competence — not weakness.

### Rehearse the modify-it-live scenario
Pick 2–3 plausible asks before the interview and actually do them against your own code, timed:
- "Add a seventh intent category."
- "Change the escalation logic to also fire on X."
- "Swap the embedding model."

If you can't do one of these in a few minutes on your own system, you don't know it as well as you think you do. Find that out now, not in the room.

### Lead with the "misleading headline number" section, unprompted
The same instinct that shaped this whole project — say the weak part before you're asked — is what differentiates you here. Interviewers grading a stack of these submissions will have seen plenty of people oversell a clean-looking F1. Being the one who pre-empts that question, in conversation, before they raise it, is what actually stands out. Not more code. More honesty about the code you have.

### Have the verifier story ready as your headline anecdote
One concrete story, rehearsed to under a minute: *"Here's a reply my system drafted. Here's how the verifier caught it. Here's why that matters for a support agent."* That single anecdote demonstrates judgment, not just implementation — it's worth more than a walkthrough of your whole architecture.

---

## 5. Pre-Submission Checklist (run through this literally, in order)

- [ ] All five items in Section 2 have evidence, not assumptions.
- [ ] The three testing layers in Section 3 have all been run at least once.
- [ ] The tune/holdout split was respected — no metric in the final report came from data the thresholds were tuned on.
- [ ] The judge and generator are confirmed to be different models (the `assert` in `config.py` has actually run, not just been written).
- [ ] README states measured reproduction time honestly, including if it's longer than 15 minutes for the full run.
- [ ] `DECISION_LOG.md` and `CITATIONS.md` are filled with your real decisions and real borrowed sources — not the template versions.
- [ ] You've done the cold-read pass on your own code and can explain every file in one sentence.
- [ ] You've timed yourself doing at least one of the three "modify it live" scenarios from Section 4.
- [ ] You know your own worst number and have a one-sentence explanation ready for it.
- [ ] You have the verifier anecdote rehearsed and can tell it in under a minute.

If every box is checked, you're not just done — you're ready. If any box isn't, that's your remaining work, and it's the only remaining work.
