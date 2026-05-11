"""Marriage finance planning. Generic, jurisdiction-agnostic — focused on
the financial pre-marriage decisions: account titling, prenup considerations,
combined budget delta, joint vs separate filing trade-off.
"""

from __future__ import annotations

from life_scenarios.scenario import ResultLine, Scenario, ScenarioResult


def evaluate(s: Scenario) -> ScenarioResult:
    p = s.profile
    d = s.decision

    p1_salary = float(p.get("partner_a_salary_usd", 0))
    p2_salary = float(p.get("partner_b_salary_usd", 0))
    p1_pre_marital = float(p.get("partner_a_pre_marital_assets_usd", 0))
    p2_pre_marital = float(p.get("partner_b_pre_marital_assets_usd", 0))
    wedding_budget = float(d.get("wedding_budget_usd", 0))
    same_state = bool(p.get("both_in_same_state", True))
    children_planned = bool(d.get("children_planned", True))

    income_delta = abs(p1_salary - p2_salary)
    higher = max(p1_salary, p2_salary)
    income_skew = income_delta / max(higher, 1)

    asset_imbalance = abs(p1_pre_marital - p2_pre_marital)

    # Joint filing typically saves 5-15% in federal tax vs single, with larger
    # benefit when incomes differ. Stylized estimate.
    joint_savings_pct = 0.03 + 0.08 * min(income_skew, 1.0)
    annual_joint_benefit = (p1_salary + p2_salary) * joint_savings_pct * 0.32  # times marginal rate band

    lines = [
        ResultLine("combined household income", p1_salary + p2_salary, ""),
        ResultLine("income skew (delta/higher)", round(income_skew, 3), ""),
        ResultLine("pre-marital asset imbalance", asset_imbalance, ""),
        ResultLine("estimated annual joint-filing benefit", round(annual_joint_benefit, 2), "vs both filing single"),
        ResultLine("wedding budget", wedding_budget, ""),
        ResultLine("3-month emergency fund target (combined)", round((p1_salary + p2_salary) * 0.25, 2), "25% of combined annual income"),
    ]

    risks = []
    actions = []
    if asset_imbalance > 250_000:
        risks.append(
            "Material pre-marital asset imbalance. Consider a prenuptial agreement specifying separate-vs-marital property; some jurisdictions presume commingling."
        )
        actions.append("Draft a prenup with separate counsel for each partner.")
    if income_skew > 0.4:
        risks.append("Significant income skew. Discuss expectations on spending splits (proportional vs equal) before wedding.")
    if not same_state:
        risks.append("Cross-state household — confirm domicile rules for state tax purposes.")
    if children_planned:
        actions.append("Plan healthcare-plan election timing (new dependent qualifying event) and life-insurance coverage update.")
    actions.append(
        "Title joint vs separate accounts intentionally; default state law (community property vs separate property) affects what becomes marital."
    )
    actions.append("Update beneficiaries on 401(k), IRA, life-insurance, brokerage upon marriage — automatic in some jurisdictions, not all.")

    headline = ("estimated joint-filing benefit (USD/yr)", round(annual_joint_benefit, 2))

    return ScenarioResult(scenario=s, lines=lines, risks=risks, actions=actions, headline_metric=headline)
