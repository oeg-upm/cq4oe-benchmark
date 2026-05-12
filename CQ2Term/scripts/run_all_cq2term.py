#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
from pathlib import Path

PYTHON = "YOUR PATH"

PRED_ROOT = Path("01_predictions")
GOLD_ROOT = Path("00_gold_standard")
EVAL_ROOT = Path("03_evaluation_results")
SUMMARY_ROOT = Path("04_summary")

DATASETS = ["wine", "vgo", "swo", "awo", "odrl", "water"]


def run(cmd):
    print("\n" + "=" * 100)
    print(" ".join(str(x) for x in cmd))
    print("=" * 100)
    subprocess.run([str(x) for x in cmd], check=True)


def find_gold_cq_terms(dataset):
    folder = GOLD_ROOT / dataset
    candidates = [
        folder / "cq_terms" / f"cq_to_terms_{dataset}.json",
        folder / f"cq_to_terms_{dataset}.json",
        folder / "cq_terms" / "cq_to_terms.json",
        folder / "cq_to_terms.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def find_pred_cq_terms(model_dir, dataset):
    candidates = [
        model_dir / "cq_terms" / f"{dataset}_terms.json",
        model_dir / f"{dataset}_terms.json",
        model_dir / "terms" / f"{dataset}_terms.json",
        model_dir / "terms" / f"{dataset}_cq2terms_terms.json",
        model_dir / "terms" / f"{dataset}_cq2term_cq2terms_terms.json",
        model_dir / "cq_terms" / f"{dataset}_cq2terms_terms.json",
        model_dir / "cq_terms" / f"{dataset}_cq2term_cq2terms_terms.json",
    ]
    for p in candidates:
        if p.exists():
            return p

    matches = sorted(model_dir.rglob(f"{dataset}*terms.json"))
    if matches:
        if len(matches) > 1:
            print(f"  [warn] {model_dir.name}/{dataset}: matched "
                  f"{len(matches)} files via fallback glob, picking "
                  f"{matches[0].name}")
        return matches[0]
    return None


def main():
    model_dirs = sorted([
        p for p in PRED_ROOT.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    ])

    for model_dir in model_dirs:
        model = model_dir.name

        for dataset in DATASETS:
            gold_cq_terms = find_gold_cq_terms(dataset)
            pred_cq_terms = find_pred_cq_terms(model_dir, dataset)

            if gold_cq_terms is None:
                print(f"SKIP {model}/{dataset}: missing gold cq_to_terms")
                continue

            if pred_cq_terms is None:
                print(f"SKIP {model}/{dataset}: missing pred terms")
                continue

            print(f"\n### Running CQ2TERM / {model} / {dataset}")
            print(f"Gold CQ terms : {gold_cq_terms}")
            print(f"Pred CQ terms : {pred_cq_terms}")

            out_dir = EVAL_ROOT / model / dataset / "06_cq_terms"
            report_path = SUMMARY_ROOT / model / f"{dataset}_report.md"

            out_dir.mkdir(parents=True, exist_ok=True)
            report_path.parent.mkdir(parents=True, exist_ok=True)

            run([
                PYTHON, "scripts/eval_cq_terms.py",
    "--gold_cq_to_terms", gold_cq_terms,
    "--pred_cq_to_terms", pred_cq_terms,
    "--methods", "hard_match,jaro_winkler,levenshtein,semantic,sequence_match",
    "--hard_threshold", "1.0",
    "--lexical_threshold", "0.8",
    "--semantic_threshold", "0.6",
    "--top_n", "3",
    "--final_threshold", "0.6",
    "--save_class_alignment_csv", out_dir / "cqterm_class_trace.csv",
    "--save_property_alignment_csv", out_dir / "cqterm_prop_trace.csv",
    "--save_class_best_matching_csv", out_dir / "cqterm_class_best_matching.csv",
    "--save_property_best_matching_csv", out_dir / "cqterm_prop_best_matching.csv",
    "--save_cq_coverage_csv", out_dir / "cq_coverage.csv",
    "--save_term_coverage_csv", out_dir / "term_coverage.csv",
    "--save_result_json", out_dir / "eval_cq_terms_result.json",
    "--save_report_md", report_path,
            ])

            print(f"DONE: CQ2TERM / {model} / {dataset}")


if __name__ == "__main__":
    main()
