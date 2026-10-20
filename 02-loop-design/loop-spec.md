# Loop Spec: Cortex PM Chief-of-Staff Agent

> Module 2 · Loop Engineering, ★ Deliverable 2
>
> ✅ **What this validates:** the agent knows when to run and when to stop, by the end you'll have proven a one-page Loop Spec with a trigger, a definition of "done," and explicit stop conditions.
>
> Your one-page blueprint for how the work you handed to the agent (M1) actually *runs*.
> An agent is just a prompt that fires itself, this spec says when it fires, what "done" means, and what it needs to do the job. Living document; refine as the course progresses.

## 1. Trigger & loop type

**Chosen type:** hook + cron (with a small goal loop inside each run)

- **Hook (primary):** fires when a new PM task arrives, because tasks arrive anytime.
- **Cron (Monday morning):** assembles the weekly leadership update, because updates are weekly. The same run sweeps for any task the hook missed.
- **Why this pairing:** urgent tasks reach me directly, so a missed task waiting until Monday's sweep is acceptable.
- **Ruled out:** not a heartbeat: tasks arrive as events and the update is weekly, so checking every N minutes would mostly be wasted runs. Not a goal loop as the trigger, but inside each run the draft → critic → revise cycle is a small goal loop, capped at 2 revisions.
- **Idempotency:** one shared log of processed task IDs, checked by both the hook and the Monday sweep, because it covers both duplicate paths. Plus one weekly update per project per week.

*Part A instinct:* "a mix, because tasks arrive anytime but updates are weekly." *Open question then:* hook or cron? *Answer:* both, one per job.

## 2. Goal / definition of done

One run is **done** when the drafted update (and any proposed stories) is **queued for my
review after the critic passes**, and Cortex has sent, posted or created nothing.

- **Self-validation:** the critic, a separate model call that never saw Cortex's reasoning,
  checks every claim against the pulled data. Cortex never grades its own draft.
- **Not done:** a draft the critic hasn't passed, or anything that left the queue.

## 3. Stop conditions

| Condition | What it looks like (detectable) | What happens |
|---|---|---|
| **Success** | Critic verdict = pass, and the draft is queued | Mark the task ID processed, log "done", stop at the HITL checkpoint |
| **Stuck / give up** | (a) a required read tool returns an error, e.g. `project_not_found`; (b) the critic rejects 2 revisions (revision cap); (c) 8 iterations without a passing draft; (d) run cost reaches $0.50 | Stop, log which condition fired, and hold the last draft for me, labelled **STUCK**, not "approved" |
| **Escalate to human** | The task asks for something above my M1 agent line: (a) a ship or GA date commitment (action 4); (b) anything about an embargoed project such as P-ORBIT; (c) posting or sending (actions 8a/8b); (d) escalating to other people (action 6). Cortex flags it with an `ESCALATE:` marker and a reason. | Stop, don't draft that part, and hand it to me labelled **ESCALATED**, with what it needs from me |

*Part A instinct:* "done = draft queued for my review after the critic passes"; "stop if data missing,
embargoed project, or a date commitment." *What Part B added:* the stuck exits (revision cap,
iteration cap, cost cap), and a separate ending for each exit, so an escalation no longer looks
like a success.

## 4. State

- **Within a run** (discarded at the end): what Cortex pulled, its drafts, the critic's
  verdicts, the revision count and cost so far.
- **Across runs** (kept): the processed task-ID log (dedupe, §1), and last week's update per
  project, for format and week-over-week comparison.
- **Scope:** per project. One project's data never carries into another project's draft, and
  embargoed projects (P-ORBIT) never enter a draft at all.
- **Today vs plan:** today nothing persists except the saved draft and a run log (one line
  per run: task, exit, reason, cost) in `run-output/`; past updates come from `fixtures/`. The task-ID log is designed here, not built yet.

## 5. The five things a loop can lean on

| Component | For Cortex |
|---|---|
| **Work tree** (isolated workspace per run, a git worktree) | Not needed yet, because Cortex only reads and drafts; nothing writes to a repo. |
| **Skills** (reusable capabilities) | Not needed yet, because Cortex does one job (weekly update + story proposals). A "status-update format" skill is a candidate once there's a second job. |
| **Plugins / connectors** (tools & access, optional if you don't have one yet) | None wired yet; `fixtures/` stand in. **Plan:** Jira (read activity, queue stories) and Slack (inbound tasks, the hook's event source), read-only first. |
| **Subagents** (independent check when the loop can't grade itself) | The critic is already an independent check on every draft. More subagents → M3 orchestration-map.md. |
| **State tracking** | As §4: within-run history, the task-ID log, last week's update per project. |

> Context plan (M4) and the hand-off to bounds & evals (M5) come in later modules, you'll add them to their own deliverables then, not here.

## Link to live loop

[`00-build/agent.py`](../00-build/agent.py) (loop and exits), [`00-build/critic.py`](../00-build/critic.py) (self-validation), [`00-build/prompts.py`](../00-build/prompts.py) (operator instructions)
