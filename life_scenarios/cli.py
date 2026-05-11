from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from . import narrative, scenario as sc


console = Console()


@click.group()
def main():
    """life-scenarios: scenario engine for major life-event decisions."""


@main.command("run")
@click.argument("path")
@click.option("--narrate/--no-narrate", default=False)
def run_cmd(path: str, narrate: bool):
    s = sc.load(Path(path))
    result = sc.run(s)

    console.print(f"\n[bold]SCENARIO[/bold]: {s.event}")
    if s.notes:
        console.print(f"[dim]{s.notes}[/dim]")
    console.print("─" * 60)

    table = Table(show_header=False)
    table.add_column("label")
    table.add_column("value", justify="right")
    table.add_column("detail")
    for line in result.lines:
        v = line.value
        if isinstance(v, (int, float)):
            v_str = f"${v:,.2f}" if abs(v) >= 1 or v == 0 else f"{v:.4f}"
        else:
            v_str = str(v)
        table.add_row(line.label, v_str, line.detail)
    console.print(table)

    if result.headline_metric:
        label, value = result.headline_metric
        if isinstance(value, (int, float)):
            console.print(f"\n[bold]headline:[/bold] {label} = ${value:,.2f}")
        else:
            console.print(f"\n[bold]headline:[/bold] {label} = {value}")

    if result.risks:
        console.print("\n[bold]RISK FLAGS[/bold]")
        for r in result.risks:
            console.print(f"  • {r}")

    if result.actions:
        console.print("\n[bold]RECOMMENDED ACTIONS[/bold]")
        for i, a in enumerate(result.actions, 1):
            console.print(f"  {i}. {a}")

    if narrate:
        console.print("\n[bold]PLAIN-ENGLISH SUMMARY[/bold]")
        console.print(narrative.narrate(result))

    console.print(
        "\n[dim]Not advice. Confirm with the appropriate specialist before acting.[/dim]"
    )


@main.command("list")
def list_cmd():
    root = Path(__file__).parent.parent / "scenarios"
    for f in sorted(root.glob("*.yaml")):
        console.print(f"  • {f.name}")


@main.command("new")
@click.option("--template", required=True, help="event template (e.g. career_break)")
def new_cmd(template: str):
    samples = {
        "career_break": _career_break_template(),
        "relocation_cost": _relocation_template(),
        "education_funding": _education_template(),
        "switch_to_self_employment": _self_employment_template(),
    }
    if template not in samples:
        console.print(f"[red]unknown template:[/red] {template}")
        console.print(f"available: {', '.join(sorted(samples))}")
        return
    click.echo(samples[template])


def _career_break_template() -> str:
    return """event: career_break
notes: 12-month sabbatical
profile:
  age: 36
  salary_usd: 250_000
  monthly_burn_usd: 11_000
  current_savings_usd: 180_000
  rsu_unvested_shares: 2_000
  rsu_current_price: 150
  employer_401k_match_rate: 0.05
decision:
  break_months: 12
  expected_reentry_premium: 0.08
  domain_switch: false
"""


def _relocation_template() -> str:
    return """event: relocation_cost
notes: cross-city relocation
profile:
  monthly_housing_usd: 4_500
  monthly_other_usd: 5_000
  household_size: 3
  owns_home_in_from: true
  home_value_usd: 950_000
  salary_usd: 280_000
  from_state: NY
  to_state: ""
decision:
  from_city: NYC
  to_city: LISBON
  one_time_moving_cost_usd: 18_000
  school_or_childcare_delta_monthly: -2_500
"""


def _education_template() -> str:
    return """event: education_funding
profile:
  children:
    - name: A
      age: 5
      target_school_type: public_in_state
      current_balance_usd: 8_000
    - name: B
      age: 2
      target_school_type: private_4yr
      current_balance_usd: 2_000
"""


def _self_employment_template() -> str:
    return """event: switch_to_self_employment
profile:
  current_w2_salary_usd: 220_000
  employer_401k_match_annual_usd: 11_000
  employer_health_contribution_annual_usd: 18_000
decision:
  expected_self_employed_billings_usd: 280_000
  structure_s_corp: true
  annual_deductible_business_expenses_usd: 20_000
"""
