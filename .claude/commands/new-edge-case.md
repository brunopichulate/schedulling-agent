# /new-edge-case — Document a New Edge Case

Add a new edge case to `docs/edge-cases.md`.

If $ARGUMENTS is provided, use it as the initial description of the edge case.

---

Ask the following questions (can be answered together):

1. **What is the edge case?** — Describe the unexpected input, timing, or scenario in one sentence.
2. **What happens today?** — Does it crash, go silent, enter the wrong state, or something else?
3. **Is there a proposed solution?** — Even a rough idea, or is it still unknown?
4. **How severe is it?** — Does it block the happy path, or is it a rare/low-impact scenario?

Then:
- Read the current `docs/edge-cases.md`
- Assign the next available number in the table
- Set status to:
  - 🔴 if no solution is defined
  - 🟡 if a solution is defined but not yet implemented
- Add it to the **Current Edge Cases** table with a clear description and notes
- If it introduces a new state machine state or agent behavior, note that in the entry

Show the proposed addition and ask for confirmation before writing.
