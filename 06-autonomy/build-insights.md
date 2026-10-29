# Build Insights: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 4, what you learned building it
>
> ✅ **What this validates:** you can reflect on what building it taught you, by the end you'll have proven the friction, the learning, and the aha that changes how you'd design your next agent.

## Friction

The code didn't match my design until I made it. An escalation used to end with the same
"approved" banner as a success, so I added three labelled exits. The critic was inconsistent until
its checks were written as numbered rules. And the 10-story cap was per call, not per run, so one
run queued 19.

## Learning

1. **A prompt isn't a bound.** The only limits that held were the ones in code or in missing
   tools. Cortex couldn't post during the jailbreak because there was nothing to post with.
2. **Context is the biggest lever.** Most of Cortex's bad drafts traced back to what it was shown,
   not to the model.
3. **Independence is what makes a critic work.** It caught mistakes Cortex made while insisting it
   hadn't.

## Aha moment

The embargoed project kept appearing in drafts in M2, M3 and M4, and I assumed the critic was
doing its job. It was, but the real cause was the roadmap tool handing Cortex the whole confidential
roadmap every run. The critic was cleaning up a **context problem**. Fixing it at the source mattered
more than any prompt change.

## What you'd do differently

Scope every read tool to the project from day one; build the bounds (timeout, daily cap, kill
switch) before adding features; write the eval cases in Module 2, not Module 5; and save every
interesting run as a replay fixture from the first week.
