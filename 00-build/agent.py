"""Cortex, a minimal, explicit agent loop you (and your coding agent) can read end
to end. This is the agent you ship: your PM chief-of-staff. You build it by
directing your coding agent (Claude Code / Cursor / Codex) to shape this file. You
never have to hand-write it.

Every bound the course talks about is visible right here in code, not buried in a
framework: the max-iteration counter, the cost cap, the revision cap, the
stop/escalate conditions, the auto-queue cap, and the absence of any publish tool.

Usage (ask your coding agent to run these for you, or run them yourself):
    python agent.py                # runs the happy-path task (weekly status update)
    python agent.py missing-data   # the stuck/escalate case
    python agent.py jailbreak       # the prompt-injection refusal case

Every run ends by showing the drafted status update in a FINAL STATUS UPDATE block
(or LAST DRAFT, held, if a bound trips), and saves it to run-output/. That file is
always a draft held for a human, it is never posted, there is no publish tool.

Requires ANTHROPIC_API_KEY in your environment (see .env.example). Model and bounds
are read from env so you can tune them, that tuning is your M5 deliverable.

The loop is deliberately transparent (hand-written tool-calling on the anthropic
client) so a grader can see the machinery. Keep the bounds explicit if you rework it.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import anthropic

import tools
from critic import review
from prompts import CORTEX_SYSTEM

try:  # load .env if python-dotenv is installed; harmless if it isn't
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# --- Bounds (your M5 deliverable: tune these and justify them) ----------------
MODEL = os.environ.get("CORTEX_MODEL", "claude-sonnet-5-5")
EFFORT = os.environ.get("CORTEX_EFFORT", "medium")  # low | medium | high | xhigh | max
MAX_ITERATIONS = int(os.environ.get("CORTEX_MAX_ITERATIONS", "8"))
MAX_REVISIONS = int(os.environ.get("CORTEX_MAX_REVISIONS", "2"))
COST_CAP_USD = float(os.environ.get("CORTEX_COST_CAP_USD", "0.50"))
DAILY_CAP_USD = float(os.environ.get("CORTEX_DAILY_CAP_USD", "5.00"))  # all runs, per UTC day
TIMEOUT_S = float(os.environ.get("CORTEX_TIMEOUT_S", "90"))  # wall clock, per run
MAX_QUEUE_ITEMS = int(os.environ.get("CORTEX_MAX_QUEUE_ITEMS", "10"))  # stories, per run
# Kill switch: set CORTEX_KILL=1, or create this file, and every run halts at its next step.
KILL_FILE = Path(__file__).parent / "KILL"
# Rough $ per 1M tokens for your chosen model, set to match its pricing.
PRICE_IN = float(os.environ.get("CORTEX_PRICE_IN_PER_M", "2.00"))
PRICE_OUT = float(os.environ.get("CORTEX_PRICE_OUT_PER_M", "10.00"))

TOOL_SCHEMAS = [
    {"name": "get_project", "description": "Look up a project by its ID (status, flags, linked PRD).",
     "input_schema": {"type": "object", "properties": {
         "project_id": {"type": "string"}}, "required": ["project_id"]}},
    {"name": "get_activity",
     "description": "Pull recent engineering activity for a project (merged PRs, open issues, Sev-1s).",
     "input_schema": {"type": "object", "properties": {
         "project_id": {"type": "string"}}, "required": ["project_id"]}},
    {"name": "search_past_updates",
     "description": "Search previous status updates and decisions for tone and precedent.",
     "input_schema": {"type": "object", "properties": {
         "query": {"type": "string"}}, "required": []}},
    {"name": "get_roadmap",
     "description": "Return the roadmap. Some items are flagged confidential/embargoed.",
     "input_schema": {"type": "object", "properties": {
         "query": {"type": "string"}}, "required": []}},
    {"name": "get_norms", "description": "Return the team norms / PM playbook the agent must follow.",
     "input_schema": {"type": "object", "properties": {
         "query": {"type": "string"}}, "required": []}},
    {"name": "propose_stories",
     "description": "Queue a set of backlog stories for human approval (creates nothing; rejected above the item cap).",
     "input_schema": {"type": "object", "properties": {
         "project_id": {"type": "string"},
         "stories": {"type": "array", "items": {"type": "string"}},
         "reason": {"type": "string"}}, "required": ["project_id", "stories"]}},
]


def call_model(client: anthropic.Anthropic, output_config: dict | None = None, **kwargs):
    """One model call. If the model declines on safety grounds, the API re-runs the
    request on Anthropic's recommended fallback model inside the same call."""
    return client.beta.messages.create(
        model=MODEL, max_tokens=16000,
        output_config={"effort": EFFORT, **(output_config or {})},
        betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kwargs)


def usage_cost(usage) -> float:
    tokens_in = (usage.input_tokens + (usage.cache_creation_input_tokens or 0)
                 + (usage.cache_read_input_tokens or 0))
    return (tokens_in * PRICE_IN + usage.output_tokens * PRICE_OUT) / 1_000_000


class Bounds:
    """Tracks spend and trips the cost cap. This is enforced OUTSIDE the model."""

    def __init__(self):
        self.cost = 0.0

    def add(self, usage) -> None:
        self.cost += usage_cost(usage)

    def over_cap(self) -> bool:
        return self.cost >= COST_CAP_USD


OUTPUT_DIR = Path(__file__).parent / "run-output"


def spent_today() -> float:
    """Total logged spend for today (UTC), across every run, from run-log.jsonl."""
    log = OUTPUT_DIR / "run-log.jsonl"
    if not log.exists():
        return 0.0
    today = datetime.now(timezone.utc).date().isoformat()
    total = 0.0
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("time", "").startswith(today):
            total += float(entry.get("cost_usd", 0))
    return total


def kill_engaged() -> bool:
    return os.environ.get("CORTEX_KILL") == "1" or KILL_FILE.exists()

# The three exits from loop-spec.md §3. Every run ends in exactly one of them.
DONE, STUCK, ESCALATED = "DONE", "STUCK", "ESCALATED"
EXIT_BANNERS = {
    DONE: "FINAL STATUS UPDATE (DONE: critic-approved draft, queued, NOT posted)",
    STUCK: "STUCK (held for you, NOT posted): Cortex gave up",
    ESCALATED: "ESCALATED (handed to you, NOT posted): a human must take it from here",
}
# Stuck (a): a required read tool can't find the project.
REQUIRED_TOOLS = {"get_project", "get_activity"}


def banner(text: str) -> None:
    print(f"\n{'=' * 64}\n{text}\n{'=' * 64}")


def emit_deliverable(which: str, draft: str, *, outcome: str,
                     reason: str, cost: float, save_draft: bool = True) -> None:
    """Surface AND persist Cortex's drafted status update so it can't get lost in
    the scroll-back. This is still a DRAFT held for human review, never a post,
    there is no publish tool.

    Runs on every exit, labelled with which of the three exits fired (DONE, STUCK,
    ESCALATED), and appends one line to run-output/run-log.jsonl.
    """
    banner(EXIT_BANNERS[outcome])
    if draft.strip():
        print(draft.rstrip())
    else:
        print("(Cortex stopped before it produced a draft, nothing to show.)")
    print(f"\nExit: {outcome}, {reason}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    if draft.strip() and save_draft:
        out = OUTPUT_DIR / f"status-update-{which}.md"
        out.write_text(
            f"<!-- Cortex draft, {outcome}; NOT posted. Run cost ~ ${cost:.4f}. -->\n"
            f"<!-- {reason} -->\n\n{draft.rstrip()}\n", encoding="utf-8")
        print(f"\nSaved draft -> {out.relative_to(Path(__file__).parent)}  "
              f"(for your review, nothing was posted)")
    with open(OUTPUT_DIR / "run-log.jsonl", "a", encoding="utf-8") as log:
        log.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                              "task": which, "outcome": outcome, "reason": reason,
                              "cost_usd": round(cost, 4)}) + "\n")


def run(which: str = "happy") -> None:
    # Timeout bound: no single model call may outlive the run's budget, and the
    # loop below checks the wall clock before every step.
    client = anthropic.Anthropic(timeout=TIMEOUT_S, max_retries=1)
    started = time.monotonic()
    bounds = Bounds()
    task = tools.get_task(which)
    if "error" in task:
        print(task)
        return

    banner(f"CORTEX RUN, fixture: task-{which}  (auto-queue cap {MAX_QUEUE_ITEMS} items)")
    print(task["body"])

    messages = [
        {"role": "user", "content": f"PM task brief:\n\n{task['body']}"},
    ]
    source_log: list[str] = [task["body"]]
    revisions = 0
    last_draft = ""
    queued = 0  # stories queued so far in THIS run (the per-run commitment cap)
    daily_before = spent_today()

    for step in range(1, MAX_ITERATIONS + 1):
        if kill_engaged():
            # Kill switch: halt now and discard what this run queued; keep no draft.
            emit_deliverable(which, last_draft, outcome=STUCK, save_draft=False,
                             reason=f"kill switch engaged; {queued} queued stories discarded",
                             cost=bounds.cost)
            return
        if time.monotonic() - started >= TIMEOUT_S:
            emit_deliverable(which, last_draft, outcome=STUCK,
                             reason=f"stuck (e): timeout, {TIMEOUT_S:.0f}s per run",
                             cost=bounds.cost)
            return
        if bounds.over_cap():
            reason = f"stuck (d): cost cap ${COST_CAP_USD} hit at ${bounds.cost:.4f}"
            emit_deliverable(which, last_draft, outcome=STUCK,
                             reason=reason, cost=bounds.cost)
            return
        if daily_before + bounds.cost >= DAILY_CAP_USD:
            emit_deliverable(which, last_draft, outcome=STUCK,
                             reason=f"stuck (d): daily cap ${DAILY_CAP_USD:.2f} reached "
                                    f"(${daily_before + bounds.cost:.4f} spent today)",
                             cost=bounds.cost)
            return

        try:
            resp = call_model(client, system=CORTEX_SYSTEM, messages=messages,
                              tools=TOOL_SCHEMAS)
        except anthropic.APITimeoutError:
            emit_deliverable(which, last_draft, outcome=STUCK,
                             reason=f"stuck (e): model call timed out after {TIMEOUT_S:.0f}s",
                             cost=bounds.cost)
            return
        bounds.add(resp.usage)
        # Keep the whole assistant turn (thinking blocks included) in the history.
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason == "refusal":
            emit_deliverable(which, last_draft, outcome=ESCALATED,
                             reason="model declined the request (refusal)",
                             cost=bounds.cost)
            return

        tool_calls = [b for b in resp.content if b.type == "tool_use"]
        if tool_calls:
            tool_results = []
            missing = []
            for call in tool_calls:
                fn = call.name
                args = call.input or {}
                if fn == "propose_stories":
                    asked = args.get("stories") or []
                    asked = [asked] if isinstance(asked, str) else asked
                    if queued + len(asked) > MAX_QUEUE_ITEMS:
                        # Per-run commitment cap: re-queuing can't stack past the cap.
                        result = {"status": "rejected", "error": "run_exceeds_queue_cap",
                                  "already_queued_this_run": queued,
                                  "requested": len(asked), "cap_items": MAX_QUEUE_ITEMS,
                                  "action": "escalate to a human; do not re-queue"}
                    else:
                        result = tools.TOOLS[fn](**args)
                        if result.get("status") == "queued_for_approval":
                            queued += result.get("count", 0)
                else:
                    result = tools.TOOLS[fn](**args)
                source_log.append(f"{fn}({args}) -> {json.dumps(result)}")
                print(f"\n[step {step}] TOOL {fn}({args})")
                print(f"          -> {json.dumps(result)[:300]}")
                if fn in REQUIRED_TOOLS and result.get("error") == "project_not_found":
                    missing.append(f"{fn}({args}) -> project_not_found")
                tool_results.append({"type": "tool_result", "tool_use_id": call.id,
                                     "content": json.dumps(result)})
            if missing:
                # Stuck (a), detected by the loop, not the model: don't guess, stop.
                emit_deliverable(which, last_draft, outcome=STUCK,
                                 reason="stuck (a): required data missing: " + "; ".join(missing),
                                 cost=bounds.cost)
                return
            messages.append({"role": "user", "content": tool_results})
            continue

        # No tool calls => Cortex produced a proposed output. Validate it.
        proposed = "".join(b.text for b in resp.content if b.type == "text")
        last_draft = proposed
        print(f"\n[step {step}] PROPOSED OUTPUT:\n{proposed}")

        banner("CRITIC, independent validation")
        try:
            verdict = review(client, call_model, proposed, "\n".join(source_log))
        except anthropic.APITimeoutError:
            emit_deliverable(which, last_draft, outcome=STUCK,
                             reason=f"stuck (e): critic call timed out after {TIMEOUT_S:.0f}s",
                             cost=bounds.cost)
            return
        # Count critic spend too.
        bounds.add(verdict["_usage"])
        # Deterministic edge (check 3 in code): an output that names an embargoed
        # project fails, whatever the critic said. A model judge can slip; a string
        # match can't be talked out of it.
        leaked = [name for name in tools.embargoed_project_names()
                  if name.lower() in proposed.lower()]
        if leaked:
            verdict["verdict"] = "fail"
            verdict["reasons"] = list(verdict.get("reasons", [])) + [
                f"Check 3 (deterministic, in code): the output names an embargoed project "
                f"({', '.join(leaked)}). Remove every mention, including as 'left out' "
                f"or when describing a request."]
        print(json.dumps({k: v for k, v in verdict.items() if k != "_usage"}, indent=2))

        if verdict["verdict"] == "pass":
            if proposed.lstrip().startswith("ESCALATE:"):
                first_line = proposed.strip().splitlines()[0]
                emit_deliverable(which, proposed, outcome=ESCALATED,
                                 reason=f"Cortex escalated: {first_line[len('ESCALATE:'):].strip()}",
                                 cost=bounds.cost)
                return
            banner(f"HITL CHECKPOINT, status update + any proposed stories queued for "
                   f"your review. Nothing posted, no commitments made. "
                   f"Run cost ≈ ${bounds.cost:.4f}")
            emit_deliverable(which, proposed, outcome=DONE,
                             reason="success: critic passed, draft queued", cost=bounds.cost)
            return

        if revisions >= MAX_REVISIONS:
            emit_deliverable(which, last_draft, outcome=STUCK,
                             reason=f"stuck (b): critic rejected {MAX_REVISIONS} revisions "
                                    f"(revision cap)", cost=bounds.cost)
            return

        revisions += 1
        print(f"\n-> critic rejected; revision {revisions}/{MAX_REVISIONS}")
        messages.append({"role": "user", "content":
                         "A validator rejected that for these reasons: "
                         f"{verdict['reasons']}. Fix it or escalate."})

    emit_deliverable(which, last_draft, outcome=STUCK,
                     reason=f"stuck (c): {MAX_ITERATIONS} iterations without a passing draft",
                     cost=bounds.cost)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "happy")
