"""Inheritance from a non-US-resident parent to a US-resident child.

US side: there is NO US estate tax on the foreign parent's estate (decedent is
non-US person, foreign-situs assets). The recipient does NOT pay US income tax
on the inheritance itself. However, Form 3520 is required if the gift/bequest
exceeds $100,000 in a tax year.

Italy side: succession tax with a €1,000,000 exemption per child (1.04 rate),
so most family inheritances are tax-free below this threshold.

The numbers below reflect 2026 rules — confirm with a current-year advisor.
"""

from __future__ import annotations

from family_tax.scenario import Scenario, ScenarioResult, TaxLine


US_FORM_3520_THRESHOLD = 100_000
ITALY_CHILD_EXEMPTION_EUR = 1_000_000
ITALY_CHILD_RATE = 0.04
GERMANY_CHILD_EXEMPTION_EUR = 400_000
GERMANY_CHILD_RATE_BAND = [
    (75_000, 0.07),
    (300_000, 0.11),
    (600_000, 0.15),
    (6_000_000, 0.19),
]
UK_NIL_RATE_BAND_GBP = 325_000
UK_RESIDENCE_NIL_RATE_BAND_GBP = 175_000
UK_RATE = 0.40

EUR_USD = 1.10
GBP_USD = 1.25


def evaluate(s: Scenario) -> ScenarioResult:
    decedent_country = s.parties.get("decedent", {}).get("country", "ITA")
    estate_usd = float(s.assets.get("estate_value_usd", 0.0))
    has_real_estate = bool(s.assets.get("includes_real_estate_in_decedent_country"))
    includes_pfic = bool(s.assets.get("includes_foreign_mutual_funds"))

    lines: list[TaxLine] = []
    risks: list[str] = []
    actions: list[str] = []
    forms: list[str] = []

    # US side
    lines.append(
        TaxLine(
            "US",
            "US estate tax (recipient)",
            0.0,
            "Recipient does not pay US estate tax on a foreign decedent's foreign-situs assets.",
        )
    )
    lines.append(
        TaxLine(
            "US",
            "US income tax on inheritance",
            0.0,
            "Inheritances are not income to the US recipient.",
        )
    )
    if estate_usd > US_FORM_3520_THRESHOLD:
        forms.append("Form 3520 (Annual Return To Report Transactions With Foreign Trusts and Receipt of Certain Foreign Gifts)")
        risks.append(
            "Form 3520 penalty is up to 25% of the gift/bequest if not filed on time. "
            "This is the largest single risk in this scenario."
        )
        actions.append(
            f"File Form 3520 with the US return for the tax year the inheritance is received (over the ${US_FORM_3520_THRESHOLD:,} threshold)."
        )

    if includes_pfic:
        risks.append(
            "Foreign mutual funds and ETFs received by the US heir are usually classified as PFICs. "
            "PFIC reporting (Form 8621) is annual, complex, and punitive on default-method gains. "
            "Consider liquidating into US-domiciled equivalents soon after receipt."
        )
        forms.append("Form 8621 (PFIC) if foreign funds retained")

    if has_real_estate:
        risks.append(
            f"Real estate situated in {decedent_country} may be subject to a separate property tax "
            "or stamp duty on transfer; not covered by income or succession exemption."
        )
        actions.append(
            "Obtain a local appraisal at date of death to establish US cost basis (step-up applies)."
        )

    lines.append(
        TaxLine(
            "US",
            "Cost-basis step-up (US)",
            0.0,
            "FMV at date of death becomes the US cost basis for inherited assets.",
        )
    )

    # Foreign side
    if decedent_country == "ITA":
        succession_tax = _italy_succession_tax(estate_usd / EUR_USD) * EUR_USD
        lines.append(
            TaxLine(
                "IT",
                "Italian succession tax",
                succession_tax,
                f"€{ITALY_CHILD_EXEMPTION_EUR:,} exemption per child, {ITALY_CHILD_RATE*100:.1f}% on excess.",
            )
        )
    elif decedent_country == "DEU":
        de_tax = _germany_inheritance_tax(estate_usd / EUR_USD) * EUR_USD
        lines.append(
            TaxLine(
                "DE",
                "German inheritance tax",
                de_tax,
                f"€{GERMANY_CHILD_EXEMPTION_EUR:,} exemption per child, then 7-19% band rates.",
            )
        )
    elif decedent_country == "GBR":
        uk_tax = _uk_iht(estate_usd / GBP_USD) * GBP_USD
        lines.append(
            TaxLine(
                "UK",
                "UK inheritance tax",
                uk_tax,
                f"£{UK_NIL_RATE_BAND_GBP:,} nil-rate band + residence nil-rate band, then {UK_RATE*100:.0f}% on excess. "
                "Paid by the estate, not the recipient.",
            )
        )
    else:
        lines.append(
            TaxLine(decedent_country, "Local succession/inheritance tax", 0.0, "Rules not modeled — confirm locally.")
        )

    total = sum(l.amount for l in lines)
    actions.append(
        "Engage a US/" + decedent_country + " cross-border CPA before any inherited assets are sold or transferred."
    )

    return ScenarioResult(
        scenario=s,
        lines=lines,
        risks=risks,
        actions=actions,
        forms_required=forms,
        total_tax_usd=round(total, 2),
    )


def _italy_succession_tax(estate_eur: float) -> float:
    taxable = max(0.0, estate_eur - ITALY_CHILD_EXEMPTION_EUR)
    return round(taxable * ITALY_CHILD_RATE, 2)


def _germany_inheritance_tax(estate_eur: float) -> float:
    taxable = max(0.0, estate_eur - GERMANY_CHILD_EXEMPTION_EUR)
    if taxable <= 0:
        return 0.0
    rate = GERMANY_CHILD_RATE_BAND[-1][1]
    for ceiling, r in GERMANY_CHILD_RATE_BAND:
        if taxable <= ceiling:
            rate = r
            break
    return round(taxable * rate, 2)


def _uk_iht(estate_gbp: float) -> float:
    nil_band = UK_NIL_RATE_BAND_GBP + UK_RESIDENCE_NIL_RATE_BAND_GBP
    taxable = max(0.0, estate_gbp - nil_band)
    return round(taxable * UK_RATE, 2)
