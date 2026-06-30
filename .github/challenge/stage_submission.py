#!/usr/bin/env python3
"""
stage_submission.py  (final layout)

Maps a submission folder

    submissions/<name>/CQ2Onto/<domain>/<domain>_ontology.owl
    submissions/<name>/CQ2Term/<domain>/<domain>_cq2terms_terms.json

into the exact paths the CQ4OE runners discover:

    CQ2Onto :  CQ2Onto/01_predictions/challenge/<name>/ontology/<domain>_ontology.owl
    CQ2Term :  CQ2Term/01_predictions/<name>/<domain>_cq2terms_terms.json

"challenge" must be present in MODES at the top of
CQ2Onto/scripts/run_all_evaluation_agent_datasets.py.
"""
import argparse, shutil, sys
from pathlib import Path
import yaml

CHALLENGE_MODE = "challenge"
OWL_EXTS = {".owl", ".rdf", ".xml", ".ttl", ".turtle"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="submission folder name")
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()
    root = Path(args.repo_root)
    sub = root / "submissions" / args.name
    meta = yaml.safe_load((sub / "metadata.yml").read_text())
    tasks = set(meta.get("tasks") or [])
    domains = sorted(meta.get("domains") or [])

    n_term = n_onto = 0
    for dom in domains:
        if "cq2term" in tasks:
            src = sub / "CQ2Term" / dom / f"{dom}_cq2terms_terms.json"
            dst = root / "CQ2Term" / "01_predictions" / args.name / "terms" / f"{dom}_cq2terms_terms.json"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst); n_term += 1
        if "cq2onto" in tasks:
            cand = [p for p in (sub / "CQ2Onto" / dom).iterdir()
                    if p.is_file() and p.suffix.lower() in OWL_EXTS]
            src = cand[0]
            dst = (root / "CQ2Onto" / "01_predictions" / CHALLENGE_MODE /
                   args.name / "ontology" / f"{dom}_ontology{src.suffix.lower()}")
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst); n_onto += 1

    print(f"Staged CQ2Term files: {n_term}")
    print(f"Staged CQ2Onto files: {n_onto}")
    print(f"RUN_CQ2TERM={'1' if n_term else '0'}")
    print(f"RUN_CQ2ONTO={'1' if n_onto else '0'}")
    if not (n_term or n_onto):
        sys.exit("::error::Nothing staged")


if __name__ == "__main__":
    main()
