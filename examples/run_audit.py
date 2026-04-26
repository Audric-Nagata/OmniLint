"""Quickstart example script."""

from auditor import AuditEngine, load_data
from auditor.core.engine import AuditConfig
from auditor.report import builder, renderer_json, renderer_cli
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_audit.py <dataset.csv>")
        sys.exit(1)

    source = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Loading {source}...")
    df, schema = load_data(source)

    config = AuditConfig(
        target_col=target,
        checks=["basic", "distribution", "labels", "leakage", "importance", "dedup"],
    )

    print("Running audit...")
    engine = AuditEngine(df, config)
    result = engine.run()

    report = builder.build(result, schema.source, schema.rows, schema.columns)

    renderer_cli.render(report)
    renderer_json.render(report, "report.json")
    print("\nReport saved to report.json")


if __name__ == "__main__":
    main()