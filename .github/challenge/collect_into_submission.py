#!/usr/bin/env python3
"""
collect_into_submission.py

Creates submissions/<name>/result/ and, for each TASK listed in metadata.yml,
a task subfolder holding the per-ontology markdown reports the runners produced:

    submissions/<name>/result/
        CQ2Onto/<domain>_report.md     (only if cq2onto is in metadata tasks)
        CQ2Term/<domain>_report.md     (only if cq2term is in metadata tasks)
        SUMMARY.md                     (headline F1s; used for the PR comment)

Report sources produced by the runners:
    CQ2Term : CQ2Term/04_summary/<name>/<domain>_report.md
    CQ2Onto : CQ2Onto/04_summary/<onto_mode>/<name>/<domain>_report.md
"""
import argparse, json, shutil, datetime
from pathlib import Path
import yaml

# metadata task id -> (result subfolder name, summary-root builder)
TASKS = {
    "cq2onto": "CQ2Onto",
    "cq2term": "CQ2Term",
}

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

    result = sub / "result"
    if result.exists():
        shutil.rmtree(result)
    result.mkdir(parents=True, exist_ok=True)

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# Evaluation results — {name}", "",
             f"_Generated {stamp}_" + (f" · commit `{args.commit[:7]}`" if args.commit else ""), ""]

    for task in tasks:
        sub_name = TASKS[task]                       # "CQ2Onto" / "CQ2Term"
        out_dir = result / sub_name
        out_dir.mkdir(parents=True, exist_ok=True)

        if task == "cq2term":
            summary_root = root / "CQ2Term" / "04_summary" / name
            res_root = root / "CQ2Term" / "03_evaluation_results" / name
        else:
            summary_root = root / "CQ2Onto" / "04_summary" / args.onto_mode / name
            res_root = root / "CQ2Onto" / "03_evaluation_results" / args.onto_mode / name

        # copy every per-ontology markdown report into result/<Task>/
        reports = sorted(summary_root.glob("*_report.md")) if summary_root.exists() else []
        for rep in reports:
            shutil.copy2(rep, out_dir / rep.name)

        # headline numbers for SUMMARY.md
        lines.append(f"## {sub_name}")
        lines.append("")
        if not reports:
            lines.append("_No report produced (task may have failed; check the run log)._")
            lines.append("")
            continue
        for rep in reports:
            dom = rep.name.replace("_report.md", "")
            if task == "cq2term":
                cf, pf = cq2term_f1(res_root / dom)
                cs = f"{cf:.3f}" if cf is not None else "?"
                ps = f"{pf:.3f}" if pf is not None else "?"
                lines.append(f"- **{dom}** — class F1 {cs}, property F1 {ps}  ([{rep.name}]({sub_name}/{rep.name}))")
            else:
                cls = top3_mean_f1(res_root / dom / "01_class" / "class_result.json")
                cs = f"{cls:.3f}" if cls is not None else "?"
                lines.append(f"- **{dom}** — class F1 {cs} (full layers in report)  ([{rep.name}]({sub_name}/{rep.name}))")
        lines.append("")

    (result / "SUMMARY.md").write_text("\n".join(lines))
    n = sum(1 for _ in result.rglob("*_report.md"))
    print(f"Wrote {n} report(s) into {result} across tasks {tasks}")
    print(f"RESULT_DIR={result}")

if __name__ == "__main__":
    main()
