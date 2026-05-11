"""Marriage between US citizen and non-US-citizen.

Key US rules: unlimited marital deduction applies only when the recipient
spouse is a US citizen. Gifts to non-citizen spouses have a special annual
exclusion ($185,000 in 2026, indexed). Estate planning typically involves a
Qualified Domestic Trust (QDOT) to preserve marital deduction at death.
"""

from __future__ import annotations

from family_tax.scenario import Scenario, ScenarioResult, TaxLine


NON_CITIZEN_SPOUSE_ANNUAL_EXCLUSION_2026 = 185_000


def evaluate(s: Scenario) -> ScenarioResult:
    spouse_country = s.parties.get("spouse", {}).get("country", "ITA")
    spouse_is_us_citizen = bool(s.parties.get("spouse", {}).get("is_us_citizen"))
    contemplating_large_gift = float(s.assets.get("contemplated_gift_to_spouse_usd", 0.0))

    lines = []
    risks = []
    actions = []
    forms = []

    if spouse_is_us_citizen:
        lines.append(
            TaxLine("US", "Marital deduction", 0.0, "Unlimited deduction; standard rules apply.")
        )
    else:
        lines.append(
            TaxLine(
                "US",
                f"Non-citizen spouse annual gift exclusion ({spouse_country})",
                0.0,
                f"Limited to ${NON_CITIZEN_SPOUSE_ANNUAL_EXCLUSION_2026:,} per year.",
            )
        )
        if contemplating_large_gift > NON_CITIZEN_SPOUSE_ANNUAL_EXCLUSION_2026:
            risks.append(
                f"Contemplated gift of ${contemplating_large_gift:,.0f} exceeds the "
                f"${NON_CITIZEN_SPOUSE_ANNUAL_EXCLUSION_2026:,} annual exclusion. Excess uses lifetime exemption."
            )
            actions.append(
                "Consider structuring large transfers over multiple tax years to stay within the annual exclusion."
            )
        risks.append(
            "At death, transfers to a non-US-citizen spouse do not qualify for the unlimited marital deduction "
            "unless held in a Qualified Domestic Trust (QDOT)."
        )
        actions.append(
            "Discuss QDOT with an estate attorney as part of estate planning, especially if combined US assets > $13.99M."
        )

    actions.append(
        "If non-US spouse has foreign accounts > $10,000 aggregate, FBAR may apply once they become a US resident."
    )
    forms.append("FBAR (FinCEN 114) once spouse is US resident with foreign accounts > $10,000")

    return ScenarioResult(
        scenario=s,
        lines=lines,
        risks=risks,
        actions=actions,
        forms_required=forms,
        total_tax_usd=0.0,
    )
