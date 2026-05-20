import argparse
import csv
import json
import os
import sys
from collections import defaultdict

def _normalize_term(t):
    if not isinstance(t, str):
        t = str(t)
    return t.strip().lower()


def _normalize_cq_entry(entry):
    classes = entry.get("explicit_classes")
    if classes is None:
        classes = entry.get("classes")
    if classes is None:
        classes = entry.get("class", [])
    props = entry.get("explicit_properties")
    if props is None:
        props = entry.get("properties")
    if props is None:
        props = entry.get("property", [])

    def _norm_list(xs):
        seen = set()
        out = []
        for x in xs:
            n = _normalize_term(x)
            if not n or n in seen:
                continue
            seen.add(n)
            out.append(n)
        return out

    question = entry.get("question") or entry.get("value", "")
    return {
        "id": entry.get("id") or entry.get("cq_id") or "",
        "question": question,
        "classes": _norm_list(classes),
        "properties": _norm_list(props),
    }


def load_cq_to_terms(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        raise ValueError(f"{json_path} must be a list of CQ objects")
    return [_normalize_cq_entry(e) for e in raw]


def collect_unique_terms(cq_table):
    classes_seen = []
    classes_set = set()
    props_seen = []
    props_set = set()
    for cq in cq_table:
        for c in cq["classes"]:
            if c not in classes_set:
                classes_set.add(c)
                classes_seen.append(c)
        for p in cq["properties"]:
            if p not in props_set:
                props_set.add(p)
                props_seen.append(p)
    return classes_seen, props_seen


def build_alignment(gold_terms, pred_terms, methods, top_n,
                    final_threshold, semantic_model=None):
    try:
        import concept_label_matching as clm
    except ImportError as e:
        raise RuntimeError(
            f"Could not import concept_label_matching. Make sure "
            f"concept_label_matching.py is in the same directory or on "
            f"PYTHONPATH. Error: {e}"
        )

    if not gold_terms or not pred_terms:
        print(f"  [warn] empty side: gold={len(gold_terms)} "
              f"pred={len(pred_terms)} — skipping alignment",
              file=sys.stderr)
        return []

    gold_input = list(gold_terms)
    pred_input = list(pred_terms)

    method_to_table = {}    # {method_name: score_table_list}
    used_methods = []
    for m in methods:
        if m == "synonym":
            print(f"  [info] Skipping 'synonym' method (NLTK disabled)",
                  file=sys.stderr)
            continue
        if m == "semantic" and not semantic_model:
            print(f"  [warn] Skipping 'semantic' method: no "
                  f"--semantic_model provided", file=sys.stderr)
            continue
        try:
            st = clm.compute_full_score_table(
                gen_class=pred_input,
                ground_class=gold_input,
                info_type=m,
                model_id=semantic_model if m == "semantic" else None,
            )
            method_to_table[m] = st
            used_methods.append(m)
        except Exception as e:
            print(f"  [warn] Method {m!r} failed: {e}", file=sys.stderr)

    if not method_to_table:
        return []

    best_map, trace = clm.build_best_class_map_top_n(
        all_score_tables=method_to_table,
        top_n=top_n,
        final_threshold=final_threshold,
        return_trace=True,
    )

    result_rows = []
    for row in trace:
        per_method = {}
        sbm_str = row.get("scores_by_method", "")
        if isinstance(sbm_str, str) and sbm_str:
            for chunk in sbm_str.split(";"):
                chunk = chunk.strip()
                if "=" in chunk:
                    name, val = chunk.split("=", 1)
                    try:
                        per_method[name.strip()] = float(val.strip())
                    except ValueError:
                        pass
        elif isinstance(sbm_str, dict):
            per_method = dict(sbm_str)
            sbm_str = "; ".join(f"{k}={v:.4f}"
                                 for k, v in sbm_str.items())

        result_rows.append({
            "gold_term": row.get("gold_term", ""),
            "pred_term": row.get("pred_term", ""),
            "top_methods_used": row.get("top_methods_used", ""),
            "scores_by_method": sbm_str,         # string form for CSV
            "per_method_scores": per_method,     # dict form for code
            "is_hard_match": bool(row.get("is_hard_match", False)),
            "avg_score": float(row.get("agg_score", 0.0)),
            "agg_score": float(row.get("agg_score", 0.0)),  # alias
            "accepted": bool(row.get("selected", False)),
            "selected": bool(row.get("selected", False)),    # alias
            "reason": row.get("reason", ""),
        })
    return result_rows


def alignment_to_simple_map(result_rows):
    out = {}
    for row in result_rows:
        if row["accepted"] and row["gold_term"] and row["pred_term"]:
            out[row["gold_term"]] = row["pred_term"]
    return out


def evaluate_per_method(gold_terms, pred_terms, methods, semantic_model=None):
    if not gold_terms or not pred_terms:
        return {}

    try:
        import concept_label_matching as clm
    except ImportError:
        return {}

    out = {}
    for m in methods:
        if m == "synonym":
            continue
        if m == "semantic" and not semantic_model:
            continue
        try:
            if m == "semantic":
                cov, p, r, f1, gmap, pmap = clm.cal_metrics(
                    list(pred_terms), list(gold_terms),
                    m, semantic_model)
                out_key = m  # keep simple key, not "semantic_<model>"
            else:
                cov, p, r, f1, gmap, pmap = clm.cal_metrics(
                    list(pred_terms), list(gold_terms), m)
                out_key = m
            n_matched = sum(1 for v in gmap.values() if v)
            out[out_key] = {
                "coverage": cov,
                "precision": p,
                "recall": r,
                "f1": f1,
                "n_matched": n_matched,
                "n_gold": len(gold_terms),
                "n_pred": len(pred_terms),
            }
        except Exception as e:
            print(f"  [warn] per-method {m!r} failed: {e}",
                  file=sys.stderr)
    return out

def compute_per_cq_coverage(gold_cq_table, pred_cq_table,
                            class_map, prop_map, mode="cq_local"):

    pred_terms_by_cq = {}
    for pcq in pred_cq_table:
        cqid = pcq["id"]
        pred_terms_by_cq[cqid] = {
            "classes": set(pcq.get("classes", [])),
            "properties": set(pcq.get("properties", [])),
        }

    all_pred_classes = set()
    all_pred_props = set()
    pred_class_to_cqs = {}
    pred_prop_to_cqs = {}
    for pcq in pred_cq_table:
        cqid = pcq["id"]
        for c in pcq.get("classes", []):
            all_pred_classes.add(c)
            pred_class_to_cqs.setdefault(c, []).append(cqid)
        for p in pcq.get("properties", []):
            all_pred_props.add(p)
            pred_prop_to_cqs.setdefault(p, []).append(cqid)

    rows = []
    n_missing_pred_cq = 0  # diagnostic: how many gold CQs have no pred counterpart
    for gold_cq in gold_cq_table:
        cq_id = gold_cq["id"]
        gold_classes = gold_cq["classes"]
        gold_props = gold_cq["properties"]

        if mode == "cq_local":
            pred_sets = pred_terms_by_cq.get(cq_id)
            if pred_sets is None:
                n_missing_pred_cq += 1
                pred_classes_here = set()
                pred_props_here = set()
            else:
                pred_classes_here = pred_sets["classes"]
                pred_props_here = pred_sets["properties"]
        else:
            pred_classes_here = all_pred_classes
            pred_props_here = all_pred_props

        covered_classes = []
        for g in gold_classes:
            mapped = class_map.get(g)
            if mapped and mapped in pred_classes_here:
                covered_classes.append({
                    "gold": g, "pred": mapped,

                    "pred_in_cqs": pred_class_to_cqs.get(mapped, []),
                })

        covered_props = []
        for g in gold_props:
            mapped = prop_map.get(g)
            if mapped and mapped in pred_props_here:
                covered_props.append({
                    "gold": g, "pred": mapped,
                    "pred_in_cqs": pred_prop_to_cqs.get(mapped, []),
                })

        n_gold = len(gold_classes) + len(gold_props)
        n_cov = len(covered_classes) + len(covered_props)
        coverage = (n_cov / n_gold) if n_gold else 0.0

        rows.append({
            "cq_id": cq_id,
            "question": gold_cq["question"],
            "n_gold_classes": len(gold_classes),
            "n_gold_properties": len(gold_props),
            "n_covered_classes": len(covered_classes),
            "n_covered_properties": len(covered_props),
            "coverage": coverage,
            "covered_classes": covered_classes,
            "covered_properties": covered_props,
            "missing_classes": [g for g in gold_classes
                                if not any(c["gold"] == g
                                           for c in covered_classes)],
            "missing_properties": [g for g in gold_props
                                   if not any(p["gold"] == g
                                              for p in covered_props)],
            "mode": mode,
        })
    if mode == "cq_local" and n_missing_pred_cq > 0:
        gold_ids = {gcq["id"] for gcq in gold_cq_table}
        pred_ids = set(pred_terms_by_cq.keys())
        missing_in_pred = sorted(gold_ids - pred_ids)
        extra_in_pred = sorted(pred_ids - gold_ids)
        print(f"\n  [WARN] CQ id mismatch detected — cq_local mode "
              f"requires gold/pred CQ ids to correspond 1-to-1.",
              file=sys.stderr)
        print(f"    {len(missing_in_pred)} gold CQ id(s) have no "
              f"pred counterpart (these score 0): "
              f"{missing_in_pred[:10]}"
              + (" ..." if len(missing_in_pred) > 10 else ""),
              file=sys.stderr)
        if extra_in_pred:
            print(f"    {len(extra_in_pred)} pred CQ id(s) are not in "
                  f"gold (ignored): "
                  f"{extra_in_pred[:10]}"
                  + (" ..." if len(extra_in_pred) > 10 else ""),
                  file=sys.stderr)
        print(f"    Check your CQ id formatting and confirm gold "
              f"and pred share the same CQ list.\n",
              file=sys.stderr)
    return rows

def compute_per_term_coverage(gold_cq_table, class_map, prop_map):

    term_to_cqs_class = defaultdict(set)
    term_to_cqs_prop = defaultdict(set)
    for cq in gold_cq_table:
        for c in cq["classes"]:
            term_to_cqs_class[c].add(cq["id"])
        for p in cq["properties"]:
            term_to_cqs_prop[p].add(cq["id"])

    rows = []
    for term, cqs in sorted(term_to_cqs_class.items()):
        rows.append({
            "term": term,
            "role": "class",
            "cq_ids": sorted(cqs),
            "aligned": term in class_map,
            "aligned_to": class_map.get(term, ""),
        })
    for term, cqs in sorted(term_to_cqs_prop.items()):
        rows.append({
            "term": term,
            "role": "property",
            "cq_ids": sorted(cqs),
            "aligned": term in prop_map,
            "aligned_to": prop_map.get(term, ""),
        })
    return rows

def aggregate_metrics_full(gold_cq_table, pred_cq_table,
                           class_map, prop_map):
    inv_class = {v: k for k, v in class_map.items()}
    inv_prop = {v: k for k, v in prop_map.items()}

    gold_classes = set()
    gold_props = set()
    for cq in gold_cq_table:
        gold_classes.update(cq["classes"])
        gold_props.update(cq["properties"])
    pred_classes = set()
    pred_props = set()
    for cq in pred_cq_table:
        pred_classes.update(cq["classes"])
        pred_props.update(cq["properties"])

    def _score(gold_set, pred_set, gold_to_pred, inv_pred_to_gold):
        tp = fp = fn = 0
        tp_pairs = []
        fn_terms = []
        fp_terms = []
        for g in gold_set:
            mapped = gold_to_pred.get(g)
            if mapped and mapped in pred_set:
                tp += 1
                tp_pairs.append({"gold": g, "pred": mapped})
            else:
                fn += 1
                fn_terms.append(g)
        for p in pred_set:
            if p not in inv_pred_to_gold:
                fp += 1
                fp_terms.append(p)
        pr = tp / (tp + fp) if (tp + fp) else 0.0
        re = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (2 * pr * re / (pr + re)) if (pr + re) else 0.0
        return {
            "tp": tp, "fp": fp, "fn": fn,
            "precision": pr, "recall": re, "f1": f1,
            "n_gold": len(gold_set), "n_pred": len(pred_set),
            "tp_pairs": tp_pairs,
            "fn_terms": fn_terms,
            "fp_terms": fp_terms,
        }

    cls = _score(gold_classes, pred_classes, class_map, inv_class)
    prp = _score(gold_props, pred_props, prop_map, inv_prop)

    tp = cls["tp"] + prp["tp"]
    fp = cls["fp"] + prp["fp"]
    fn = cls["fn"] + prp["fn"]
    pr = tp / (tp + fp) if (tp + fp) else 0.0
    re = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * pr * re / (pr + re)) if (pr + re) else 0.0
    combined = {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": pr, "recall": re, "f1": f1,
        "n_gold": cls["n_gold"] + prp["n_gold"],
        "n_pred": cls["n_pred"] + prp["n_pred"],
    }

    return {
        "class_only": cls,
        "property_only": prp,
        "combined": combined,
    }


def save_alignment_csv(result_rows, path, role_label=None):
    fields = ["role", "gold_term", "pred_term",
              "top_methods_used", "scores_by_method",
              "is_hard_match", "agg_score", "selected", "reason"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in result_rows:
            w.writerow({
                "role": role_label or "",
                "gold_term": r.get("gold_term", ""),
                "pred_term": r.get("pred_term", ""),
                "top_methods_used": r.get("top_methods_used", ""),
                "scores_by_method": r.get("scores_by_method", ""),
                "is_hard_match": r.get("is_hard_match", False),
                "agg_score": f"{r.get('avg_score', 0.0):.4f}",
                "selected": r.get("accepted", False),
                "reason": r.get("reason", ""),
            })
    print(f"  Saved alignment trace CSV to: {path}", file=sys.stderr)


def save_best_matching_csv(result_rows, path):

    headers = ["Gold_term", "Pre_term", "Method", "Score"]
    accepted = [r for r in result_rows if r.get("accepted")]

    accepted.sort(key=lambda r: r.get("gold_term", ""))

    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for r in accepted:

            scores = r.get("per_method_scores", {}) or {}
            if scores:
                top = sorted(scores.items(),
                             key=lambda kv: -kv[1])[:3]
                method_str = "+".join(m for m, _ in top)
                if scores.get("hard_match", 0.0) >= 1.0:
                    method_str = "hard_match"
                else:
                    method_str = f"top3_avg({method_str})"
            else:
                method_str = ""
            w.writerow([
                r.get("gold_term", ""),
                r.get("pred_term", ""),
                method_str,
                f"{r.get('avg_score', 0.0):.4f}",
            ])
    print(f"  Saved best-matching CSV to: {path}", file=sys.stderr)


def save_cq_coverage_csv(rows, path):
    fields = ["cq_id", "question", "n_gold_classes", "n_gold_properties",
              "n_covered_classes", "n_covered_properties", "coverage",
              "missing_classes", "missing_properties"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({
                "cq_id": r["cq_id"],
                "question": r["question"],
                "n_gold_classes": r["n_gold_classes"],
                "n_gold_properties": r["n_gold_properties"],
                "n_covered_classes": r["n_covered_classes"],
                "n_covered_properties": r["n_covered_properties"],
                "coverage": f"{r['coverage']:.4f}",
                "missing_classes": "; ".join(r["missing_classes"]),
                "missing_properties": "; ".join(r["missing_properties"]),
            })
    print(f"  Saved CQ-coverage CSV to: {path}", file=sys.stderr)


def save_term_coverage_csv(rows, path):
    fields = ["term", "role", "cq_ids", "aligned", "aligned_to"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({
                "term": r["term"],
                "role": r["role"],
                "cq_ids": "; ".join(r["cq_ids"]),
                "aligned": "true" if r["aligned"] else "false",
                "aligned_to": r["aligned_to"],
            })
    print(f"  Saved term-coverage CSV to: {path}", file=sys.stderr)


def save_result_json(config, results, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"config": config, "results": results},
                  f, ensure_ascii=False, indent=2)
    print(f"  Saved result JSON to: {path}", file=sys.stderr)


def build_report_md(config, gold_cq_table, pred_cq_table,
                    class_align, prop_align,
                    per_method_class, per_method_prop,
                    per_cq, per_term, metrics, args):
    L = []
    L.append("# CQ2Term Evaluation Report")
    L.append("")
    L.append("_Generated by `eval_cq_terms.py`_  ")
    L.append(f"_Gold: `{args.gold_cq_to_terms}` · "
             f"Pred: `{args.pred_cq_to_terms}`_  ")
    L.append(f"_Methods: `{', '.join(config['methods'])}` · "
             f"top-N: {config['top_n']} · "
             f"final_threshold: {config['final_threshold']}_")
    L.append("")
    L.append("Evaluation Five steps:")
    L.append("")
    L.append("1. **Term statistics** — count gold vs pred terms by role")
    L.append("2. **Per-method matching** — hard / lexical / semantic "
             "at various thresholds, reporting method-level "
             "gold-term coverage")
    L.append("3. **Best matching** — top-N average + final_threshold + "
             "1-to-1 selection")
    L.append("4. **Term-level metrics** — P/R/F1 over the set "
             "of unique terms, ignoring CQ id")
    L.append("5. **CQ coverage** — per-CQ accuracy under cq_local "
             "mode, with at-least-one / average / fully-covered views")
    L.append("")

    def _accepted(rows):
        return sum(1 for r in rows if r["accepted"])

    L.append("## Step 1 — Term Statistics")

    def _collect(cq_table):
        cls = set()
        prp = set()
        for cq in cq_table:
            cls.update(cq["classes"])
            prp.update(cq["properties"])
        return cls, prp

    gold_classes_set, gold_props_set = _collect(gold_cq_table)
    pred_classes_set, pred_props_set = _collect(pred_cq_table)

    L.append("### Summary")
    L.append("")
    L.append("| Side | CQs | Unique classes | Unique properties | "
             "Total unique terms |")
    L.append("|---|---:|---:|---:|---:|")
    L.append(f"| Gold | {len(gold_cq_table)} | "
             f"{len(gold_classes_set)} | {len(gold_props_set)} | "
             f"{len(gold_classes_set) + len(gold_props_set)} |")
    L.append(f"| Pred | {len(pred_cq_table)} | "
             f"{len(pred_classes_set)} | {len(pred_props_set)} | "
             f"{len(pred_classes_set) + len(pred_props_set)} |")
    L.append("")

    L.append("### Class Terms")
    L.append("")
    L.append(f"- **Gold classes ({len(gold_classes_set)}):** "
             + (", ".join(f"`{c}`" for c in sorted(gold_classes_set))
                if gold_classes_set else "_none_"))
    L.append("")
    L.append(f"- **Pred classes ({len(pred_classes_set)}):** "
             + (", ".join(f"`{c}`" for c in sorted(pred_classes_set))
                if pred_classes_set else "_none_"))
    L.append("")
    g_ci_c = {c.lower() for c in gold_classes_set}
    p_ci_c = {c.lower() for c in pred_classes_set}
    L.append(f"- _Exact (case-insensitive) overlap: "
             f"**{len(g_ci_c & p_ci_c)}**  ·  "
             f"only in gold: **{len(g_ci_c - p_ci_c)}**  ·  "
             f"only in pred: **{len(p_ci_c - g_ci_c)}**_")
    L.append("")

    L.append("### Property Terms")
    L.append("")
    L.append(f"- **Gold properties ({len(gold_props_set)}):** "
             + (", ".join(f"`{p}`" for p in sorted(gold_props_set))
                if gold_props_set else "_none_"))
    L.append("")
    L.append(f"- **Pred properties ({len(pred_props_set)}):** "
             + (", ".join(f"`{p}`" for p in sorted(pred_props_set))
                if pred_props_set else "_none_"))
    L.append("")
    g_ci_p = {p.lower() for p in gold_props_set}
    p_ci_p = {p.lower() for p in pred_props_set}
    L.append(f"- _Exact (case-insensitive) overlap: "
             f"**{len(g_ci_p & p_ci_p)}**  ·  "
             f"only in gold: **{len(g_ci_p - p_ci_p)}**  ·  "
             f"only in pred: **{len(p_ci_p - g_ci_p)}**_")
    L.append("")

    L.append("## Step 2 — Per-Method Matching Results (P/R/F1)")
    L.append("")

    try:
        import concept_label_matching as _clm
        HARD_T = getattr(_clm, "HARD_THRESHOLD", 1.0)
        LEX_T = getattr(_clm, "LEXICAL_THRESHOLD", 0.8)
        SEM_T = getattr(_clm, "SEMANTIC_THRESHOLD", 0.6)
    except Exception:
        HARD_T, LEX_T, SEM_T = 1.0, 0.8, 0.6

    L.append(f"Each method runs an **independent 1-to-1 greedy "
             f"matching** at its own conventional threshold "
             f"(`hard_match` = `{HARD_T}`; lexical = `{LEX_T}`; "
             f"semantic = `{SEM_T}`) and reports its own "
             f"method-level gold-term coverage, plus Precision, "
             f"Recall, F1. These numbers are diagnostic. They show "
             f"how each individual method would perform on its own, "
             f"before the top-N aggregation in Step 3. The "
             f"`Coverage` column here is the fraction of gold terms "
             f"that this single method aligned to a pred term. It "
             f"is not the same as the per-CQ coverage reported in "
             f"Step 5.")
    L.append("")

    def _emit_per_method_table(per_method_dict, role_label, n_gold):
        L.append(f"### {role_label} alignment ({n_gold} gold terms)")
        L.append("")
        if not per_method_dict:
            L.append("_No methods evaluated (empty input or all "
                     "methods skipped)._")
            L.append("")
            return
        L.append("| Method | TP_gold | Coverage | Precision | "
                 "Recall | F1 |")
        L.append("|---|---:|---:|---:|---:|---:|")
        for method in sorted(per_method_dict.keys()):
            r = per_method_dict[method]
            cov = r.get("coverage", 0.0)
            p = r.get("precision", 0.0)
            rec = r.get("recall", 0.0)
            f1 = r.get("f1", 0.0)
            tp_gold = int(round(rec * n_gold))
            L.append(f"| `{method}` | {tp_gold}/{n_gold} | "
                     f"{cov*100:.1f}% | {p*100:.1f}% | "
                     f"{rec*100:.1f}% | {f1*100:.1f}% |")
        L.append("")

    g_classes = set()
    g_props = set()
    for cq in gold_cq_table:
        g_classes.update(cq["classes"])
        g_props.update(cq["properties"])

    _emit_per_method_table(per_method_class, "Class", len(g_classes))
    _emit_per_method_table(per_method_prop, "Property", len(g_props))

    L.append("## Step 3 — Best Matching Selection")
    L.append("")
    L.append(f"Each pair's per-method scores are averaged over the **top "
             f"{config['top_n']}** methods, then pairs below "
             f"**{config['final_threshold']}** are dropped. A greedy "
             f"1-to-1 selection picks the final alignment map.")

    if class_align:
        accepted_class = [r for r in class_align if r["accepted"]]
        if accepted_class:
            L.append("### Accepted class alignments")
            L.append("")
            L.append("| Gold | Pred | Avg score | Top methods |")
            L.append("|---|---|---:|---|")
            for r in sorted(accepted_class,
                            key=lambda x: -x["avg_score"]):
                top_methods = sorted(
                    r["per_method_scores"].items(),
                    key=lambda x: -x[1])[:3]
                methods_str = ", ".join(
                    f"{m}={s:.2f}" for m, s in top_methods)
                L.append(f"| `{r['gold_term']}` | `{r['pred_term']}` | "
                         f"{r['avg_score']:.3f} | {methods_str} |")
            L.append("")

    if prop_align:
        accepted_prop = [r for r in prop_align if r["accepted"]]
        if accepted_prop:
            L.append("### Accepted property alignments")
            L.append("")
            L.append("| Gold | Pred | Avg score | Top methods |")
            L.append("|---|---|---:|---|")
            for r in sorted(accepted_prop,
                            key=lambda x: -x["avg_score"]):
                top_methods = sorted(
                    r["per_method_scores"].items(),
                    key=lambda x: -x[1])[:3]
                methods_str = ", ".join(
                    f"{m}={s:.2f}" for m, s in top_methods)
                L.append(f"| `{r['gold_term']}` | `{r['pred_term']}` | "
                         f"{r['avg_score']:.3f} | {methods_str} |")
            L.append("")

    cls_m = metrics["class_only"]
    prp_m = metrics["property_only"]
    com_m = metrics["combined"]

    L.append("## Step 4 — Term-level Metrics")
    L.append("")
    L.append("Aggregated over the **set of unique terms** across all "
             "CQs, ignoring CQ id. This answers the coarse question: "
             "_does pred know the right concepts for this domain?_")
    L.append("")
    L.append("Per-CQ accuracy (_does pred mention the right concepts "
             "in the right CQ?_) is reported separately in Step 5. "
             "The two metrics can diverge: an LLM with strong "
             "vocabulary but weak CQ-specific reasoning will score "
             "higher here than on per-CQ coverage.")
    L.append("")
    L.append("- TP = gold term has an aligned pred term that appears "
             "anywhere in pred")
    L.append("- FN = gold term not covered by any pred term")
    L.append("- FP = pred term doesn't translate back to any gold term")
    L.append("")
    L.append("| Granularity | Gold | Pred | TP | FP | FN | "
             "Precision | Recall | F1 |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for label, m in [("Class only", cls_m),
                     ("Property only", prp_m),
                     ("**Combined (all terms)**", com_m)]:
        L.append(f"| {label} | {m['n_gold']} | {m['n_pred']} | "
                 f"{m['tp']} | {m['fp']} | {m['fn']} | "
                 f"{m['precision']*100:.1f}% | "
                 f"{m['recall']*100:.1f}% | "
                 f"{m['f1']*100:.1f}% |")
    L.append("")

    if cls_m.get("fn_terms") or prp_m.get("fn_terms"):
        L.append("**Missed gold terms (FN):**")
        L.append("")
        if cls_m.get("fn_terms"):
            L.append(f"- Classes ({len(cls_m['fn_terms'])}): "
                     + ", ".join(f"`{t}`" for t in cls_m["fn_terms"]))
        if prp_m.get("fn_terms"):
            L.append(f"- Properties ({len(prp_m['fn_terms'])}): "
                     + ", ".join(f"`{t}`" for t in prp_m["fn_terms"]))
        L.append("")
    if cls_m.get("fp_terms") or prp_m.get("fp_terms"):
        L.append("**Extra pred terms (FP) — don't translate to any gold term:**")
        L.append("")
        if cls_m.get("fp_terms"):
            L.append(f"- Classes ({len(cls_m['fp_terms'])}): "
                     + ", ".join(f"`{t}`" for t in cls_m["fp_terms"]))
        if prp_m.get("fp_terms"):
            L.append(f"- Properties ({len(prp_m['fp_terms'])}): "
                     + ", ".join(f"`{t}`" for t in prp_m["fp_terms"]))
        L.append("")

    L.append("### Per-term Coverage Overview")
    L.append("")
    L.append("For each gold term, did it find an aligned "
             "pred term, and which gold CQs does it appear in?")
    L.append("")
    n_aligned = sum(1 for r in per_term if r["aligned"])
    L.append(f"**{n_aligned} / {len(per_term)} gold terms aligned to "
             f"some pred term.**")
    L.append("")
    L.append("| Term | Role | CQs | Aligned | Aligned to |")
    L.append("|---|---|---|:-:|---|")
    for r in per_term:
        ok = "Y" if r["aligned"] else "N"
        cqs = ", ".join(r["cq_ids"])
        L.append(f"| `{r['term']}` | {r['role']} | {cqs} | {ok} | "
                 f"`{r['aligned_to']}` |")
    L.append("")

    L.append("## Step 5 — CQ Coverage")
    L.append("")
    cq_mode = per_cq[0].get("mode", "cq_local") if per_cq else "cq_local"
    if cq_mode == "cq_local":
        L.append("For each gold CQ, coverage is computed over its gold terms "
             "(classes and properties). A term is counted as covered only "
             "when its aligned pred term appears in the pred CQ with the "
             "same CQ id. This enforces CQ-local correctness.")
    else:
        L.append("For each gold CQ, coverage is computed over its gold terms "
             "(classes and properties). A term is counted as covered if "
             "its aligned pred term appears anywhere in the pred output. "
             "This lenient global mode is intended only for cases where "
             "gold and pred CQ ids cannot be reliably matched, and may "
             "overestimate performance by crediting terms assigned to the "
             "wrong CQ.")
    L.append("")
    L.append("Alignment is performed globally at the term level with a 1-to-1 "
         "mapping across systems. Coverage then projects this mapping back "
         "onto each CQ, so the evaluation separates vocabulary alignment "
         "from CQ-specific term assignment.")
    L.append("")

    n_cq_total = len(per_cq)
    n_cq_any = sum(1 for r in per_cq if r["coverage"] > 0.0)
    n_cq_full = sum(1 for r in per_cq if r["coverage"] >= 1.0)
    avg_cov = (sum(r["coverage"] for r in per_cq) / n_cq_total
               if n_cq_total else 0.0)

    L.append("### Overall CQ coverage rate")
    L.append("")
    L.append("| View | Value | Meaning |")
    L.append("|---|---:|---|")
    L.append(f"| Covered CQs (partial counts) | "
             f"**{n_cq_any}/{n_cq_total} = "
             f"{(n_cq_any/n_cq_total*100 if n_cq_total else 0):.1f}%** | "
             f"CQs where pred covers at least one gold term |")
    L.append(f"| Average per-CQ coverage | **{avg_cov*100:.1f}%** | "
             f"mean of each CQ's coverage % |")
    L.append(f"| Fully (100%) covered CQs | "
             f"**{n_cq_full}/{n_cq_total} = "
             f"{(n_cq_full/n_cq_total*100 if n_cq_total else 0):.1f}%** | "
             f"CQs where pred covers every gold term |")
    L.append("")

    L.append("| CQ id | Question | Gold (Classes/Properties) | Covered (Classes/Properties) | "
             "Coverage | Missing |")
    L.append("|---|---|---|---|---:|---|")
    for r in per_cq:
        q = (r["question"] or "").replace("|", "\\|")
        miss = []
        if r["missing_classes"]:
            miss.append(f"C: {', '.join(r['missing_classes'])}")
        if r["missing_properties"]:
            miss.append(f"P: {', '.join(r['missing_properties'])}")
        miss_str = " · ".join(miss) if miss else "—"
        L.append(f"| {r['cq_id']} | {q} | "
                 f"{r['n_gold_classes']}/{r['n_gold_properties']} | "
                 f"{r['n_covered_classes']}/{r['n_covered_properties']} | "
                 f"{r['coverage']*100:.1f}% | {miss_str} |")
    L.append("")
    L.append("")
    return "\n".join(L)


def append_report_md(report_text, path):
    marker = "# CQ2Term Evaluation Report"
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"  Created MD: {path}", file=sys.stderr)
        return
    with open(path, "r", encoding="utf-8") as f:
        existing = f.read()
    if marker in existing:
        idx = existing.find(marker)
        prefix = existing[:idx].rstrip()
        if prefix.endswith("---"):
            prefix = prefix[:-3].rstrip()
        new = prefix + "\n\n---\n\n" + report_text
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        print(f"  Replaced existing CQ-term section in: {path}",
              file=sys.stderr)
        return
    if not existing.endswith("\n"):
        existing += "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(existing + "\n---\n\n" + report_text)
    print(f"  Appended CQ-term section to: {path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--gold_cq_to_terms", required=True,
                        help="Gold CQ→terms JSON")
    parser.add_argument("--pred_cq_to_terms", required=True,
                        help="Pred CQ→terms JSON (same shape)")

    parser.add_argument("--methods",
                        default="hard_match,jaro_winkler,levenshtein,"
                                "semantic,sequence_match",
                        help="Comma-separated alignment methods")
    parser.add_argument("--top_n", type=int, default=3,
                        help="Top-N method scores to average per pair")
    parser.add_argument("--final_threshold", type=float, default=0.6,
                        help="Drop pairs with averaged top-N score "
                             "below this")
    

    parser.add_argument("--semantic_threshold", type=float, default=None,
                    help="Per-method threshold for the 'semantic' "
                         "method. Defaults to 0.6 if not set.")
    parser.add_argument("--lexical_threshold", type=float, default=None,
                    help="Per-method threshold for lexical methods "
                         "(levenshtein, jaro_winkler, sequence_match). "
                         "Defaults to 0.8 if not set.")
    parser.add_argument("--hard_threshold", type=float, default=None,
                    help="Per-method threshold for 'hard_match'. "
                         "Defaults to 1.0 if not set.")
    parser.add_argument("--semantic_model", default="embeddinggemma:latest",
                        help="Ollama model for the 'semantic' method")

    parser.add_argument("--save_class_alignment_csv", default=None,
                        help="Trace CSV for class-only alignment")
    parser.add_argument("--save_property_alignment_csv", default=None,
                        help="Trace CSV for property-only alignment")
    parser.add_argument("--save_class_best_matching_csv", default=None,
                        help="Best-matching CSV for class alignment "
                             "(only accepted pairs, same shape as "
                             "class_best_matching.csv: "
                             "Gold_term,Pre_term,Method,Score)")
    parser.add_argument("--save_property_best_matching_csv", default=None,
                        help="Best-matching CSV for property alignment "
                             "(only accepted pairs, same shape as "
                             "property_best_matching.csv)")
    parser.add_argument("--save_cq_coverage_csv", default=None)
    parser.add_argument("--save_term_coverage_csv", default=None)
    parser.add_argument("--save_result_json", default=None)
    parser.add_argument("--save_report_md", default=None)
    parser.add_argument(
        "--cq_coverage_mode",
        choices=["cq_local", "global"],
        default="cq_local",
        help="How to count gold-term coverage per CQ:\n"
             "  cq_local (default): a gold term G in gold CQ_i is "
             "covered if its globally aligned pred term P appears "
             "in pred CQ_i (same id). This is the correct evaluation "
             "when gold and pred share the same CQ list.\n"
             "  global: lenient — G is covered if P appears anywhere "
             "in pred. Diagnostic use only — overestimates LLM "
             "capability by crediting pred for mentioning the right "
             "term in the wrong CQ.")

    args = parser.parse_args()

    import concept_label_matching as _clm
    if any(t is not None for t in (args.semantic_threshold,
                               args.lexical_threshold,
                               args.hard_threshold)):
        _clm.override_thresholds(
        semantic=args.semantic_threshold,
        lexical=args.lexical_threshold,
        hard=args.hard_threshold,
    )

# ...
    print(f"Per-method thresholds: "
    f"hard={_clm.HARD_THRESHOLD}, "
    f"lexical={_clm.LEXICAL_THRESHOLD}, "
    f"semantic={_clm.SEMANTIC_THRESHOLD}",
    file=sys.stderr)

    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    print(f"Methods: {methods}", file=sys.stderr)
    print(f"Top-N: {args.top_n}", file=sys.stderr)
    print(f"Final threshold: {args.final_threshold}", file=sys.stderr)

    print(f"\nLoading gold from {args.gold_cq_to_terms!r}...",
          file=sys.stderr)
    gold_cq_table = load_cq_to_terms(args.gold_cq_to_terms)
    print(f"  {len(gold_cq_table)} gold CQs", file=sys.stderr)

    print(f"Loading pred from {args.pred_cq_to_terms!r}...",
          file=sys.stderr)
    pred_cq_table = load_cq_to_terms(args.pred_cq_to_terms)
    print(f"  {len(pred_cq_table)} pred CQs", file=sys.stderr)

    gold_classes, gold_props = collect_unique_terms(gold_cq_table)
    pred_classes, pred_props = collect_unique_terms(pred_cq_table)
    print(f"\nUnique gold terms: {len(gold_classes)} classes, "
          f"{len(gold_props)} properties", file=sys.stderr)
    print(f"Unique pred terms: {len(pred_classes)} classes, "
          f"{len(pred_props)} properties", file=sys.stderr)

    print("\n=== Alignment 1/2: class-only ===", file=sys.stderr)
    class_align = build_alignment(
        gold_terms=gold_classes, pred_terms=pred_classes,
        methods=methods, top_n=args.top_n,
        final_threshold=args.final_threshold,
        semantic_model=args.semantic_model,
    )

    print("\n=== Alignment 2/2: property-only ===", file=sys.stderr)
    prop_align = build_alignment(
        gold_terms=gold_props, pred_terms=pred_props,
        methods=methods, top_n=args.top_n,
        final_threshold=args.final_threshold,
        semantic_model=args.semantic_model,
    )

    print("\n=== Per-method evaluation (Layer 2 style) ===",
          file=sys.stderr)
    per_method_class = evaluate_per_method(
        gold_terms=gold_classes, pred_terms=pred_classes,
        methods=methods, semantic_model=args.semantic_model,
    )
    per_method_prop = evaluate_per_method(
        gold_terms=gold_props, pred_terms=pred_props,
        methods=methods, semantic_model=args.semantic_model,
    )

    class_map = alignment_to_simple_map(class_align)
    prop_map = alignment_to_simple_map(prop_align)
    print(f"\nClass alignments accepted: {len(class_map)} / "
          f"{len(gold_classes)}", file=sys.stderr)
    print(f"Property alignments accepted: {len(prop_map)} / "
          f"{len(gold_props)}", file=sys.stderr)

    print("\n=== Computing per-term coverage ===", file=sys.stderr)
    per_term = compute_per_term_coverage(gold_cq_table, class_map, prop_map)
    n_aligned = sum(1 for r in per_term if r["aligned"])
    print(f"  {n_aligned} / {len(per_term)} gold terms aligned",
          file=sys.stderr)

    print("\n=== Computing aggregate metrics (3 granularities) ===",
          file=sys.stderr)
    metrics = aggregate_metrics_full(gold_cq_table, pred_cq_table,
                                     class_map, prop_map)
    for label, key in [("Class only", "class_only"),
                       ("Property only", "property_only"),
                       ("Combined", "combined")]:
        m = metrics[key]
        print(f"  {label:<14}  TP={m['tp']:>3} FP={m['fp']:>3} "
              f"FN={m['fn']:>3}  "
              f"P={m['precision']*100:5.1f}%  "
              f"R={m['recall']*100:5.1f}%  "
              f"F1={m['f1']*100:5.1f}%", file=sys.stderr)

    print("\n=== Computing per-CQ coverage ===", file=sys.stderr)
    per_cq = compute_per_cq_coverage(gold_cq_table, pred_cq_table,
                                     class_map, prop_map,
                                     mode=args.cq_coverage_mode)
    n_full = 0
    avg_cov = 0.0
    for r in per_cq:
        if r["coverage"] >= 1.0:
            n_full += 1
        avg_cov += r["coverage"]
        print(f"  {r['cq_id']:<8} {r['n_covered_classes']}/"
              f"{r['n_gold_classes']} cls + "
              f"{r['n_covered_properties']}/{r['n_gold_properties']} prop "
              f"= {r['coverage']*100:.1f}%", file=sys.stderr)
    if per_cq:
        avg_cov /= len(per_cq)
    print(f"  ----  {n_full}/{len(per_cq)} CQs fully covered, "
          f"avg = {avg_cov*100:.1f}%", file=sys.stderr)

    print("\n=== Saving outputs ===", file=sys.stderr)
    if args.save_class_alignment_csv:
        save_alignment_csv(class_align, args.save_class_alignment_csv,
                           role_label="class")
    if args.save_property_alignment_csv:
        save_alignment_csv(prop_align, args.save_property_alignment_csv,
                           role_label="property")
    if args.save_class_best_matching_csv:
        save_best_matching_csv(class_align,
                               args.save_class_best_matching_csv)
    if args.save_property_best_matching_csv:
        save_best_matching_csv(prop_align,
                               args.save_property_best_matching_csv)
    if args.save_cq_coverage_csv:
        save_cq_coverage_csv(per_cq, args.save_cq_coverage_csv)
    if args.save_term_coverage_csv:
        save_term_coverage_csv(per_term, args.save_term_coverage_csv)

    config = {
        "gold_cq_to_terms": args.gold_cq_to_terms,
        "pred_cq_to_terms": args.pred_cq_to_terms,
        "methods": methods,
        "top_n": args.top_n,
        "final_threshold": args.final_threshold,
        "semantic_model": args.semantic_model,
        # MOD: stamp cli_args so the leaderboard can group runs by config.
        "cli_args": {
            k: (str(v) if hasattr(v, "__fspath__") else v)
            for k, v in vars(args).items()
        },
    }
    if args.save_result_json:
        save_result_json(config, {
            "metrics_overall": metrics,
            # MOD: persist per-method P/R/F1 for class and property terms.
            "per_method_class":    per_method_class,
            "per_method_property": per_method_prop,
            "alignments": {
                "class":    class_align,
                "property": prop_align,
            },
            "per_cq_coverage": per_cq,
            "per_term_coverage": per_term,
        }, args.save_result_json)

    if args.save_report_md:
        report = build_report_md(config, gold_cq_table, pred_cq_table,
                                 class_align, prop_align,
                                 per_method_class, per_method_prop,
                                 per_cq, per_term,
                                 metrics, args)
        append_report_md(report, args.save_report_md)


if __name__ == "__main__":
    main()
