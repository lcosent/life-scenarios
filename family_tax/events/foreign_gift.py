"""Large gift from a non-US person to a US-resident recipient.

US rule: no US income or gift tax on the recipient. But Form 3520 is required
if the aggregate value from a single non-US person exceeds $100,000 in a tax
year (or $19,570 if from a foreign corp/partnership for 2026).
"""

from __future__ import annotations

from family_tax.scenario import Scenario, ScenarioResult, TaxLine


THRESHOLD_INDIVIDUAL = 100_000
THRESHOLD_ENTITY = 19_570


def evaluate(s: Scenario) -> ScenarioResult:
    amount = float(s.assets.get("gift_value_usd", 0.0))
    from_entity = bool(s.parties.get("donor", {}).get("is_entity"))

    threshold = THRESHOLD_ENTITY if from_entity else THRESHOLD_INDIVIDUAL
    lines = [
        TaxLine("US", "US gift tax (recipient)", 0.0, "Recipient never pays US gift tax."),
        TaxLine("US", "US income tax", 0.0, "Gifts are not income."),
    ]
    forms = []
    risks = []
    actions = []

    if amount >= threshold:
        forms.append("Form 3520")
        risks.append(
            f"Aggregate gifts of ${amount:,.0f} from a {'foreign entity' if from_entity else 'foreign individual'} "
            f"exceed the ${threshold:,} threshold. Form 3520 must be filed. Penalty up to 25% if missed."
        )
        actions.append(
            "File Form 3520 by the US tax return due date for the tax year of receipt."
        )
    else:
        lines.append(
            TaxLine("US", "Form 3520 filing", 0.0, f"Not required below ${threshold:,} threshold.")
        )

    return ScenarioResult(
        scenario=s,
        lines=lines,
        risks=risks,
        actions=actions,
        forms_required=forms,
        total_tax_usd=0.0,
    )
