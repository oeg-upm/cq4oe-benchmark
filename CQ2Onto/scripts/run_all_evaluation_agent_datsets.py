#!/usr/bin/env python3
"""
run_all_evaluation_agent_datsets.py

Walks 01_predictions/<mode>/<model>/ontology/, evaluates each prediction
against its matching gold standard, and refreshes the leaderboard at the
end of a successful run.

Standard call:
    cd CQ2Onto
    python -u scripts/run_all_evaluation_agent_datsets.py

Run a subset of layers:
    python -u scripts/run_all_evaluation_agent_datsets.py --layers concept,property
    python -u scripts/run_all_evaluation_agent_datsets.py --layers triple,atomic,axioms,hierarchy

Skip the leaderboard refresh:
    python -u scripts/run_all_evaluation_agent_datsets.py --no_leaderboard
"""
import argparse
import subprocess
import sys
from pathlib import Path

PYTHON = "/Users/ljymacbook/opt/anaconda3/envs/tempautocl/bin/python"

MODES = ["agent", "normal", "cqbycq", "mymodel"]

GOLD_ROOT = Path("00_gold_standard")
DATASETS = ["wine", "vgo", "swo", "awo", "odrl", "water"]

# leaderboard/ sits at the repo root (one level above CQ2Onto/, which is cwd).
LEADERBOARD_DIR = Path("../leaderboard")

ALL_LAYERS = ["concept", "property", "triple", "atomic", "axioms", "hierarchy"]


def run(cmd):
    print("\n" + "=" * 100)
    print(" ".join(str(x) for x in cmd))
    print("=" * 100)
    subprocess.run([str(x) for x in cmd], check=True)


def detect_dataset(filename):
    name = filename.lower()
    for ds in DATASETS:
        if name.startswith(ds):
            return ds
    return None


def find_gold_owl(dataset):
    folder = GOLD_ROOT / dataset / "ontology"
    files = sorted(folder.glob("*.owl"))
    if not files:
        return None
    return files[0]


def find_gold_axioms(dataset):
    folder = GOLD_ROOT / dataset / "axioms"
    files = sorted(folder.glob("*axiom*gold*.json"))
    if not files:
        files = sorted(folder.glob("*.json"))
    if not files:
        return None
    return files[0]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--layers", default=",".join(ALL_LAYERS),
                   help="Comma-separated subset of: "
                        + ",".join(ALL_LAYERS))
    p.add_argument("--modes", default=None,
                   help="Comma-separated subset of MODES. "
                        "Default: all configured modes.")
    p.add_argument("--no_leaderboard", action="store_true",
                   help="Skip the leaderboard refresh at the end")
    args = p.parse_args()
    args.layers_set = set(args.layers.split(","))
    unknown = args.layers_set - set(ALL_LAYERS)
    if unknown:
        sys.exit(f"Unknown layer name(s): {sorted(unknown)}. "
                 f"Accepted: {ALL_LAYERS}")
    if args.modes:
        args.modes_list = [m.strip() for m in args.modes.split(",") if m.strip()]
        unknown_modes = set(args.modes_list) - set(MODES)
        if unknown_modes:
            sys.exit(f"Unknown mode(s): {sorted(unknown_modes)}. "
                     f"Add to MODES first or pick from: {MODES}")
    else:
        args.modes_list = MODES
    return args


def refresh_leaderboard():
    """Call build_leaderboard.py from the leaderboard directory."""
    script = LEADERBOARD_DIR / "build_leaderboard.py"
    if not script.exists():
        print(f"WARN: {script} not found, leaderboard not refreshed.")
        return
    cmd = [
        PYTHON, str(script),
        "--cq2term_root", "../CQ2Term/03_evaluation_results",
        "--cq2onto_root", "03_evaluation_results",
        "--html_data",    str(LEADERBOARD_DIR / "leaderboard_data.js"),
        "--markdown_out", str(LEADERBOARD_DIR / "leaderboard.md"),
    ]
    print("\n" + "=" * 100)
    print("Refreshing leaderboard")
    print(" ".join(str(x) for x in cmd))
    print("=" * 100)
    try:
        subprocess.run([str(x) for x in cmd], check=True)
    except subprocess.CalledProcessError as e:
        # Do not let a leaderboard glitch tank the evaluation run.
        print(f"WARN: leaderboard refresh failed with exit {e.returncode}, "
              f"but evaluation results were saved.")


def main():
    args = parse_args()
    L = args.layers_set

    for mode in args.modes_list:
        PRED_ROOT = Path("01_predictions") / mode
        EVAL_ROOT = Path("03_evaluation_results") / mode
        ATOMIC_ROOT = Path("02_atomic_axioms") / mode
        SUMMARY_ROOT = Path("04_summary") / mode

        if not PRED_ROOT.exists():
            print(f"SKIP mode {mode}: missing {PRED_ROOT}")
            continue

        model_dirs = sorted([
            p for p in PRED_ROOT.iterdir()
            if p.is_dir() and not p.name.startswith(".")
        ])

        for model_dir in model_dirs:
            model = model_dir.name
            ontology_dir = model_dir / "ontology"

            if not ontology_dir.exists():
                print(f"SKIP {mode}/{model}: no ontology folder")
                continue

            pred_owls = sorted([
                p for p in ontology_dir.glob("*.owl")
                if "atomic_tbox" not in p.name
                and ".ipynb_checkpoints" not in str(p)
            ])

            for pred_owl in pred_owls:
                dataset = detect_dataset(pred_owl.name)
                if dataset is None:
                    print(f"SKIP unknown dataset: {pred_owl}")
                    continue

                gold_owl = find_gold_owl(dataset)
                gold_axioms = find_gold_axioms(dataset)

                if gold_owl is None:
                    print(f"SKIP {dataset}: missing gold owl")
                    continue
                if gold_axioms is None:
                    print(f"SKIP {dataset}: missing gold axioms")
                    continue

                print(f"\n### Running {mode} / {model} / {dataset}")

                base_eval = EVAL_ROOT / model / dataset
                class_dir = base_eval / "01_class"
                prop_dir = base_eval / "02_property"
                triple_dir = base_eval / "03_triple"
                axiom_dir = base_eval / "04_axiom"
                hierarchy_dir = base_eval / "05_hierarchy"
                atomic_dir = ATOMIC_ROOT / model / dataset
                report_path = SUMMARY_ROOT / model / f"{dataset}_report.md"

                for d in [
                    class_dir, prop_dir, triple_dir, axiom_dir, hierarchy_dir,
                    atomic_dir, report_path.parent,
                ]:
                    d.mkdir(parents=True, exist_ok=True)

                class_csv = class_dir / "class_best_matching.csv"
                property_csv = prop_dir / "property_best_matching.csv"
                pred_axiom_json = atomic_dir / f"{pred_owl.stem}_atomic_tbox.json"
                strict_cq_csv = axiom_dir / "strict_cq_coverage.csv"

                # 1. Class / concept evaluation
                if "concept" in L:
                    run([
                        PYTHON, "scripts/concept/eval_concept.py",
                        "--generate_onto_file_path", pred_owl,
                        "--ground_onto_file_path", gold_owl,
                        "--model_id", "embeddinggemma",
                        "--methods", "hard_match,sequence_match,levenshtein,jaro_winkler,semantic",
                        "--top_n", "3",
                        "--hard_threshold", "1.0",
                        "--lexical_threshold", "0.8",
                        "--semantic_threshold", "0.6",
                        "--final_threshold", "0.6",
                        "--save_file_path", class_dir / "class_result.json",
                        "--save_best_matching_csv", class_csv,
                        "--save_alignment_trace_csv", class_dir / "class_alignment_trace.csv",
                        "--save_alignment_trace_json", class_dir / "class_alignment_trace.json",
                        "--save_report_md", report_path,
                    ])

                # 2. Property evaluation
                if "property" in L:
                    run([
                        PYTHON, "scripts/property/eval_property.py",
                        "--pred_onto", pred_owl,
                        "--gold_onto", gold_owl,
                        "--model_id", "embeddinggemma",
                        "--methods", "hard_match,sequence_match,levenshtein,jaro_winkler,semantic",
                        "--top_n", "3",
                        "--final_threshold", "0.7",
                        "--hard_threshold", "1.0",
                        "--lexical_threshold", "0.8",
                        "--semantic_threshold", "0.6",
                        "--save_result", prop_dir / "property_result.json",
                        "--save_best_matching_csv", property_csv,
                        "--save_alignment_trace_csv", prop_dir / "property_alignment_trace.csv",
                        "--save_alignment_trace_json", prop_dir / "property_alignment_trace.json",
                        "--save_report_md", report_path,
                    ])

                # 3. Triple / domain-range evaluation
                if "triple" in L:
                    if not class_csv.exists() or not property_csv.exists():
                        sys.exit(f"ERROR: triple layer needs class+property alignment CSVs. "
                                 f"Run --layers concept,property first.")
                    run([
                        PYTHON, "scripts/triple/eval_triple.py",
                        "--pred_onto", pred_owl,
                        "--gold_onto", gold_owl,
                        "--class_csv", class_csv,
                        "--property_csv", property_csv,
                        "--save_result", triple_dir / "triple_result.json",
                        "--save_layer3_csv", triple_dir / "triple_layer3_pairs.csv",
                        "--save_layer3_json", triple_dir / "triple_layer3_pairs.json",
                        "--save_report_md", report_path,
                        "--threshold", "0.6",
                        "--literal_relax", "no",
                    ])

                # 4. Extract predicted atomic axioms
                if "atomic" in L:
                    run([
                        PYTHON, "scripts/axioms/Axioms_atomic.py",
                        pred_owl,
                    ])
                    for f in pred_owl.parent.glob(f"{pred_owl.stem}_atomic_tbox.*"):
                        f.replace(atomic_dir / f.name)

                # 5. Axiom evaluation
                if "axioms" in L:
                    if not pred_axiom_json.exists():
                        sys.exit(f"ERROR: pred axiom JSON not found: {pred_axiom_json}. "
                                 f"Run --layers atomic first.")
                    if not class_csv.exists() or not property_csv.exists():
                        sys.exit(f"ERROR: axioms layer needs class+property alignment CSVs.")
                    run([
                        PYTHON, "scripts/axioms/eval_axioms.py",
                        "--gold", gold_axioms,
                        "--pred", pred_axiom_json,
                        "--class_csv", class_csv,
                        "--property_csv", property_csv,
                        "--save_result_json", axiom_dir / "eval_axioms_result.json",
                        "--details_csv", axiom_dir / "axiom_details.csv",
                        "--save_cq_csv", strict_cq_csv,
                        "--save_report_md", report_path,
                        "--literal_relax", "no",
                        "--threshold", "0.6",
                        "--no_layer2",
                    ])

                # 6. Hierarchy / HermiT evaluation
                if "hierarchy" in L:
                    if not pred_axiom_json.exists():
                        sys.exit(f"ERROR: hierarchy layer needs atomic axiom JSON: {pred_axiom_json}")
                    if not class_csv.exists() or not property_csv.exists():
                        sys.exit(f"ERROR: hierarchy layer needs class+property alignment CSVs.")
                    run([
                        PYTHON, "scripts/hierarchy/eval_hierarchy.py",
                        "--gold_owl", gold_owl,
                        "--pred_owl", pred_owl,
                        "--class_csv", class_csv,
                        "--property_csv", property_csv,
                        "--gold", gold_axioms,
                        "--pred", pred_axiom_json,
                        "--strict_cq_csv", strict_cq_csv,
                        "--output_json", hierarchy_dir / "hierarchy_result.json",
                        "--output_csv", hierarchy_dir / "hierarchy_pairs.csv",
                        "--output_md", report_path,
                    ])

                print(f"DONE: {mode} / {model} / {dataset}")

    # Auto-refresh leaderboard at the end of a full successful run.
    if not args.no_leaderboard:
        refresh_leaderboard()


if __name__ == "__main__":
    main()
