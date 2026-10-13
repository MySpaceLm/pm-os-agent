"""Independent validator (M3). A separate model call that never saw the drafting
context, so it can't inherit the draft's blind spots. Returns a pass/fail verdict.
The revision cap that stops a critic<->drafter loop lives in `agent.py`.
"""

from __future__ import annotations

import json

from prompts import CRITIC_SYSTEM


VERDICT_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["pass", "fail"]},
        "reasons": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["verdict", "reasons"],
    "additionalProperties": False,
}


def review(client, call_model, proposed_output: str, source_data: str) -> dict:
    """Return {"verdict": "pass"|"fail", "reasons": [...]} for a proposed output.

    `call_model(client, **kwargs)` is the same model call Cortex uses (agent.py), so
    the critic runs on the same model and settings but in a fresh conversation.
    """
    resp = call_model(
        client,
        system=CRITIC_SYSTEM,
        messages=[
            {"role": "user", "content":
                f"SOURCE DATA Cortex used:\n{source_data}\n\n"
                f"CORTEX PROPOSED OUTPUT:\n{proposed_output}"},
        ],
        output_config={"format": {"type": "json_schema", "schema": VERDICT_SCHEMA}},
    )
    try:
        if resp.stop_reason == "refusal":
            raise ValueError("critic call was declined")
        text = next(b.text for b in resp.content if b.type == "text")
        verdict = json.loads(text)
    except (StopIteration, json.JSONDecodeError, ValueError):
        verdict = {"verdict": "fail", "reasons": ["critic returned unparseable output"]}
    verdict["_usage"] = resp.usage
    return verdict
