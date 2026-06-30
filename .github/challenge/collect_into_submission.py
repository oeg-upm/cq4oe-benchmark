#!/usr/bin/env python3
"""
collect_into_submission.py

For each TASK listed in metadata.yml, writes everything the Action produces into
a SINGLE top-level folder, submissions/<name>/result/:

    submissions/<name>/
        result/                              <- the one output folder
            CQ2Onto/
                result/                      <- numeric files (mirror of 03_evaluation_results)
                    <domain>/<layer>/*.json,*.csv
                report/                      <- markdown reports (from 04_summary)
                    <domain>_report.md
            CQ2Term/
                result/
                    <domain>/06_cq_terms/*.json,*.csv
                report/
                    <domain>_report.md
            summary.md                       <- headline F1s + links (used for PR comment)
            result_data.js                   <- written later by make_result_data.py
            leaderboard.md                   <- written later by make_result_data.py

Sources produced by the runners:
    CQ2Term : 04_summary/<name>/...           03_evaluation_results/<name>/...
    CQ2Onto : 04_summary/<mode>/<name>/...     03_evaluation_results/<mode>/<name>/...
"""
import argparse, json, shutil, datetime
from pathlib import Path
import yaml

TASKS = {"cq2onto": "CQ2Onto", "cq2term": "CQ2Term"}

def cq2term_f1(domain_dir: Path):
    p = domain_dir / "06_cq_terms" / "eval_cq_terms_result.json"
    try:
        m = json.loads(p.read_text())["results"]["metrics_overall"]
        return m.get("class_only", {}).get("f1"), m.get("property_only", {}).get("f1")
    except Exception:
        return None, None

def top3_mean_f1(layer_json: Path):
    try:
        f1s = sorted((r.get("f1", 0.0) for r in json.loads(layer_json.read_text()).get("results", [])), reverse=True)
        return sum(f1s[:3]) / max(1, len(f1s[:3])) if f1s else None
    except Exception:
        return None

def roots_for(task, root, name, onto_mode):
    if task == "cq2term":
        return (root / "CQ2Term" / "04_summary" / name,
                root / "CQ2Term" / "03_evaluation_results" / name)
    return (root / "CQ2Onto" / "04_summary" / onto_mode / name,
            root / "CQ2Onto" / "03_evaluation_results" / onto_mode / name)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--onto-mode", default="challenge")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--commit", default="")
    args = ap.parse_args()
    root = Path(args.repo_root)
    name = args.name
    sub = root / "submissions" / name
    meta = yaml.safe_load((sub / "metadata.yml").read_text())
    tasks = [t for t in (meta.get("tasks") or []) if t in TASKS]

    # Single top-level output folder. Wipe and recreate so stale runs don't linger.
    out_root = sub / "result"
    if out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    # summary.md has no title heading (by request); it opens with the provenance line.
    lines = [f"_Generated {stamp}_" + (f" · commit `{args.commit[:7]}`" if args.commit else ""), ""]

    for task in tasks:
        sub_name = TASKS[task]                       # "CQ2Onto" / "CQ2Term"
        summary_root, res_root = roots_for(task, root, name, args.onto_mode)
        task_out = out_root / sub_name               # result/<Task>/

        # ---- result/<Task>/report/<domain>_report.md  (markdown) ----
        rep_out = task_out / "report"
        rep_out.mkdir(parents=True, exist_ok=True)
        reports = sorted(summary_root.glob("*_report.md")) if summary_root.exists() else []
        for rep in reports:
            shutil.copy2(rep, rep_out / rep.name)

        # ---- result/<Task>/result/  (numeric tree, mirror of 03_evaluation_results/<name>) ----
        if res_root.exists():
            shutil.copytree(res_root, task_out / "result", dirs_exist_ok=True)

        # ---- summary.md section ----
        lines.append(f"## {sub_name}"); lines.append("")
        if not reports:
            lines.append("_No report produced (task may have failed; check the run log)._"); lines.append(""); continue
        for rep in reports:
            dom = rep.name.replace("_report.md", "")
            link = f"{sub_name}/report/{rep.name}"     # relative to result/summary.md
            if task == "cq2term":
                cf, pf = cq2term_f1(res_root / dom)
                cs = f"{cf:.3f}" if cf is not None else "?"
                ps = f"{pf:.3f}" if pf is not None else "?"
                lines.append(f"- **{dom}** — class F1 {cs}, property F1 {ps}  ([{rep.name}]({link}))")
            else:
                cls = top3_mean_f1(res_root / dom / "01_class" / "class_result.json")
                cs = f"{cls:.3f}" if cls is not None else "?"
                lines.append(f"- **{dom}** — class F1 {cs} (full layers in report)  ([{rep.name}]({link}))")
        lines.append("")

    (out_root / "summary.md").write_text("\n".join(lines))
    n_md = sum(1 for _ in out_root.rglob("*_report.md"))
    n_num = sum(1 for _ in out_root.rglob("*")
                if _.is_file() and _.name not in {"summary.md"} and "/report/" not in _.as_posix())
    print(f"result/: {n_md} markdown report(s); {n_num} numeric file(s); tasks {tasks}")

if __name__ == "__main__":
    main()
