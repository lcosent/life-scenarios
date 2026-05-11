# family-tax-scenarios

A planning tool for **international families living in the US** to understand the financial impact of life events — inheritance, marriage, kids born abroad, dual citizenship, return to home country — *before* they happen.

```
$ family-tax-scenarios run scenarios/inheritance_italian_mother.yaml

SCENARIO: Italian mother (Italian resident) leaves $1.2M
          to US-resident son (dual IT/US citizen)
─────────────────────────────────────────────────────────
US estate tax (recipient)        $0       (US does not tax recipient)
US gift tax (recipient)          $0       (n/a — inheritance)
Form 3520 required               YES      (foreign gift > $100k)
Italy succession tax (decedent)  $0       (€1M exemption per child)
Step-up in basis (US)            YES      ($1.2M FMV at death)
Total tax burden                 $0

RISK FLAGS
  • PFIC exposure if estate includes Italian mutual funds
  • Form 3520 penalty up to 25% of gift value if not filed
  • Italy may impose tax on Italian real estate (separate from succession)

RECOMMENDED ACTIONS
  1. File Form 3520 with US return for the tax year of receipt.
  2. Engage a US/IT cross-border CPA before any Italian assets are sold.
  3. Document FMV at date of death — establishes US cost basis.
```

## Why this exists

International families face stupid, expensive, avoidable tax surprises because the planning is fragmented across two or three jurisdictions and three or four advisors. A US accountant doesn't know Italian succession law. An Italian commercialista doesn't know IRS Form 3520. The family pays for the gap.

**family-tax-scenarios** is a "what if" simulator. You describe your situation in YAML, pick a life event, and get a plain-English breakdown — across both tax systems — of who owes what, what forms must be filed, and what the recommended action is.

It is **not tax advice**. It is a **conversation starter** for the meeting you should have with a real cross-border tax advisor.

## What it covers

| Event | Jurisdictions | Status |
|---|---|---|
| Inheritance from non-US parent | US + IT, DE, UK, FR, CH | ✓ |
| Inheritance from non-US parent (real estate) | US + IT, DE | ✓ |
| Gift > $100k from non-US person | US (Form 3520) | ✓ |
| Marriage to non-US-citizen spouse | US (gift tax, estate tax) | ✓ |
| Child born abroad to US citizen | US (CRBA, FBAR) | ✓ |
| Return to home country with US assets | US exit tax (Section 877A) | partial |
| Selling Italian primary residence as US resident | US + IT capital gains | ✓ |
| Receiving RSU from US employer while moving abroad | US sourcing + treaty | ✓ |

PRs welcome. Each scenario is one YAML file under `scenarios/` and one Python module under `family_tax/events/`.

## Quickstart

```bash
pip install -e .

# list bundled scenarios
family-tax-scenarios list

# run a specific scenario
family-tax-scenarios run scenarios/inheritance_italian_mother.yaml

# describe your own situation, get a recommendation
family-tax-scenarios interactive
```

## How it works

```
   YAML scenario  ─┐
                   │
   rules engine   ─┼─▶  per-jurisdiction computation
   (rules/*.yaml)  │    (form lookups, thresholds, exemptions)
                   │
                   └─▶  flagged risks (PFIC, FBAR, 3520, ...)
                              │
                              ▼
                   LLM narrates the result in plain English
                              │
                              ▼
                       Recommended actions
```

The rules engine is **plain Python**, not a model. Thresholds, exemptions, and form numbers come from `rules/*.yaml` — easy to update each year. The LLM is only used for the narrative summary and risk explanation.

## Scenarios bundled

```
scenarios/
├── inheritance_italian_mother.yaml      # the canonical example
├── inheritance_german_father.yaml
├── inheritance_uk_grandparent.yaml
├── marriage_us_citizen_to_eu.yaml
├── child_born_abroad.yaml
├── return_to_italy_with_rsus.yaml
├── sell_italian_apartment_as_us_resident.yaml
└── large_gift_from_foreign_parent.yaml
```

Each scenario file is short, hand-edited YAML you can copy and adapt to your own situation.

## What this is not

- **Not tax advice.** Every output ends with "consult a cross-border tax advisor before acting."
- **Not a replacement** for Turbotax, H&R Block Expat, or a CPA. It is a *pre-CPA* tool — surfaces the questions you should be asking.
- **Not jurisdiction-complete.** Currently covers US + IT, DE, UK, FR, CH. PRs welcome for Spain, Japan, Australia, Canada.
- **Not real-time.** Rule data is updated annually. Always confirm current-year thresholds with your advisor.

## Pricing if this were a product

A reasonable user would pay **$49–$199** for a single scenario report that surfaces a $50k+ tax surprise *before* it happens. The market is real (millions of dual-resident or dual-national families in the US alone). This repo is the engine; a product would wrap it in onboarding, doc upload, and an advisor-handoff workflow.

## License

MIT.
