"""Cross-city or cross-country relocation cost model.

Combines:
  - cost-of-living delta (housing + general)
  - moving costs (1-time)
  - state-income tax delta (US states or stylized national rate)
  - real-estate sale costs (if owned)
  - school / childcare delta
"""

from __future__ import annotations

from life_scenarios.scenario import ResultLine, Scenario, ScenarioResult


# Stylized monthly cost-of-living indices (NYC=100). Indicative only.
COL_INDEX = {
    "NYC": 100, "SF": 105, "LA": 88, "BOS": 86, "DC": 84, "SEA": 82,
    "AUS": 70, "CHI": 72, "MIA": 78, "DEN": 70,
    "LONDON": 92, "PARIS": 80, "BERLIN": 60, "MILAN": 64, "LISBON": 55, "BARCELONA": 58,
    "SINGAPORE": 90, "TOKYO": 75,
}

# State income tax top marginal (illustrative)
STATE_RATE = {
    "CA": 0.13, "NY": 0.10, "WA": 0.0, "TX": 0.0, "FL": 0.0,
    "MA": 0.09, "IL": 0.05, "CO": 0.044,
}


def evaluate(s: Scenario) -> ScenarioResult:
    p = s.profile
    d = s.decision

    from_city = d.get("from_city", "NYC").upper()
    to_city = d.get("to_city", "LISBON").upper()
    monthly_housing = float(p.get("monthly_housing_usd", 4000))
    monthly_other = float(p.get("monthly_other_usd", 5000))
    household_size = int(p.get("household_size", 2))
    moving_cost = float(d.get("one_time_moving_cost_usd", 12_000))
    owns_home = bool(p.get("owns_home_in_from", False))
    home_value = float(p.get("home_value_usd", 0))
    salary = float(p.get("salary_usd", 0))
    from_state = p.get("from_state", "").upper()
    to_state = p.get("to_state", "").upper()
    school_change_monthly = float(d.get("school_or_childcare_delta_monthly", 0))

    from_col = COL_INDEX.get(from_city, 100)
    to_col = COL_INDEX.get(to_city, 100)
    col_ratio = to_col / from_col

    new_housing = monthly_housing * col_ratio
    new_other = monthly_other * col_ratio
    monthly_delta = (new_housing + new_other + school_change_monthly) - (monthly_housing + monthly_other)
    annual_delta_living = monthly_delta * 12

    # State tax delta
    state_delta = salary * (STATE_RATE.get(to_state, 0) - STATE_RATE.get(from_state, 0))

    # Home sale costs (~7% of value: agent fees, taxes, prep)
    home_sale_friction = home_value * 0.07 if owns_home else 0.0

    # 5-year projection: net cost = year1 (moving + friction + delta) + 4 × delta
    year1_one_time = moving_cost + home_sale_friction
    five_year_net = year1_one_time + 5 * (annual_delta_living + state_delta)

    lines = [
        ResultLine("from city / to city", f"{from_city} → {to_city}", ""),
        ResultLine("cost-of-living ratio", round(col_ratio, 3), f"index {to_col}/{from_col}"),
        ResultLine("new monthly housing (modeled)", round(new_housing, 2), ""),
        ResultLine("new monthly other (modeled)", round(new_other, 2), ""),
        ResultLine("monthly cost delta", round(monthly_delta, 2), ""),
        ResultLine("annual living delta", round(annual_delta_living, 2), ""),
        ResultLine("annual state-tax delta", round(state_delta, 2), f"{from_state or 'n/a'} → {to_state or 'n/a'}"),
        ResultLine("one-time moving cost", round(moving_cost, 2), ""),
        ResultLine("home sale friction (7%)", round(home_sale_friction, 2), "agent + taxes + prep" if owns_home else "n/a"),
        ResultLine("5-year net cost (positive = expensive)", round(five_year_net, 2), ""),
    ]

    risks = []
    actions = []
    if to_col > from_col * 1.1:
        risks.append("Target city is materially more expensive. Validate housing actually achievable at modeled rate.")
    if owns_home:
        risks.append("Selling primary residence has long tail risks (timing, capital gains, replacement market).")
        actions.append("Get 3 independent market appraisals before committing.")
    if household_size > 1 and school_change_monthly == 0:
        risks.append("School / childcare delta is set to zero. If you have kids, this is the single largest variable.")
        actions.append("Model school options explicitly: public, international, bilingual, private. Set school_or_childcare_delta_monthly.")
    if to_city in {"LONDON", "PARIS", "BERLIN", "MILAN", "LISBON", "BARCELONA", "SINGAPORE", "TOKYO"}:
        risks.append("Cross-border move: visa, tax-residency timing, social security totalization, and healthcare enrollment are critical.")
        actions.append("Consult a cross-border tax advisor BEFORE the move date. Tax residency often pivots on physical-presence days.")

    headline = ("5-year net cost (USD)", round(five_year_net, 2))

    return ScenarioResult(scenario=s, lines=lines, risks=risks, actions=actions, headline_metric=headline)
