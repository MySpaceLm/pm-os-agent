# Orchestration Map: Cortex PM Chief-of-Staff Agent

> Module 3 · Orchestration & Subagents, ★ Deliverable 3
>
> ✅ **What this validates:** nothing advances unchecked, by the end you'll have proven a justified topology, a roster, and a validator with a defined fail action.
>
> Builds on your M2 Loop Spec. Only split one agent into a team when there's a real reason, coordination has a cost.

## 1. Why split? (or why not)

**Cortex today, from my Loop Spec:** one agent, fired by a hook on inbound PM tasks plus a
Monday cron, that pulls project data, drafts the update and proposed stories, and stops at my
review checkpoint (DONE / STUCK / ESCALATED).

| Reason | Applies? | Why / why not |
|---|---|---|
| Separation of concerns | No | Drafting and following the posting norms don't pull against each other enough to need two agents; the norms are rules the drafter already follows, and the validator checks them. |
| Parallelism | No | One task is about one project, and Cortex already pulls its five data sources in a single step; there's no wall-clock time worth splitting for. |
| Independent validator | **Yes** | Cortex can't grade its own draft. In my M2 happy run, the draft named the embargoed Orbit project while claiming to have left it out, and only the separate critic caught it. |
| Context-window pressure | No | One project's fixtures fit easily in one context; a run is a few thousand tokens. |

**Decision:** split exactly once, for an independent validator. Everything else stays in the one
Cortex agent.

## 2. Topology

**Pattern:** single + subagents (one lead agent, one validator subagent)

```
[Hook: inbound PM task]  or  [Monday cron: weekly update + sweep]
        │
        ▼
[Cortex] pull data (5 read tools) → queue stories → draft update
        │   project_not_found → STUCK (a), held for PM, before any draft
        ▼
[Critic] 5 checks, fresh context, sees only draft + sources
        ├─ pass, draft starts "DONE:"     → [PM review checkpoint] → queued, nothing posted (DONE)
        ├─ pass, draft starts "ESCALATE:" → [PM] handed over (ESCALATED)
        └─ fail → back to Cortex with reasons, max 2 revisions
                   └─ 3rd fail → STUCK (b), last draft held for PM
```

## 3. Roster

| Agent / subagent | Responsibility | Runs which Loop Spec |
|---|---|---|
| **Cortex** (lead) | Pulls data, queues stories, drafts the update, ends with DONE or ESCALATE | M2 loop: hook + Monday cron, three exits |
| **Critic** (validator subagent) | Checks every proposed output against the 5 checks in §5; never drafts, never sends | One call per proposed output, inside the M2 inner goal loop (max 2 revisions) |
| **Me** (PM, human) | Approves, posts, decides dates and escalations | Above the line (M1: actions 4, 6, 8a, 8b) |

## 4. Communication & hand-offs

| From → To | What passes | Form |
|---|---|---|
| Cortex → Critic | The proposed output + a source log (task brief + every tool call and result) | In-process function call, plain text |
| Critic → Cortex | Verdict + reasons | JSON `{verdict, reasons}`, schema-enforced; on fail, reasons appended as a message |
| Cortex → Me | Draft, exit label (DONE / STUCK / ESCALATED) and reason | Banner + `run-output/status-update-*.md` + one `run-log.jsonl` line |

No MCP or A2A: a plain in-process hand-off I control. The Cortex ↔ Critic exchange already has A2A's
shape (from, to, type, content), so it could move to a protocol later if the critic lived elsewhere.

## 5. The validator

**Critic checks** (each one pass/fail, against the pulled data only):
1. **Right project, real IDs:** every project, PR and issue named exists in the pulled data.
2. **Every figure and status call is traceable:** no invented numbers, and a Green/Amber/Red
   call matches the evidence (status, flags, Sev-1s).
3. **No confidential leak:** no embargoed project (e.g. P-ORBIT) is named or described anywhere
   in the output, not even as "left out."
4. **No commitments above my agent line:** no ship or GA date, no launch gate, nothing posted or
   created; stories are only queued.
5. **Stories trace to the PRD:** each queued story maps to an in-scope PRD item, the batch is
   within the cap, and any inferred story is flagged as inferred, never claimed as "in scope."

**Fail-action:** revise. Cortex gets the failed checks and reasons and redrafts.
**Revision cap:** max 2 revisions. On a 3rd fail, the run stops as **STUCK (b)** (Loop Spec §3):
the last draft is held for me with the critic's reasons, and the run is logged.
**Pass-action:** the draft advances to my review checkpoint. It never auto-sends; posting stays
above my agent line (M1, actions 8a/8b).

## 6. State: shared vs isolated

- **Shared:** the pulled source data (the critic sees the same tool results Cortex used) and the
  current draft.
- **Isolated:** Cortex's conversation and reasoning, including its earlier drafts, never reach the
  critic. The critic's reasoning stays inside its own call; only its verdict and reasons go back.
- **Fresh every review:** on a revision, the critic sees only the new draft, not its own earlier
  verdict, so it re-checks from scratch instead of anchoring on its first opinion.
- **Across runs:** the run log, and the task-ID log designed in M2, belong to Cortex only.

## 7. Cost & latency budget

| Case | Model calls | Observed run cost |
|---|---|---|
| Clean pass (0 revisions) | ~3 drafter + 1 critic | $0.045–0.049 |
| 1 revision | +1 drafter + 1 critic | $0.083 |
| 2 revisions (the cap) | +2 drafter + 2 critic | $0.130 |

- **What the validator adds:** one critic call per proposed output, about $0.01 on a clean pass;
  each revision cycle (redraft + re-check) adds about $0.04.
- **Worst case at the cap:** about $0.13–0.15 per run, well under the $0.50 per-run cost cap.
- **Latency:** not measured yet. Each critic call adds one model round trip, so the worst case is
  4 extra round trips before a draft reaches me. Measure wall-clock time per exit in M5.
- **Bound for M5:** keep the revision cap at 2, and alert if a run's validator spend exceeds $0.10.
