from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from . import narrative, scenario as sc


console = Console()


@click.group()
def main():
    """family-tax-scenarios: international family life-event tax simulator."""


@main.command("run")
@click.argument("path")
@click.option("--narrate/--no-narrate", default=False, help="Add an LLM narrative summary.")
def run_cmd(path: str, narrate: bool):
    s = sc.load(Path(path))
    result = sc.run(s)

    console.print(f"\n[bold]SCENARIO[/bold]: {s.event}")
    if s.notes:
        console.print(f"[dim]{s.notes}[/dim]")
    console.print("─" * 60)

    table = Table(show_header=False)
    table.add_column("jur")
    table.add_column("label")
    table.add_column("amount", justify="right")
    for line in result.lines:
        amt = f"${line.amount:,.2f}" if line.amount else "$0"
        table.add_row(line.jurisdiction, line.label, amt)
    console.print(table)

    console.print(f"[bold]total modeled tax:[/bold] ${result.total_tax_usd:,.2f}")

    if result.forms_required:
        console.print("\n[bold]FORMS REQUIRED[/bold]")
        for f in result.forms_required:
            console.print(f"  • {f}")

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
        "\n[dim]This is not tax advice. Confirm all figures with a cross-border CPA before acting.[/dim]"
    )


@main.command("list")
def list_cmd():
    root = Path(__file__).parent.parent / "scenarios"
    for f in sorted(root.glob("*.yaml")):
        console.print(f"  • {f.name}")
