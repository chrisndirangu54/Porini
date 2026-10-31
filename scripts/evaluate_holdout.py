"""Run independent held-out validation on CSV (group,label,score).
Usage: PYTHONPATH=. python scripts/evaluate_holdout.py results.csv
"""
import csv
import json
import sys
from pathlib import Path
from backend.app.evidence_quality import binary_metrics, group_evaluation

def main(path):
    with Path(path).open(newline="",encoding="utf-8") as f:
        records=list(csv.DictReader(f))
    rows=[(r["group"],int(r["label"]),float(r["score"])) for r in records]
    report={"overall":binary_metrics([r[1] for r in rows],[r[2] for r in rows]),
            "by_group":group_evaluation(rows),"note":"Holdout-only; do not extrapolate to untested regions"}
    print(json.dumps(report,indent=2))
    return report

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("Usage: python scripts/evaluate_holdout.py predictions.csv")
    main(sys.argv[1])
