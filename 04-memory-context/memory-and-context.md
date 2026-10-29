# Context Engineering & Memory: Cortex PM Chief-of-Staff Agent

> Module 4 · Context Engineering & Memory
>
> ✅ **What this validates:** the agent reasons on the right, safe inputs, by the end you'll have proven a context budget, per-source retrieve-vs-long-context decisions, and a memory map with risk mitigations.
>
> 🗂️ **How the lab maps to this file:** In **Part A** (before the lecture) you don't edit this file, you rough-draft on scratch, focused on the per-source calls in **section 2** plus a quick remember/forget + "how it rots" sketch. In **Part B** (after the lecture) you complete **all five sections**; the Lab Guide's guided builder writes this file for you to copy in and commit.

## 1. Context budget

Each iteration gets, in priority order:
1. Cortex's operating rules (system prompt), always.
2. The task brief, whole.
3. This project's record (status, flags, PRD summary).
4. This project's recent activity (PRs, issues, Sev-1s, metric).
5. This project's roadmap section only, never the confidential items.
6. Team norms.
7. The 2 most recent past updates for this project, for format and week-over-week.

**Left out on purpose:** other projects' data, confidential roadmap items (Orbit, Pulsar),
older updates. A run today is a few thousand tokens, so the budget is about *what's safe and
relevant*, not about fitting.

## 2. Retrieve vs. long-context: per source

For each data source, decide: **retrieve** (narrow a large/changing corpus to the relevant slice) or **long-context** (just include a bounded set you can reason over).

| Source | Size / volatility | Decision | Deciding factor & why |
|---|---|---|---|
| Task brief (`get_task`) | One small doc per run | **Long-context** | **Size:** bounded and self-contained; include it whole and reason over all of it. |
| Project record (`get_project`) | One record among many projects | **Retrieve** (exact ID) | **Size:** fetch only this project's record, so other projects never enter the context. |
| Recent activity (`get_activity`) | Big and changing; grows every day | **Retrieve** | **Volatility:** big and changing, it grows every day, so pull only this project's latest slice. |
| Past updates + decisions (`search_past_updates`) | Unbounded; one more every week | **Retrieve** | **Size:** only the last 2 updates for this project are needed for format and comparison. |
| Roadmap (`get_roadmap`) | Medium; holds confidential items | **Retrieve** (this project's section) | **Citation / audit:** cite the shareable entry; the confidential items must never reach the drafter. *Today the tool returns the whole roadmap; that's the leak path.* |
| Team norms (`get_norms`) | Small (~2 KB); changes occasionally | **Long-context** (fresh each run) | **Cost:** small enough to include whole; re-reading it every run keeps it current. |

## 3. Retrieval quality plan

| Retrieved source | Routing | Grading | Reranking | Self-verification | Caching | Why these moves |
|---|---|---|---|---|---|---|
| Project record | ✓ | | | ✓ | | Exact-ID lookup is the routing; the critic checks every status and flag claim against the record (checks 1–2). |
| Recent activity | ✓ | ✓ | ✓ | ✓ | | Route by project ID; grade out items from other projects; newest first so this week's PRs aren't lost in the middle; the critic traces every PR and metric (checks 1–2). |
| Past updates + decisions | ✓ | ✓ | ✓ | | ✓ | Route to this project only; grade out other projects' updates, and return **nothing** rather than unrelated updates when there's no match; most recent 2 first; cache for the Monday run. |
| Roadmap | ✓ | ✓ | | ✓ | ✓ | Route to this project's section; **grade out every CONFIDENTIAL item before the drafter sees it**; the critic's check 3 is the backstop; cache within the day. |

**Long-context sources** (task brief, team norms) are included whole, so they need no retrieval moves.

**Today vs plan:** built today are exact-ID routing for the project record and activity, and
self-verification through the critic. Not built yet: roadmap grading (confidential items still
reach the drafter), past-update routing and grading (it falls back to unrelated updates),
reranking and caching.

## 4. Memory map (your PM brain)

| Memory type | What Cortex stores | Scope / TTL | Who may write it |
|---|---|---|---|
| **Working** (in-loop) | This run's pulled data, drafts, critic verdicts, revision count, cost so far | This run only; discarded at the end | Cortex |
| **Episodic** (past runs) | Past status updates and decisions per project; the run log (`run-log.jsonl`); the task-ID log (designed in M2) | Per project. Updates kept 12 weeks (only the last 2 are loaded); run log and drafts 90 days | Only **PM-approved** updates become past updates; Cortex writes only the run log |
| **Semantic** (durable facts) | Team norms, PRD scope, project status and flags, the embargo list | Long-lived, but **re-read from source every run**, never trusted from memory | Humans only (PM, leadership); Cortex never writes them |
| **Shared** (across agents) | The draft + source log sent to the critic; the critic's verdict and reasons sent back | This run only | Cortex and the critic, within the run |

**Agent Line tie (M1):** Cortex may *read* above-the-line facts (norms, roadmap, decisions) but
never *write* them. Deciding what becomes a durable fact stays with me.

## 5. Memory risks & mitigations

| Risk | Where it bites Cortex | Mitigation |
|---|---|---|
| **Drift** | A past update says "Green" while a new Sev-1 has opened (this week's data pack has an open Sev-1, #440, on Vega) | Past updates are used only for format and trend, never as current facts; status, flags and Sev-1s are re-fetched every run |
| **Poisoning** | Text from a task brief or pasted notes (like the jailbreak fixture) written into memory and trusted on every later run, the ChatGPT memory attack in miniature | Cortex writes no durable memory except the run log; only PM-approved updates become past updates; brief content is data, not instructions (prompt rule) |
| **Staleness** | A decision reversed, or a norm or embargo changed. Pulsar became embargoed only this week, so a roadmap cached from last week wouldn't know | Date-stamp every entry, latest decision wins; cache the roadmap and norms only within a day; re-read them every run |
| **Confidential / retention** | Embargoed projects (Orbit, Pulsar) and people's names in updates | Grade confidential items out before the drafter sees them (§3); the run log stores IDs and outcomes, not content; `run-output/` stays gitignored; 90-day TTL on run logs and drafts, enforced as a **bound in M5** |
