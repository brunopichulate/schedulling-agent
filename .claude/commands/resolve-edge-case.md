# /resolve-edge-case — Close a Resolved Edge Case

Mark an edge case as implemented and resolved in `docs/edge-cases.md`.

If $ARGUMENTS is provided, use it as the edge case number or description to identify which one was resolved.

---

Ask:
1. **Which edge case?** — Number from the table, or description (if not provided via $ARGUMENTS)
2. **What was built?** — Brief description of what was implemented
3. **Which files handle it?** — List the relevant file paths
4. **Which new states or agents were added?** — Any additions to the state machine or agent layer?

Then:
- Read the current `docs/edge-cases.md`
- Move the entry from **Current Edge Cases** to **Resolved Edge Cases** section
- Update status to 🟢
- Add implementation notes: what was built, which files, which states/agents

Also check:
- Should `docs/architecture.md` be updated? (new states, new components)
- Should `docs/business-rules.md` be updated? (new rules introduced by the resolution)

Show the proposed changes and ask for confirmation before applying.
