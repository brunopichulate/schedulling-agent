# /evaluate — Full Coherence Check

Run a deep, multi-phase evaluation of the current implementation. Use this after implementing anything significant before committing.

If $ARGUMENTS is provided, treat it as the specific focus area or file(s) to evaluate. Otherwise, evaluate based on the current git diff.

---

## Phase 1 — Static Analysis

Run all of the following and collect output:

```bash
uv run ruff check .
```

```bash
uv run python -m mypy src/ --ignore-missing-imports
```

```bash
pytest --tb=short -q
```

```bash
uv run python -m vulture src/ --min-confidence 70 2>/dev/null || echo "vulture not installed — skipping dead code scan"
```

Report results. Do NOT proceed to the next phase if there are critical failures (test failures or type errors on new code).

---

## Phase 2 — Clean Code Review

Read the current git diff:
```bash
git diff HEAD
```

Also read the full content of any files that were modified. Then evaluate:

**Naming & Clarity**
- Do variable, function, and class names reveal intent clearly?
- Are domain terms from the glossary in `CLAUDE.md` used correctly?
- Any abbreviations that would confuse a new developer?

**Single Responsibility**
- Does each function do exactly one thing? Can it be described in one sentence without "and"?
- Are there functions > 50 lines that should be broken down?

**DRY**
- Duplicated logic that should be extracted to a shared utility?
- Magic strings or numbers that should be constants?

**Complexity**
- Any deeply nested code (>3 levels) that should be flattened?
- Cyclomatic complexity concerns (>10 branches in one function)?

**Type Hints**
- Are all new functions fully type-annotated?
- Any `Any` types that should be more specific?

**Dead Code**
- Unreachable branches, commented-out code, unused imports?

---

## Phase 3 — Bug Detection (Async-Specific)

This stack (FastAPI + Celery + MongoDB + Redis + Agno) has specific failure modes. Check carefully:

**Race Conditions**
- Can two Celery tasks process messages for the same phone number simultaneously?
- Are state machine reads and writes atomic? Is there a check-then-act pattern on MongoDB state that's not serialized?
- Are Redis operations that need atomicity using pipelines or Lua scripts?

**Celery Task Idempotency**
- What happens if the same WhatsApp message triggers the task twice (duplicate webhook)?
- Is there a deduplication mechanism (message ID check)?

**External API Timeouts**
- Do all calls to OpenAI, WhatsApp Cloud API, Langfuse, and Google Calendar have explicit timeouts?
- What happens when any of these services is slow or down? Does it crash the Celery task?

**Error Handling**
- Any bare `except:` or `except Exception:` that swallows errors silently?
- Are Celery task failures properly logged and retried with backoff?
- Can the workflow leave the state machine in an inconsistent state if an exception occurs mid-transition?

**Resource Leaks**
- MongoDB connections properly closed after use?
- Redis locks released even on exception (use `try/finally` or context manager)?

**State Machine Validity**
- Can a message arrive out-of-order (e.g., founder replies before mentor has sent slots)?
- Are invalid state transitions rejected with a clear log?
- Is the `aguardando_intervencao_humana` state reachable from all states, not just some?

**WhatsApp 24h Window**
- Is the window correctly checked before deciding template vs. free-form message?
- What happens if the window expires mid-workflow?

**None & Edge Input**
- Are there missing None checks before dereference?
- What happens with empty string, whitespace-only, or very long messages from the user?

---

## Phase 4 — Security (OWASP-aligned)

**Input Validation**
- Is the WhatsApp webhook signature (META__VERIFY_TOKEN) validated before any processing?
- Are phone numbers validated/sanitized before being used as state machine keys?

**Prompt Injection**
- Is user-provided message content sent directly to the LLM without sanitization?
- Could a malicious WhatsApp message manipulate the agent's behavior?

**Secrets & Credentials**
- Any API keys, tokens, or passwords hardcoded in the codebase?
- Are sensitive values excluded from logs?

**PII in Logs**
- Are phone numbers, names, and conversation content absent from log lines?
- Does structured logging strip or mask sensitive fields?

**LLM Output Safety**
- Is agent output validated before being forwarded to WhatsApp?
- Could the LLM generate a message that breaks the WhatsApp template format?

---

## Phase 5 — Product & Discovery Alignment

Read the following docs before this phase:
- `docs/business-rules.md`
- `docs/edge-cases.md`
- `docs/discovery/README.md`
- `CLAUDE.md` sections: Decided Technical Decisions, Future Architecture Direction

**Business Rules**
- Does this implementation match every applicable rule in `docs/business-rules.md`?
- Does it violate any rule (even implicitly)?

**Edge Cases**
- Does this implementation resolve any of the open edge cases in `docs/edge-cases.md`?
  - If yes: flag them as candidates for /resolve-edge-case
- Does this implementation introduce NEW edge cases not yet documented?
  - If yes: flag them as candidates for /new-edge-case

**Technical Decisions**
- Does it stay consistent with all decided technical decisions in `CLAUDE.md`?
- (e.g., not using Behalf method, prompts in Portuguese, Redis+MongoDB split)

**Future Architecture**
- Does it create dead ends for future multi-agent expansion?
- Are new states added in a way that the state machine can be extended without rewriting?
- Is the change Agno-specific in a way that would block HyperFlow migration?

**Discovery Hypotheses**
- Does this implementation directly test or relate to any of the 5 hypotheses (H1–H5) in the Assumption Map?
- If yes, note which hypothesis and how the implementation enables or constrains validation.

---

## Output Format

Present results in this structure:

```
## Evaluation Report — [date] — [files or feature evaluated]

### Phase 1: Static Analysis
[results of each tool with pass/fail]

### Phase 2: Clean Code
✅/⚠️/❌ [check] — [finding] — [line number if applicable] — [severity] — [fix]

### Phase 3: Bug Detection
✅/⚠️/❌ [check] — [finding] — [severity: critical/high/medium] — [specific fix]

### Phase 4: Security
✅/⚠️/❌ [check] — [finding] — [severity] — [fix]

### Phase 5: Product Alignment
✅/⚠️/❌ [check] — [finding]
[Edge cases to document: ...]
[Edge cases resolved: ...]

---
### Summary
🚫 BLOCKERS (must fix before commit): ...
⚠️  WARNINGS (should fix soon): ...
✅ Safe to commit: yes/no
```

Be specific. Line numbers. Exact failure scenarios. Concrete fixes. No generic advice.
