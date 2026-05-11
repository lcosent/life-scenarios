"""US-resident sells a primary residence in their home country.

US rule: Section 121 exclusion ($250k single, $500k joint) applies if you've
owned and used the property as primary residence for 2 of the last 5 years.
Foreign-country tax (paid abroad) is generally creditable via Form 1116.
Italy: capital gains on primary residence held >5 years are exempt.
"""

from __future__ import annotations

from family_tax.scenario import Scenario, ScenarioResult, TaxLine


SECTION_121_SINGLE = 250_000
SECTION_121_JOINT = 500_000
US_LTCG_TOP = 0.20
NIIT = 0.038
ITALY_CAPGAIN_RATE = 0.26


def evaluate(s: Scenario) -> ScenarioResult:
    sale_usd = float(s.assets.get("sale_price_usd", 0.0))
    basis_usd = float(s.assets.get("cost_basis_usd", 0.0))
    held_years = float(s.assets.get("held_years", 0.0))
    used_as_primary_residence_5y = bool(s.assets.get("used_as_primary_residence_5y"))
    married_joint = bool(s.parties.get("seller", {}).get("filing_joint"))
    country = s.parties.get("property", {}).get("country", "ITA")

    gain = max(0.0, sale_usd - basis_usd)
    lines = []
    risks = []
    actions = []
    forms = []

    section_121 = SECTION_121_JOINT if married_joint else SECTION_121_SINGLE
    if used_as_primary_residence_5y:
        excluded = min(gain, section_121)
        taxable_us = gain - excluded
        lines.append(
            TaxLine(
                "US",
                "Section 121 exclusion",
                -excluded,
                f"${section_121:,} excluded ({'joint' if married_joint else 'single'} filer).",
            )
        )
    else:
        taxable_us = gain
        risks.append(
            "Did not meet 2-of-last-5-years use test. Section 121 exclusion not available."
        )

    us_tax = taxable_us * (US_LTCG_TOP + NIIT)
    if taxable_us > 0:
        lines.append(
            TaxLine(
                "US",
                "US capital gains + NIIT",
                round(us_tax, 2),
                f"Assumes top long-term rate ({US_LTCG_TOP*100:.0f}%) + NIIT ({NIIT*100:.1f}%). Actual depends on bracket.",
            )
        )

    if country == "ITA":
        if held_years >= 5:
            lines.append(
                TaxLine("IT", "Italy capital gains", 0.0, "Held > 5 years; primary residence exempt.")
            )
        else:
            it_tax = gain * ITALY_CAPGAIN_RATE
            lines.append(TaxLine("IT", "Italy capital gains", round(it_tax, 2), "26% flat on gain."))
            risks.append("Italian capital gains may be creditable against US tax via Form 1116.")
            forms.append("Form 1116 (Foreign Tax Credit)")
    else:
        lines.append(
            TaxLine(country, "Foreign capital gains", 0.0, "Local rules not modeled — confirm locally.")
        )

    if gain > 0:
        forms.append("Form 8949 + Schedule D")
        actions.append("Convert sale price and basis at appropriate FX rate (basis at acquisition date, proceeds at sale date).")
    actions.append("Track FX gain/loss on the foreign currency proceeds if not repatriated immediately.")

    total = sum(l.amount for l in lines if l.amount > 0)
    return ScenarioResult(
        scenario=s,
        lines=lines,
        risks=risks,
        actions=actions,
        forms_required=forms,
        total_tax_usd=round(total, 2),
    )
