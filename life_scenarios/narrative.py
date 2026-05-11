"""Optional LLM narrative summary."""

from __future__ import annotations

import os

from openai import OpenAI

from .scenario import ScenarioResult


PROMPT = """You are an experienced financial planner who explains decisions clearly to clients.

Summarize the scenario result below for a non-specialist reader. Plain English. Three short paragraphs:
1. What is being decided, in two sentences.
2. The key numbers and what they mean.
3. The single most important next action.

End with: "This is not advice. Consult a qualified advisor before acting."

Scenario: {event}
Headline: {headline}

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
        headline=str(result.headline_metric),
        lines="\n".join(f"  {l.label}: {l.value}" for l in result.lines),
        risks="\n".join(f"  - {r}" for r in result.risks) or "  (none)",
        actions="\n".join(f"  - {a}" for a in result.actions) or "  (none)",
    )
    base = os.environ.get("LIFE_SCENARIOS_BASE_URL", "http://localhost:8000/v1")
    model = os.environ.get("LIFE_SCENARIOS_MODEL", "chat")
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
    h = result.headline_metric or ("", 0)
    return (
        f"Scenario: {result.scenario.event}\n"
        f"Headline: {h[0]} = {h[1]}\n"
        f"Top action: {result.actions[0] if result.actions else 'consult a qualified advisor'}\n"
        "This is not advice. Consult a qualified advisor before acting."
    )
