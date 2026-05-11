"""K-12 + college education funding planner.

Computes required savings rate to fully fund each child's education given
their age, target school type, and existing balances. Handles 529 vs taxable
account trade-off (state deduction value vs flexibility).
"""

from __future__ import annotations

from life_scenarios.scenario import ResultLine, Scenario, ScenarioResult


# Annual cost models (2026, indicative, in USD). Inflate at 5% per year.
SCHOOL_TYPE_ANNUAL = {
    "public_in_state": 28_000,
    "public_out_state": 50_000,
    "private_4yr": 82_000,
    "ivy_tier": 95_000,
    "international_uk": 60_000,
    "international_eu": 30_000,
}
EDUCATION_INFLATION = 0.05


def project_total_cost(annual: float, years_until_start: int, years_in_school: int = 4) -> float:
    total = 0.0
    for yr in range(years_in_school):
        cost = annual * (1 + EDUCATION_INFLATION) ** (years_until_start + yr)
        total += cost
    return total


def required_monthly_savings(target: float, current: float, years_until_start: int, expected_return: float = 0.07) -> float:
    if years_until_start <= 0:
        return max(target - current, 0)
    months = years_until_start * 12
    monthly_r = expected_return / 12
    future_of_current = current * (1 + expected_return) ** years_until_start
    needed = max(target - future_of_current, 0)
    if needed <= 0:
        return 0.0
    return needed * monthly_r / ((1 + monthly_r) ** months - 1)


def evaluate(s: Scenario) -> ScenarioResult:
    p = s.profile
    children = p.get("children", [])
    if not children:
        return ScenarioResult(
            scenario=s,
            lines=[ResultLine("error", "no children in profile", "")],
            risks=["Profile is missing `children:` list."],
            actions=["Add children with age and target_school_type."],
        )

    lines: list[ResultLine] = []
    risks: list[str] = []
    actions: list[str] = []
    total_monthly = 0.0
    total_target = 0.0

    for child in children:
        age = int(child["age"])
        target_type = child["target_school_type"]
        current_balance = float(child.get("current_balance_usd", 0))
        years_until = max(18 - age, 1)
        annual_cost = SCHOOL_TYPE_ANNUAL.get(target_type, 50_000)
        total_cost = project_total_cost(annual_cost, years_until, years_in_school=4)
        monthly = required_monthly_savings(total_cost, current_balance, years_until)
        total_monthly += monthly
        total_target += total_cost
        lines.append(
            ResultLine(
                f"{child.get('name', 'child')} (age {age}, {target_type})",
                round(total_cost, 2),
                f"{years_until} yrs to start · needs ${monthly:,.0f}/mo",
            )
        )
        if current_balance == 0 and years_until < 10:
            risks.append(
                f"{child.get('name', 'child')}: <10 years and no savings yet. Required monthly rate is steep — start now."
            )

    lines.append(ResultLine("TOTAL target across children", round(total_target, 2), ""))
    lines.append(ResultLine("TOTAL monthly savings required", round(total_monthly, 2), ""))

    actions += [
        "Open or max-fund 529 plans where state tax deduction is available; otherwise use a flexible taxable brokerage.",
        "Confirm financial aid eligibility threshold before committing to large 529 balances (assets reduce aid).",
        "Revisit annually — costs inflate above general CPI.",
    ]
    risks.append("Aid-eligibility cliff: 529 balances in parent's name count at 5.64% in FAFSA EFC calculation.")

    headline = ("total monthly savings (USD)", round(total_monthly, 2))

    return ScenarioResult(scenario=s, lines=lines, risks=risks, actions=actions, headline_metric=headline)
