"""Sale of a major asset (real estate, business stake, large equity position).

Computes net proceeds after taxes (federal long-term capital gains + NIIT +
state) under generic US assumptions.
"""

from __future__ import annotations

from life_scenarios.scenario import ResultLine, Scenario, ScenarioResult


LTCG_TOP = 0.20
NIIT = 0.038


def evaluate(s: Scenario) -> ScenarioResult:
    sale = float(s.assets.get("sale_price_usd", 0))
    basis = float(s.assets.get("cost_basis_usd", 0))
    asset_type = s.assets.get("type", "real_estate")
    primary_residence_eligible = bool(s.assets.get("primary_residence_section_121_eligible", False))
    filing_joint = bool(s.parties.get("seller", {}).get("filing_joint", False))

    gain = max(0.0, sale - basis)

    section_121 = 500_000 if filing_joint else 250_000
    if primary_residence_eligible and asset_type == "real_estate":
        excluded = min(gain, section_121)
    else:
        excluded = 0.0

    taxable_gain = gain - excluded
    federal_tax = taxable_gain * (LTCG_TOP + NIIT)

    lines = [
        ResultLine("sale price", sale, ""),
        ResultLine("cost basis", basis, ""),
        ResultLine("gross gain", gain, ""),
        ResultLine("Section 121 exclusion", -excluded, "primary residence, 2-of-5 use test" if primary_residence_eligible else "n/a"),
        ResultLine("taxable gain", taxable_gain, ""),
        ResultLine("federal LTCG + NIIT", round(federal_tax, 2), "23.8% top rate"),
        ResultLine("net proceeds (modeled)", round(sale - federal_tax, 2), "before state tax"),
    ]

    risks = []
    actions = []
    if asset_type == "business":
        risks.append("Qualified Small Business Stock (QSBS) may exclude up to $10M or 10× basis. Check Section 1202 eligibility.")
        actions.append("Confirm QSBS qualification before sale: 5-year hold, original issuance, $50M assets test.")
    if gain > 1_000_000:
        risks.append("Single large sale crosses NIIT thresholds and bumps marginal bracket. Consider installment sale or charitable trust.")
        actions.append("Model installment sale (Section 453) and CRT/CRUT vs outright sale.")
    actions.append("Coordinate with CPA on quarterly estimated tax payments to avoid underpayment penalty.")

    headline = ("net proceeds after federal (USD)", round(sale - federal_tax, 2))
    return ScenarioResult(scenario=s, lines=lines, risks=risks, actions=actions, headline_metric=headline)
