# /discovery-status — PM Status: Discovery vs. Delivery

Give a structured picture of where this project stands across discovery and delivery. Designed for prioritization decisions.

---

## Step 1 — Gather data

Read all of the following:
- `docs/discovery/README.md` — artifact status and open questions
- `docs/edge-cases.md` — resolution status per case
- `docs/business-rules.md` — open/undefined rules
- `CLAUDE.md` — decided decisions, future architecture direction

Run:
```bash
git log --oneline -15
```

---

## Step 2 — Produce the report

Structure the output as follows:

---

### Hypotheses Status
For each of the 5 hypotheses (H1–H5 from the Assumption Map):
- **Status:** Untested / Partially testable / Being tested / Validated / Invalidated
- **Blocker:** what's preventing validation right now?
- **Evidence:** any signal from recent commits, tests, or decisions that informs this hypothesis?

---

### Discovery Artifacts
Table with: Artifact | Status | What's missing to complete it

---

### Delivery Status
Based on git log:
- What was recently built (last 15 commits)?
- What's implemented but not validated against a hypothesis?
- What do the open business rules in `docs/business-rules.md` tell us about delivery gaps?

---

### Edge Cases
- How many are unresolved? Resolved?
- Which unresolved cases are most likely to surface in the next real test?

---

### Top 3 Priorities Right Now
Based on everything above, what are the 3 most important things to address next?
Format: [Priority] — [Why it matters] — [Suggested action]

---

Be direct. This is for a PM making prioritization decisions, not a status update for a manager. Flag risks, not just progress.
