"""Career break / sabbatical decision.

Computes runway, total opportunity cost (forgone comp + lost RSU + lost
employer match + lost compounding on retirement), and the breakeven year
post-return assuming an expected re-entry wage premium.
"""

from __future__ import annotations

from life_scenarios.scenario import ResultLine, Scenario, ScenarioResult


def evaluate(s: Scenario) -> ScenarioResult:
    p = s.profile
    d = s.decision

    break_months = float(d.get("break_months", 12))
    monthly_burn = float(p.get("monthly_burn_usd", 0))
    current_savings = float(p.get("current_savings_usd", 0))
    salary = float(p.get("salary_usd", 0))
    rsu_unvested = float(p.get("rsu_unvested_shares", 0))
    rsu_price = float(p.get("rsu_current_price", 0))
    match_rate = float(p.get("employer_401k_match_rate", 0))
    reentry_premium = float(d.get("expected_reentry_premium", 0))
    domain_switch = bool(d.get("domain_switch", False))

    runway_needed = monthly_burn * break_months
    runway_floor = monthly_burn * 3  # post-break 3-month buffer

    forgone_salary = salary * (break_months / 12)
    rsu_forfeit = rsu_unvested * rsu_price
    match_miss = salary * match_rate * (break_months / 12)
    opportunity_cost = forgone_salary + rsu_forfeit + match_miss

    new_salary = salary * (1 + reentry_premium)
    annual_premium = new_salary - salary
    breakeven_years_after = opportunity_cost / max(annual_premium, 1.0) if annual_premium > 0 else float("inf")

    lines = [
        ResultLine("runway needed", round(runway_needed, 2), f"{break_months:.0f} months × ${monthly_burn:,.0f}"),
        ResultLine("emergency buffer post-break", round(runway_floor, 2), "3 months of burn"),
        ResultLine("current savings", round(current_savings, 2), ""),
        ResultLine("savings gap (need + buffer − have)", round(runway_needed + runway_floor - current_savings, 2), ""),
        ResultLine("forgone salary", round(forgone_salary, 2), ""),
        ResultLine("RSU forfeit at departure", round(rsu_forfeit, 2), f"{rsu_unvested:,.0f} unvested × ${rsu_price:,.2f}"),
        ResultLine("missed 401(k) match", round(match_miss, 2), f"{match_rate*100:.1f}% of salary"),
        ResultLine("total opportunity cost", round(opportunity_cost, 2), "forgone salary + RSU + match"),
        ResultLine("expected re-entry salary", round(new_salary, 2), f"+{reentry_premium*100:.1f}% premium"),
        ResultLine(
            "breakeven year post-return",
            round(breakeven_years_after, 1) if breakeven_years_after != float("inf") else "never (no premium)",
            "",
        ),
    ]

    risks = []
    actions = []
    if current_savings < runway_needed + runway_floor:
        risks.append(
            f"Savings gap of ${runway_needed + runway_floor - current_savings:,.0f}. Build the floor first."
        )
        actions.append("Build savings to runway + buffer before separation.")
    if rsu_forfeit > 0:
        risks.append(
            f"Unvested RSU value at risk: ${rsu_forfeit:,.0f}. Confirm next cliff date with employer."
        )
        actions.append("Time departure within 2 weeks after the next RSU vest cliff to maximize realized comp.")
    risks.append(
        f"Health insurance: ~$850/mo COBRA modeled; budget ${850 * break_months:,.0f} for {break_months:.0f}-month break."
    )
    if domain_switch:
        risks.append(
            "Domain-switch breaks see longer re-entry timelines; expected premium may not materialize in year 1."
        )
        actions.append("Build evidence (cohort, project, certification) during the break to credibly switch.")
    actions.append("Validate the re-entry premium assumption by talking to 3 hiring managers in the target domain BEFORE leaving.")

    headline = ("opportunity cost (USD)", round(opportunity_cost, 2))

    return ScenarioResult(scenario=s, lines=lines, risks=risks, actions=actions, headline_metric=headline)
