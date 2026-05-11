"""Scenario loader + dispatcher."""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Scenario:
    event: str
    profile: dict
    decision: dict
    parties: dict
    assets: dict
    jurisdictions: list[str]
    notes: str = ""
    raw: dict = field(default_factory=dict)


@dataclass
class ResultLine:
    label: str
    value: float | str
    detail: str = ""


@dataclass
class ScenarioResult:
    scenario: Scenario
    lines: list[ResultLine]
    risks: list[str]
    actions: list[str]
    headline_metric: tuple[str, float] | None = None

    def to_dict(self) -> dict:
        return {
            "event": self.scenario.event,
            "lines": [l.__dict__ for l in self.lines],
            "risks": self.risks,
            "actions": self.actions,
            "headline": self.headline_metric,
        }


def load(path: Path) -> Scenario:
    data = yaml.safe_load(path.read_text())
    return Scenario(
        event=data["event"],
        profile=data.get("profile", {}),
        decision=data.get("decision", {}),
        parties=data.get("parties", {}),
        assets=data.get("assets", {}),
        jurisdictions=data.get("jurisdictions", []),
        notes=data.get("notes", ""),
        raw=data,
    )


def run(scenario: Scenario) -> ScenarioResult:
    """Dispatch to the event module by name."""
    module_name = f"life_scenarios.events.{scenario.event}"
    mod = importlib.import_module(module_name)
    return mod.evaluate(scenario)
