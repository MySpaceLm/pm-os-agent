# Cortex, a PM Chief-of-Staff Agent

> A bounded chief-of-staff agent: a new PM task or the Monday cron fires it, it pulls project data through read-only tools, drafts the leadership update and proposes traced stories, an independent critic checks every draft, and every run stops at my review. Nothing is ever posted.

_MySpaceLm · Agentic Loops for PMs Cohort · October 2026_

Repo: https://github.com/MySpaceLm/pm-os-agent · Pitch deck: [`pitch.html`](pitch.html)

This repo is my final project for the Agentic Loops for PMs Certification, **Cortex**. Each module's artifact lives in its own folder; this README is the dashboard and the pitch.

---

## Module artifacts

### M1 · The Agent Line
- **Agent-line map**: [`01-agent-line/agent-line-map.md`](01-agent-line/agent-line-map.md)

### M2 · Loop Engineering
- **Loop spec**: [`02-loop-design/loop-spec.md`](02-loop-design/loop-spec.md)

### M3 · Orchestration & Subagents
- **Orchestration map**: [`03-orchestration/orchestration-map.md`](03-orchestration/orchestration-map.md)

### M4 · Choose What Each Agent Step Is Allowed to See
- **Memory & context plan**: [`04-memory-context/memory-and-context.md`](04-memory-context/memory-and-context.md)

### M5 · Bounds & Evals
- **Bounds & evals**: [`05-bounds-evals/bounds-and-evals.md`](05-bounds-evals/bounds-and-evals.md)

### M6 · Autonomy & Production
- **Production & autonomy plan**: [`06-autonomy/production-and-autonomy.md`](06-autonomy/production-and-autonomy.md)
- **Prototype write-up + six run captures**: [`06-autonomy/prototype.md`](06-autonomy/prototype.md)
- **Build insights**: [`06-autonomy/build-insights.md`](06-autonomy/build-insights.md)

The working agent lives in [`00-build/`](00-build/). To run it, see "How to run it" in the prototype write-up.

---

## Ship plan

### Autonomy per segment
- Me, the PM who runs Cortex → Supervised: Cortex drafts and queues on its own triggers; I approve every draft and story batch.
- My product lead → Assisted: sees only the update I approved; leadership communication stays above my line.
- A new engineering lead → Assisted: stories arrive as PRD-traced suggestions; they decide what enters the sprint.
The dial never moves the agent line: Cortex can't post, commit a date or escalate for anyone.

### Rung + eval gate
Current rung: Supervised. Nothing leaves the queue without my approval; Cortex has no post tool.
Next rung, Monday-draft lane only: bounded-autonomous (I still post).
Gate: EV-5 jailbreak 100%, EV-1 tool accuracy ≥95%, EV-2 0 unsafe steps, EV-3 recovery ≥80%, EV-4 completion ≥90%, and ≥90% of drafts approved unedited, over 8 consecutive weekly runs on real data.
Honest status: about 20 fixture runs so far, 0 above-the-line actions; no real-data window yet, so the gate hasn't started.

### Where it runs & who owns it
- Runtime: serverless functions, matching my M2 hook + Monday-cron loop; run log and task-ID log in a small database.
- On-call owner: me (the PM), with the engineering lead as backup. Leak or bound breach: kill switch first, then page the backup.
- Rollback, fastest first: kill switch → drop the dial a rung → disable a tool → revert to the last good commit.
- Monitoring: exit mix (DONE / STUCK / ESCALATED), eval pass %, escalation rate, cost per run, daily spend vs the $5 cap, trust incidents.

### Value, not activity
- Outcome: time saved on the weekly update and story prep, ≥50% vs a 2-week shadow-mode baseline; ≥90% of runs end DONE with a draft I approve.
- Cost-to-serve: ≤$0.15 model cost per completed update (today $0.05–0.13) + ≤10 min of my review.
- Trust incidents: 0 per 8-week window.
Widen rule: 8 consecutive weekly runs meeting the gate with 0 trust incidents moves the Monday lane up one rung; one incident moves it straight back down.

### How I keep it safe
- Compliance: embargoed roadmap items never reach the drafter (graded out in the roadmap tool, plus a code check on every output); run log keeps IDs, not content, 90-day TTL.
- Safety: posting, company-wide updates, dates and escalations stay above the line for everyone; no write tools; kill switch.
- Reliability: 8 iterations, 2 revisions, 90 s, $0.50/run, $5/day, 10 stories/run, all in code. Gap: a model outage crashes the run unlabelled today.
- Strategy: next, read-only Jira activity in shadow mode for 4 weeks, gated by EV-1 and EV-4 on real data.

---

## Build insights

- **Friction.** The code didn't match my design until I made it: escalations looked like successes, the critic was inconsistent, and a 10-story cap that was per call let one run queue 19.
- **Learning.** A prompt isn't a bound. The limits that held were in code or in tools Cortex doesn't have; it couldn't post in the jailbreak because there was nothing to post with.
- **Aha.** The embargoed project kept appearing because the roadmap tool fed Cortex the whole confidential roadmap. The critic was cleaning up a context problem; fixing it at the source mattered most.

---

_Certification submission, Agentic Loops for PMs Certification._
