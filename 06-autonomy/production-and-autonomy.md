# Production & Autonomy: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 5, how you'd ship it, govern it, and widen trust over time
>
> ✅ **What this validates:** you can ship it, govern it, and widen trust deliberately, by the end you'll have proven an autonomy dial, a Trust Ladder rung with its eval gate, and a governance plan.

## Autonomy Dial by segment

_Autonomy is a product decision per user, not one global setting._

| Segment | Desired autonomy | Why |
|---|---|---|
| **Me, the PM who runs Cortex** (closest to a "Waymo passenger") | **Supervised:** Cortex fires on its own triggers, drafts the update and queues stories; I approve every draft and batch | I own the commitments, and Cortex hasn't cleared an eval gate over a real window yet |
| **My product lead**, who reads the weekly update | **Assisted:** they never use Cortex directly; they see only the update I approved | Leadership communication is above my line (M1 action 8b), so their trust rests on my approval, not Cortex's |
| **A new engineering lead**, who reviews proposed stories at sprint planning ("Tesla driver") | **Assisted:** stories arrive as suggestions, each traced to the PRD with inferred ones flagged; they decide what enters the sprint | Stories turn into team commitments, and they're new to Cortex and want to see the reasoning |

The dial never moves my M1 agent line: for every segment, Cortex can't post, commit a date or escalate to anyone.

## Trust Ladder

- **Current rung: Supervised.** Cortex acts on its own triggers (pulls, drafts, queues stories),
  but nothing leaves the queue until I approve it, and it has no way to post, commit or escalate.

- **Next rung, for one lane only: bounded-autonomous for the routine Monday draft.** Drafts that
  pass the critic skip my line-by-line review; I review only STUCK and ESCALATED runs and spot-check
  1 in 5. **I still post every update myself**, so the M1 line doesn't move.

- **Eval gate to reach it** (my M5 suite, over **8 consecutive weekly runs on real data**, plus the
  offline suite passing on every change):
  - EV-5 jailbreak / safety: **100%**, zero tolerance
  - EV-1 tool-call accuracy: **≥ 95%**
  - EV-2 path quality: **≥ 90% clean, 0 unsafe steps**
  - EV-3 recovery: **≥ 80%** without me
  - EV-4 task completion: **≥ 90%**
  - and **≥ 90% of Monday drafts approved by me unedited** over the same 8 weeks

- **Clean incident record for that window:** 0 embargoed names in any draft that reaches me,
  0 invented figures reaching me, 0 bound breaches (cost, iterations, queue cap), 0 kill-switch
  pulls. Critic catches are logged but don't count as incidents, since catching them is its job.

- **Incident record so far (fixtures only, about 20 runs during the course):** 0 above-the-line
  actions (nothing could be posted). Near-misses: embargoed names appeared in drafts in M2, M3, M4
  and the M5 jailbreak, all caught by the critic, none in a final output; one M4 run queued 19
  stories (now fixed by the per-run cap). **No real-data window yet**, so the gate hasn't started.

## Deployment plan

- **Runtime: serverless functions.** My M2 loop is a hook (new PM task) plus a Monday cron:
  event-driven, low-volume work, paid per run. An always-on service would sit idle almost all
  week. The two pieces of persistent state, the run log and the task-ID log, live in a small
  database rather than on one machine.
- **Operator / on-call owner:** **me (the PM)**, with **the engineering lead** (by role) as backup.
  Escalation: STUCK or ESCALATED runs come to me the same day; a suspected leak or bound breach
  means kill switch first, then the backup is paged.
- **Rollback**, fastest first: (1) the **kill switch** (`CORTEX_KILL=1` or a `KILL` file) halts
  every run; (2) **drop the dial** for the Monday lane back to supervised; (3) **disable a tool** by
  removing it from `TOOLS`; (4) **revert** to the last known-good commit.
- **Monitoring** (a weekly view built from `run-log.jsonl` plus the offline eval suite): exit mix
  (DONE / STUCK / ESCALATED), eval pass % on EV-1 to EV-6, escalation rate, cost per completed run,
  daily spend against the $5 cap, critic catch rate, and trust incidents.
- **Runbook:** pause = kill switch; recover = fix the cause, then re-run the task; regression check
  = replay the five recorded runs (M5 §5) before re-enabling.

## ROI metrics (beyond adoption & tokens)

| Metric | Target | How I capture it |
|---|---|---|
| **Outcome:** time saved on the weekly update and story prep | Set from a baseline: I time my manual prep for 2 weeks while Cortex runs in shadow mode, then target **≥ 50% less** | My own time log vs the shadow baseline |
| **Outcome:** completion rate | **≥ 90%** of runs end DONE with a draft I approve | `run-log.jsonl` exits + my approvals |
| **Cost-to-serve** per completed update | **≤ $0.15** model cost (today $0.05–0.13) **+ ≤ 10 min** of my review | Run log cost + review time |
| **Trust incidents** | **0** per 8-week window | Incident log (the same definition as the gate) |

## Widen-autonomy decision rule

When **8 consecutive weekly runs on real data** meet the gate (EV-5 100%, EV-1 ≥ 95%, EV-2 0 unsafe
steps, EV-3 ≥ 80%, EV-4 ≥ 90%, ≥ 90% approved unedited) with **0 trust incidents**, the Monday draft
lane moves up one rung. **One trust incident moves it straight back down** until the cause is fixed
and the gate is re-cleared from zero.

## Governance & forward strategy

- **Compliance:** embargoed roadmap items (Orbit, Pulsar) and personal data never enter a drafting
  prompt; roadmap grading is built, and read scoping for the other sources is next. The run log
  keeps IDs and outcomes, not content, with a 90-day TTL. The API key lives only in `.env`.
- **Safety:** above the line for **every** segment: posting, company-wide updates, date commitments
  and escalations. Cortex has no write tools; if posting is ever added, it gets a single-use token
  per approved update. The kill switch is mine.
- **Reliability:** caps of 8 iterations, 2 revisions, 90 s, $0.50 per run, $5 per day and 10
  stories per run; every non-success ends STUCK or ESCALATED with a reason. Refusals fall back to
  another model server-side. **Gap:** other API errors (e.g. the model being down) crash the run
  without a label today; the plan is to catch them as STUCK, and I write that week's update by hand.
- **Strategy:** next capability: **read-only Jira activity**, run in shadow mode for 4 weeks and
  gated by EV-1 and EV-4 on real data before Cortex uses it. Next segment: the engineering lead
  moves to supervised for story batches once 90% of proposed stories are accepted over two sprints.
