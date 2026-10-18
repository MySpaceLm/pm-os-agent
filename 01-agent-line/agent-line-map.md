# Agent Line Map: Cortex PM Chief-of-Staff Agent

> Module 1 · The Agent Line
>
> ✅ **What this validates:** every risky action has a clear owner, by the end you'll have proven an above/below-the-line map with HITL checkpoints, scored on reversibility, blast radius, and measurability.

## The workflow, decision by decision

List every discrete decision or action in your agent's workflow, then score each one and place it **above** the line (a human owns it) or **below** (the agent owns it). Borderline calls get an HITL checkpoint.

| Decision / action | Reversibility (H/M/L) | Blast radius (H/M/L) | Measurability (H/M/L) | Above / Below | HITL? |
|---|---|---|---|---|---|
| 1. Pull project state + activity | H | L | H | Below | · |
| 2. Decide relevant context | H | M | M | Below | PM reviews the draft + a list of what Cortex left out |
| 3. Draft the update | H | L | M | Below | Critic checks the facts, then PM reviews the draft |
| 4. Decide tone / commitment level | M | H | L | Above | Cortex suggests a status with evidence; PM decides |
| 5. Flag at-risk / escalation | H | L | M | Below | PM reviews each flag + a list of what Cortex checked and found clear |
| 6. Choose what to escalate | L | H | M | Above | Cortex recommends what and to whom; PM decides and sends |
| 7. Propose a story batch (capped) | H | L | M | Below | PM approves each story, each traced to a PRD item |
| 8a. Post an update to the team channel | L | M | M | Above | PM posts it |
| 8b. Approve a company-wide update | L | H | H | Above | PM approves and posts; never Cortex |

## Agent anatomy (sketch)

- **Model:** Claude Sonnet 5.5 (effort: medium, ~$0.045/run) by default; escalate to Claude Opus 5.5 only for the above-the-line suggestions, the status suggestion (action 4) and the escalation recommendation (action 6), because they're high-stakes.
- **Tools:** read-only: `get_project`, `get_activity`, `search_past_updates`, `get_roadmap`, `get_norms` · capped: `propose_stories` (queues for approval, creates nothing, rejects batches over 10) · deliberately absent: post, create, merge, commit.
- **Memory:** nothing persists between runs; each run re-reads the roadmap, norms and past updates from source. The run's conversation is discarded; only the draft is saved to `run-output/` for PM review.
- **Loop:** _placeholder, defined in M2 loop-spec.md_
- **Bounds:** _placeholder, defined in M5 bounds-and-evals.md_
- **Evals:** _placeholder, defined in M5 bounds-and-evals.md_

## The golden rule, applied

- **1. Pull project state + activity** sits below the line because it's easy to reverse (just re-run it), has a low blast radius since it only reads data and shares nothing, and is easy to verify against the sources. Deciding factor: blast radius.
- **2. Decide relevant context** sits below the line with a checkpoint because it's easy to reverse (it only shapes a draft), has a medium blast radius if an omission slips through, and is only partly verifiable since omissions are hard to spot, so the PM reviews the draft plus a list of what Cortex left out. Deciding factor: measurability.
- **3. Draft the update** sits below the line with a checkpoint because it's easy to reverse (a draft I can edit), has a low blast radius since the draft never leaves the queue, and is partly verifiable: the critic checks the facts, but the PM judges the quality. Deciding factor: measurability.
- **4. Decide tone / commitment level** sits above the line because it's only partly reversible once leadership has read it, has a high blast radius since it sets leadership expectations, and is hard to verify until the date holds or slips, so Cortex suggests a status with evidence and the PM decides. Deciding factor: blast radius.
- **5. Flag at-risk / escalation** sits below the line with a checkpoint because a false alarm is easy to dismiss, it has a low blast radius since a flag only goes to me, and it's only partly verifiable because missed flags are invisible, so the PM reviews each flag plus a list of what Cortex checked and found clear. Deciding factor: measurability.
- **6. Choose what to escalate** sits above the line because it's hard to reverse once people have heard it, has a high blast radius since escalating pulls other people in, and is only partly verifiable, so Cortex recommends what to escalate and to whom and the PM decides and sends. Deciding factor: blast radius.
- **7. Propose a story batch (capped)** sits below the line with a checkpoint because it's easy to reverse (nothing is created until I approve), has a low blast radius since the 10-story cap limits it and nothing reaches the team without me, and is only partly verifiable since story choice is a product judgment, so the PM approves each story, each traced to a PRD item. Deciding factor: measurability.
- **8a. Post an update to the team channel** sits above the line because it's hard to reverse (people have already read it), has a medium blast radius since the team has context and corrects fast, and is only partly verifiable, so the PM posts it. Deciding factor: reversibility.
- **8b. Approve a company-wide update** sits above the line because it's hard to reverse once everyone has read it, has a high blast radius since it reaches the whole company at once, and is easy to verify afterward, which doesn't save it, because one red is enough. So the PM approves and posts it, never Cortex. Deciding factor: blast radius.

## Hardest call

**8a, posting an update to the team channel.** The case for below the line was real: it's my own squad, they already have the context, and a mistake gets corrected in the thread within minutes, so the blast radius is only medium. What settled it was reversibility: once people have already read it, a correction doesn't undo it. So it stays above the line and I post it myself. **Deciding axis: reversibility.**
