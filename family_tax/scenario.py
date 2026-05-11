"""Scenario loader + dispatcher."""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Scenario:
    event: str
    parties: dict
    assets: dict
    jurisdictions: list[str]
    notes: str = ""
    raw: dict = field(default_factory=dict)


@dataclass
class TaxLine:
    jurisdiction: str
    label: str
    amount: float = 0.0
    detail: str = ""


@dataclass
class ScenarioResult:
    scenario: Scenario
    lines: list[TaxLine]
    risks: list[str]
    actions: list[str]
    forms_required: list[str]
    total_tax_usd: float

    def to_dict(self) -> dict:
        return {
            "event": self.scenario.event,
            "lines": [l.__dict__ for l in self.lines],
            "risks": self.risks,
            "actions": self.actions,
            "forms_required": self.forms_required,
            "total_tax_usd": self.total_tax_usd,
        }


def load(path: Path) -> Scenario:
    data = yaml.safe_load(path.read_text())
    return Scenario(
        event=data["event"],
        parties=data.get("parties", {}),
        assets=data.get("assets", {}),
        jurisdictions=data.get("jurisdictions", []),
        notes=data.get("notes", ""),
        raw=data,
    )


def run(scenario: Scenario) -> ScenarioResult:
    """Dispatch to the event module by name."""
    module_name = f"family_tax.events.{scenario.event}"
    mod = importlib.import_module(module_name)
    return mod.evaluate(scenario)
