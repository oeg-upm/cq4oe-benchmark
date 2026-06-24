#!/usr/bin/env python3
"""
backfill_legacy_cli_args.py

One-shot migration. Writes the paper-baseline cli_args block into legacy
CQ2Onto evaluation JSONs that pre-date the eval-script patches.

After running this, every old run in 03_evaluation_results/ behaves like
a freshly-evaluated patched run, so build_leaderboard.py groups them
without needing --assume_config_onto or canonical-fill heuristics.

This script is idempotent. It only writes cli_args to a JSON that does
not already have it.

Usage:
    python backfill_legacy_cli_args.py CQ2Onto/03_evaluation_results

Per-layer baseline cli_args are hard-coded below to match the configuration
used to produce the 162 paper runs:
    - concept: top_n=3, final_threshold=0.6, hard=1.0, lex=0.8, sem=0.6,
               model_id=embeddinggemma, methods="hard_match,sequence_match,
               levenshtein,jaro_winkler,semantic"
    - property: same but final_threshold=0.7
    - triple: threshold=0.6, literal_relax="no", model_id=embeddinggemma
    - axiom: threshold=0.6, literal_relax="no", no_layer2=True
    - hierarchy: (none baseline-affecting beyond reasoner)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


# ─────────────────────────────────────────────────────────────────
# Paper-baseline cli_args per layer.
# Edit here if your old runs used a different baseline.
# ─────────────────────────────────────────────────────────────────

BASELINE = {
    "01_class/class_result.json": {
        "model_id":            "embeddinggemma",
        "methods":             "hard_match,sequence_match,levenshtein,jaro_winkler,semantic",
        "top_n":               3,
        "final_threshold":     0.6,
        "hard_threshold":      1.0,
        "lexical_threshold":   0.8,
        "semantic_threshold":  0.6,
    },
    "02_property/property_result.json": {
        "model_id":            "embeddinggemma",
        "methods":             "hard_match,sequence_match,levenshtein,jaro_winkler,semantic",
        "top_n":               3,
        "final_threshold":     0.7,
        "hard_threshold":      1.0,
        "lexical_threshold":   0.8,
        "semantic_threshold":  0.6,
    },
    "03_triple/triple_result.json": {
        "model_id":      "embeddinggemma",
        "threshold":     0.6,
        "literal_relax": "no",
    },
    "04_axiom/eval_axioms_result.json": {
        "threshold":     0.6,
        "literal_relax": "no",
        "no_layer2":     True,
    },
    "05_hierarchy/hierarchy_result.json": {
        # No grouping-affecting args.
    },
}


def _load(p: Path) -> dict | None:
    try:
        return json.load(open(p, "r", encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _save(p: Path, data: dict):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def backfill_one(json_path: Path, cli_args: dict, dry_run: bool) -> str:
    """Inject cli_args into config block of one result JSON.

    Returns one of: "wrote", "skipped (already has cli_args)",
                    "skipped (no config)", "skipped (no file)".
    """
    if not json_path.exists():
        return "skipped (no file)"
    data = _load(json_path)
    if not data:
        return "skipped (unreadable)"
    cfg = data.get("config")
    if not isinstance(cfg, dict):
        # Some layers (axiom) keep config nested at top, others nest under "results"
        return "skipped (no config block)"
    if "cli_args" in cfg and cfg["cli_args"]:
        return "skipped (already has cli_args)"
    cfg["cli_args"] = dict(cli_args)
    if not dry_run:
        _save(json_path, data)
    return "wrote"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("root", help="Path to CQ2Onto/03_evaluation_results")
    p.add_argument("--dry-run", action="store_true",
                   help="Show what would change without writing")
    args = p.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"ERROR: {root} does not exist", file=sys.stderr)
        sys.exit(2)

    # Walk <root>/<mode>/<model>/<dataset>/
    counts = {"wrote": 0, "skipped (already has cli_args)": 0,
              "skipped (no config block)": 0, "skipped (unreadable)": 0,
              "skipped (no file)": 0}

    for mode_dir in sorted(root.iterdir()):
        if not mode_dir.is_dir():
            continue
        for model_dir in sorted(mode_dir.iterdir()):
            if not model_dir.is_dir():
                continue
            for dataset_dir in sorted(model_dir.iterdir()):
                if not dataset_dir.is_dir():
                    continue
                for rel_path, cli in BASELINE.items():
                    if not cli:
                        continue
                    json_path = dataset_dir / rel_path
                    status = backfill_one(json_path, cli, args.dry_run)
                    counts[status] = counts.get(status, 0) + 1
                    if status == "wrote":
                        # Print a short relative breadcrumb
                        short = json_path.relative_to(root)
                        print(f"  {'[DRY] ' if args.dry_run else ''}wrote cli_args  →  {short}")

    print("\n=== Summary ===")
    for k, v in counts.items():
        print(f"  {k}: {v}")

    if args.dry_run:
        print("\n(dry-run: no files modified)")


if __name__ == "__main__":
    main()
