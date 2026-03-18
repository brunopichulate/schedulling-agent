# /update-docs — Sync Documentation with Code

Analyze recent code changes and update the relevant documentation files. Run this after implementing a feature, fixing a bug, or making any structural change.

If $ARGUMENTS is provided, treat it as a specific area to focus on (e.g., "state machine" or "agents").

---

## Step 1 — Understand what changed

Run:
```bash
git log --oneline -10
```

```bash
git diff HEAD~1 -- src/
```

If there are uncommitted changes, also run:
```bash
git diff -- src/
```

---

## Step 2 — Identify affected docs

Based on what changed, determine which docs need updating:

| If this changed | Update this doc |
|---|---|
| State machine states, transitions, or logic | `docs/architecture.md` → State Machine States section |
| New agents, tools, or agent behavior | `docs/architecture.md` → Component Interactions section |
| Data flow or pipeline steps | `docs/architecture.md` → Full Data Flow section |
| New dependencies added (`uv add`) | `CLAUDE.md` → Tech Stack table |
| New files or directories in `src/` | `CLAUDE.md` → Project Scaffolding section |
| New env vars used in code | `CLAUDE.md` → Environment Variables section |
| Business logic in workflows or handlers | `docs/business-rules.md` |
| Edge case handling added | `docs/edge-cases.md` |
| Discovery artifact created or updated | `docs/discovery/README.md` |

---

## Step 3 — Propose and apply changes

For each doc that needs updating:
1. Read the current content of that doc
2. Show the specific section that needs changing
3. Propose the exact update
4. Ask for confirmation before applying

Be conservative — only update what clearly changed. Do not rewrite sections that are still accurate. Do not add sections that don't reflect real changes.

---

## Step 4 — Flag anything that needs human input

If you find:
- A new edge case introduced by the change → suggest running `/new-edge-case`
- An edge case that was resolved → suggest running `/resolve-edge-case`
- A discovery artifact whose status should change → flag it with the suggested update
- A business rule that was implicitly changed but not documented → flag it for Bruno to confirm before updating
