"""Run the career-break demo."""

from pathlib import Path

from life_scenarios import scenario as sc


def main():
    s = sc.load(Path("scenarios/career_break_12mo.yaml"))
    result = sc.run(s)
    print(f"event: {s.event}")
    for line in result.lines:
        print(f"  {line.label:40s} {line.value}")
    if result.headline_metric:
        print(f"headline: {result.headline_metric}")
    print(f"risks: {result.risks}")


if __name__ == "__main__":
    main()
