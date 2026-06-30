#!/usr/bin/env python3
"""
validate_submission.py  (final layout)

Guard run on every challenge PR before evaluation. Enforces, from the list of
changed files plus the submission contents, that the PR is a well-formed entry
that touches only its own submissions/<name>/ folder. This is what protects the
gold standards, evaluation scripts, leaderboard, and other submissions.

Usage:
    python .github/challenge/validate_submission.py --changed-files changed.txt

changed.txt = one repo-relative path per line. Prints "NAME=<folder>" on the
last line so the workflow can capture the submission folder name.
"""
import argparse, json, sys
from pathlib import Path
import yaml

VALID_DOMAINS = {"awo", "odrl", "swo", "vgo", "water", "wine"}
VALID_TASKS = {"cq2term", "cq2onto"}
OWL_EXTS = {".owl", ".rdf", ".xml", ".ttl", ".turtle"}
SUB = "submissions/"

# Folders under submissions/ that are NOT entries and must never be evaluated.
# example-submission is the reference template shipped with the repo; the Action
# only ever runs over a freshly pulled participant folder.
IGNORE_NAMES = {"example-submission"}


def fail(msg):
    print(f"::error::{msg}")
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--changed-files", required=True)
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()
    root = Path(args.repo_root)

    changed = [l.strip() for l in Path(args.changed_files).read_text().splitlines() if l.strip()]
    if not changed:
        fail("No changed files. A submission must add files under submissions/.")

    # 1. confine everything to submissions/
    outside = [c for c in changed if not c.startswith(SUB)]
    if outside:
        fail("PR changes files outside submissions/: " + ", ".join(outside[:20]))

    # 2. exactly one submission folder (the example template is never an entry)
    names = {c.split("/")[1] for c in changed if len(c.split("/")) > 2}
    names = {n for n in names if n and n != "README.md" and n not in IGNORE_NAMES}
    if len(names) != 1:
        fail(f"A PR must touch exactly one submissions/<name>/ folder "
             f"(excluding {sorted(IGNORE_NAMES)}); found {sorted(names)}.")
    name = next(iter(names))
    sub = root / SUB / name

    # 3. required files
    meta_path = sub / "metadata.yml"
    if not meta_path.exists():
        fail(f"Missing {meta_path}.")

    # 4. metadata schema
    try:
        meta = yaml.safe_load(meta_path.read_text())
    except Exception as e:
        fail(f"metadata.yml is not valid YAML: {e}")
    for key in ("organization_id", "method_name", "tasks", "domains"):
        if not meta.get(key):
            fail(f"metadata.yml missing required key '{key}'.")
    tasks = set(meta["tasks"] or [])
    domains = set(meta["domains"] or [])
    if not tasks <= VALID_TASKS:
        fail(f"Unknown task(s) {sorted(tasks - VALID_TASKS)}. Valid: {sorted(VALID_TASKS)}")
    if not domains <= VALID_DOMAINS:
        fail(f"Unknown domain(s) {sorted(domains - VALID_DOMAINS)}. Valid: {sorted(VALID_DOMAINS)}")

    # 5. every declared (task, domain) has a parseable artifact
    for dom in sorted(domains):
        if "cq2term" in tasks:
            tj = sub / "CQ2Term" / dom / f"{dom}_cq2terms_terms.json"
            if not tj.exists():
                fail(f"cq2term+{dom} declared but missing {tj}.")
            try:
                data = json.loads(tj.read_text())
            except Exception as e:
                fail(f"{tj} is not valid JSON: {e}")
            if not isinstance(data, list) or (data and not {"id", "value", "class", "property"} <= set(data[0])):
                fail(f"{tj} must be a list of objects with keys id, value, class, property.")
        if "cq2onto" in tasks:
            dom_dir = sub / "CQ2Onto" / dom
            owls = [p for p in dom_dir.iterdir()
                    if dom_dir.exists() and p.is_file() and p.suffix.lower() in OWL_EXTS] if dom_dir.exists() else []
            if not owls:
                fail(f"cq2onto+{dom} declared but no ontology file in {dom_dir}/.")

    print(f"Validation passed: name='{name}' tasks={sorted(tasks)} domains={sorted(domains)}")
    print(f"NAME={name}")


if __name__ == "__main__":
    main()
