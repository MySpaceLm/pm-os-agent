# Prototype: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 1, the working agent demo
>
> ✅ **What this validates:** the agent actually runs end to end, by the end you'll have proven it with real screenshots of your Cortex across the six required moments (M2 to M6).

## What it does

_One paragraph: the agent in action, end to end._

## How you built it

- **Coding agent:** _which one you directed (Claude Code / Cursor / Codex)_
- **Model + bounds:** _model used, max iterations, cost cap, queue cap_
- **Repo / config:** _path to your build in `00-build/`_
- **Live link:** _[shareable URL, optional bonus]_

## Screenshots (required, collected M2 to M6)

Real screenshots of *your* Cortex running. These are the `00-build/CORTEX-ANATOMY.md` set and they are required, a link alone is not enough.

| # | Screenshot | What it shows | From |
|---|---|---|---|
| 1 | _[img]_ | happy-path run: a real drafted update + the HITL checkpoint (queued, not posted) | M2 |
| 2 | [transcript](screenshots/02-critic-rejects.txt) | the critic rejecting a bad draft (revise/block): it failed draft 1 (named embargoed Orbit; inferred stories claimed in scope) and draft 2 (a coverage mention; "all in scope" contradiction), sent each back with reasons, and passed draft 3, which then stopped at the HITL checkpoint | M3 |
| 3 | [grounded](screenshots/03a-grounded.txt) · [withheld source](screenshots/03b-withheld-activity.txt) | a grounded update citing pulled activity + a caught hallucination. **(a)** On the ingested data pack, every claim traces to a pull: 43% vs 41%, PRs #820/#823 and issue #825 from `get_activity`; critic passed first time. **(b)** With `get_activity` withheld, Cortex invented nothing: it flagged "no tool returns merged PRs, open issues or Sev-1s," asked me to confirm no Sev-1 before sending, and took the metric only from the roadmap, saying so. The critic rejected two drafts for naming embargoed Orbit/Pulsar (the roadmap leak path) and passed the third | M4 |
| 4 | _[img]_ | jailbreak refused + escalated | M5 |
| 5 | _[img]_ | an iteration/cost/queue bound halting a runaway | M5 |
| 6 | _[img]_ | end-to-end run | M6 |

## How to run it

_Minimal steps for someone to reproduce the demo (env vars, and the command or the coding-agent prompt you used)._
