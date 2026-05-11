"""Switch from W-2 to self-employment (1099 / S-corp).

Models the comp trade-off: lose W-2 benefits (employer-paid health, 401k
match, employer payroll taxes) but gain (deductible business expenses,
solo 401k, QBI deduction, no double FICA on S-corp distributions).
"""

from __future__ import annotations

from life_scenarios.scenario import ResultLine, Scenario, ScenarioResult


def evaluate(s: Scenario) -> ScenarioResult:
    p = s.profile
    d = s.decision

    w2_salary = float(p.get("current_w2_salary_usd", 0))
    employer_match = float(p.get("employer_401k_match_annual_usd", 0))
    employer_health = float(p.get("employer_health_contribution_annual_usd", 0))
    expected_billings = float(d.get("expected_self_employed_billings_usd", 0))
    s_corp = bool(d.get("structure_s_corp", False))
    deductible_expenses = float(d.get("annual_deductible_business_expenses_usd", 0))

    # W-2 total comp
    w2_total = w2_salary + employer_match + employer_health

    # Self-employed gross to comparable net
    self_gross = expected_billings - deductible_expenses
    self_health = -12_000  # estimated marketplace coverage net of subsidies
    # FICA: self-employment is 15.3% on first wage base; under S-corp, FICA only on reasonable salary, not distributions
    if s_corp:
        reasonable_salary = min(self_gross * 0.4, 150_000)
        se_tax = reasonable_salary * 0.153
    else:
        se_tax = min(self_gross, 176_100) * 0.153

    # Solo 401k: can contribute up to ~$70k as employer+employee
    solo_401k_potential = min(self_gross * 0.25, 70_000)
    qbi_deduction = self_gross * 0.20 * 0.32 if self_gross < 383_900 else 0  # 20% of QBI × ~32% marginal rate

    self_net = self_gross - se_tax + qbi_deduction - 12_000  # health out-of-pocket
    delta = self_net - w2_total

    lines = [
        ResultLine("W-2 salary", w2_salary, ""),
        ResultLine("W-2 401k match (annual)", employer_match, ""),
        ResultLine("W-2 employer health (annual)", employer_health, ""),
        ResultLine("W-2 total comp (modeled)", w2_total, ""),
        ResultLine("self-employed billings", expected_billings, ""),
        ResultLine("less: deductible business expenses", deductible_expenses, ""),
        ResultLine("self-employed gross (after expenses)", self_gross, ""),
        ResultLine("self-employment tax (FICA equiv)", -se_tax, "S-corp shields distributions" if s_corp else "full SE tax"),
        ResultLine("QBI deduction value (estimated)", qbi_deduction, ""),
        ResultLine("health insurance out-of-pocket (estimated)", -12_000, "marketplace, family"),
        ResultLine("self-employed net (modeled)", self_net, ""),
        ResultLine("delta vs W-2 total comp", delta, "positive = self-employment better"),
        ResultLine("solo 401k contribution headroom", solo_401k_potential, "vs $23,000 W-2 401k max"),
    ]

    risks = []
    actions = []
    if delta < 0:
        risks.append(
            f"Modeled delta is negative (${delta:,.0f}). Need ${(w2_total - self_net):,.0f} more billings/year to break even."
        )
    risks.append("Self-employment income is lumpy; budget for quarterly estimated taxes and uneven months.")
    risks.append("First year: COBRA bridge (~$1,500/mo family) before marketplace effective date.")
    if s_corp:
        actions.append("Document 'reasonable salary' methodology — IRS scrutinizes S-corp salary/distribution split.")
        actions.append("File S-corp election (Form 2553) within 2 months 15 days of starting.")
    actions.append("Open Solo 401(k) before December 31 of year 1 — funding deadline is the next tax filing date.")
    actions.append("Talk to a CPA who has at least 20 self-employed clients before structuring.")

    headline = ("net delta vs W-2 (USD)", round(delta, 2))

    return ScenarioResult(scenario=s, lines=lines, risks=risks, actions=actions, headline_metric=headline)
