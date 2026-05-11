"""Run the canonical Italian-mother inheritance scenario."""

from pathlib import Path

from family_tax import scenario as sc


def main():
    s = sc.load(Path("scenarios/inheritance_italian_mother.yaml"))
    result = sc.run(s)
    print(f"event: {s.event}")
    for line in result.lines:
        print(f"  {line.jurisdiction:3s} {line.label:40s} ${line.amount:,.2f}")
    print(f"total: ${result.total_tax_usd:,.2f}")
    print(f"forms: {result.forms_required}")
    print(f"risks: {result.risks}")


if __name__ == "__main__":
    main()
