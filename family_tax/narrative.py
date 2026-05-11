"""Optional LLM narrative summary. Fallback to a plain template if no model is reachable."""

from __future__ import annotations

import os

from openai import OpenAI

from .scenario import ScenarioResult


PROMPT = """You are a cross-border tax explainer. Summarize the scenario result below for a
non-specialist family member. Plain English, no jargon. Three short paragraphs:

1. What is happening, in two sentences.
2. The tax outcome, in two sentences.
3. The single most important thing to do next.

Always end with: "This is not tax advice. Consult a cross-border CPA."

Scenario: {event}
Lines:
{lines}

Risks:
{risks}

Actions:
{actions}
"""


def narrate(result: ScenarioResult) -> str:
    body = PROMPT.format(
        event=result.scenario.event,
        lines="\n".join(f"  {l.jurisdiction:3s}  {l.label}: ${l.amount:,.2f}" for l in result.lines),
        risks="\n".join(f"  - {r}" for r in result.risks) or "  (none)",
        actions="\n".join(f"  - {a}" for a in result.actions) or "  (none)",
    )
    base = os.environ.get("FAMTAX_BASE_URL", "http://localhost:8000/v1")
    model = os.environ.get("FAMTAX_MODEL", "chat")
    try:
        client = OpenAI(base_url=base, api_key="local")
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": body}],
            max_tokens=400,
            temperature=0.2,
        )
        return resp.choices[0].message.content or _template(result)
    except Exception:
        return _template(result)


def _template(result: ScenarioResult) -> str:
    return (
        f"Scenario: {result.scenario.event}\n"
        f"Total modeled tax: ${result.total_tax_usd:,.2f}\n"
        f"Top action: {result.actions[0] if result.actions else 'consult a cross-border CPA'}\n"
        "This is not tax advice. Consult a cross-border CPA."
    )
