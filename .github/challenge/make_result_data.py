#!/usr/bin/env python3
"""
make_result_data.py

Runs leaderboard/build_leaderboard.py scoped to ONE submission and writes
    submissions/<name>/result/result_data.js   (same format as leaderboard_data.js)
    submissions/<name>/result/leaderboard.md    (the aggregate markdown, as a bonus)

build_leaderboard.py discovers runs by rglob and needs the <mode>/<model>/<dataset>
directory depth, which the flattened result/ folder does not have. So we build a
temporary view from the staged 03_evaluation_results trees (which DO have that
depth) containing only this submission, run the builder over it, then clean up.
"""
import argparse, shutil, subprocess, sys, tempfile
from pathlib import Path
import yaml


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--onto-mode", default="challenge")
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()
    root = Path(args.repo_root).resolve()
    name = args.name
    sub = root / "submissions" / name
    meta = yaml.safe_load((sub / "metadata.yml").read_text())
    tasks = set(meta.get("tasks") or [])

    tmp = Path(tempfile.mkdtemp(prefix="cq4oe_lb_"))
    onto_root = tmp / "onto"
    term_root = tmp / "term"
    onto_root.mkdir(parents=True, exist_ok=True)
    term_root.mkdir(parents=True, exist_ok=True)

    if "cq2onto" in tasks:
        src = root / "CQ2Onto" / "03_evaluation_results" / args.onto_mode / name
        if src.exists():
            shutil.copytree(src, onto_root / args.onto_mode / name)
    if "cq2term" in tasks:
        src = root / "CQ2Term" / "03_evaluation_results" / name
        if src.exists():
            shutil.copytree(src, term_root / name)

    out_js = sub / "result" / "result_data.js"
    out_md = sub / "result" / "leaderboard.md"
    out_js.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, str(root / "leaderboard" / "build_leaderboard.py"),
        "--cq2onto_root", str(onto_root),
        "--cq2term_root", str(term_root),
        "--html_data",    str(out_js),
        "--markdown_out", str(out_md),
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"Wrote {out_js}")


if __name__ == "__main__":
    main()
