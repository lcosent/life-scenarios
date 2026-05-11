# life-scenarios

A planning tool for **major life-event decisions**. You describe your situation in YAML, pick a scenario (career break, relocation, school funding, large life transaction), and get a structured trade-off analysis with explicit numbers and risk flags.

```
$ life-scenarios run scenarios/career_break_12mo.yaml

SCENARIO: 12-month sabbatical at 36 to learn a new domain
─────────────────────────────────────────────────────────────
runway needed                $138,000     12 months at modeled burn
opportunity cost             $310,000     salary + RSU forfeit + match miss
emergency buffer post-break  $30,000      recommended floor
re-entry premium expected    +8%          historical for skilled domain switch
breakeven year (post-return) year 4       given assumed wage path

RISK FLAGS
  • Health insurance: 12 months of COBRA at modeled $850/mo if unemployed
  • RSU cliff: 2,400 unvested shares forfeited at departure
  • Recovery timing: each additional month past 12 reduces re-entry rate

RECOMMENDED ACTIONS
  1. Lock in COBRA election timing before separation.
  2. Time departure 2 weeks after next RSU vest cliff.
  3. Build the floor first; sabbatical second.
```

## What it is

A scenario engine. The unit is a **YAML scenario file** that describes a decision you are considering. The engine evaluates it and returns:

- numbers (cash flows, opportunity cost, runway, deltas)
- forms / steps required (if applicable)
- risk flags (the things you didn't think of)
- recommended actions

It is not advice. It is a **conversation starter** for the meeting you should have with the right specialist (CPA, financial advisor, attorney, immigration consultant) depending on the scenario.

## What it covers

Scenarios are organized into categories. Each category is a folder under `life_scenarios/events/`.

| Category | Example scenarios |
|---|---|
| **Career** | sabbatical / career break, switch to self-employment |
| **Mobility** | cross-city relocation (with COL + state tax + housing model) |
| **Family** | kids' education funding (529 vs taxable), marriage finance planning |
| **Money events** | inheritance modeling, large foreign gift, sale of major asset |

Each scenario is hand-curated. Eight ship in the box. Easy to add your own.

## Quickstart

```bash
pip install -e .

# list bundled scenarios
life-scenarios list

# run a specific scenario
life-scenarios run scenarios/career_break_12mo.yaml

# print a template you can edit
life-scenarios new --template career_break > my_decision.yaml
$EDITOR my_decision.yaml
life-scenarios run my_decision.yaml
```

## How it works

```
   YAML scenario  ─┐
                   │
   per-event rule ─┼─▶  numeric model (Python — plain functions, no LLM)
   modules         │
                   └─▶  flagged risks
                              │
                              ▼
                   optional LLM narrates plain-English summary
                              │
                              ▼
                       Recommended actions
```

The rules engine is **plain Python**. Thresholds, exemption amounts, rate bands live in module constants — easy to bump each year. The LLM is only used for the optional narrative summary.

## Scenario format

```yaml
event: career_break
notes: 12-month sabbatical at 36 to learn a new domain

profile:
  age: 36
  salary_usd: 280_000
  monthly_burn_usd: 11_500
  current_savings_usd: 165_000
  rsu_unvested_shares: 2_400
  rsu_current_price: 185
  employer_401k_match_rate: 0.05

decision:
  break_months: 12
  expected_reentry_premium: 0.08
  domain_switch: true

jurisdictions: ["US"]
```

## Bundled scenarios

```
scenarios/
├── career_break_12mo.yaml
├── relocation_high_to_lower_col.yaml
├── education_funding_two_kids.yaml
├── switch_to_self_employment.yaml
├── inheritance_generic.yaml
├── foreign_gift_generic.yaml
├── marriage_finance_planning.yaml
└── sell_major_asset.yaml
```

All scenarios use **generic** parties and amounts. They are intentionally not identifying — use them as templates and edit locally. Files under `my_*.yaml` are gitignored.

## What this is not

- **Not financial, legal, or tax advice.** Every scenario ends with "consult a qualified advisor."
- **Not a complete financial planner.** It covers point-in-time decisions, not ongoing portfolio management.
- **Not jurisdiction-complete.** Money-event scenarios model US plus a handful of EU jurisdictions. PRs welcome.

## License

MIT.
