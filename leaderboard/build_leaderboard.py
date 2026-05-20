"""
build_leaderboard.py  (v4)

Scans CQ4OE evaluation results for BOTH benchmarks and writes a JS
data file consumed by leaderboard.html.

Benchmarks and tasks:
    CQ2Term:
        - term_recovery  (1 task)
    CQ2Onto:
        - term_recovery
        - property_chars
        - triple
        - axiom
        - hierarchy   (5 tasks)

Total: 6 task tabs.

Metric coverage matches paper Table 2:
    - Per-method P/R/F1 for term-recovery tasks (5 methods × 2 term types)
    - Aggregated (top-3 mean) P/R/F1 for term-recovery
    - AC / G P/R/F1 for property_chars, triple, axiom
    - Cosine diagnostic for triple (and axiom, if --no_layer2 is OFF)
    - CQ coverage:
        * CQ2Term term-recovery: At-least-one / Mean / Full
        * CQ2Onto axiom: Axiom@1 / Axiom-Mean / Axiom-Full
        * CQ2Onto hierarchy: Closure@1 / Closure-Mean / Closure-Full

Configuration is read from each layer's config.cli_args (set by patched
eval_*.py scripts). Runs are grouped by full config tuple.

Usage:
    python build_leaderboard.py \\
        --cq2term_root CQ2Term/03_evaluation_results \\
        --cq2onto_root CQ2Onto/03_evaluation_results \\
        --html_data    docs/leaderboard_data.js \\
        --markdown_out docs/leaderboard.md \\
        --assume_config "literal_relax=no,threshold=0.6,no_layer2=True"
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

METHODS = ["hard_match", "sequence_match", "levenshtein", "jaro_winkler", "semantic"]

# Domain order matches paper Table 1: Small (Wine, AWO) → Medium (ODRL, SAREF4WATR)
# → Large (VGO, SWO).
DOMAIN_ORDER = ["wine", "awo", "odrl", "water", "vgo", "swo"]


def order_datasets(datasets):
    """Sort datasets following the paper's Small→Large tier order."""
    known = [d for d in DOMAIN_ORDER if d in datasets]
    unknown = sorted(d for d in datasets if d not in DOMAIN_ORDER)
    return known + unknown


# ─────────────────────────────────────────────────────────────────
# Generic helpers
# ─────────────────────────────────────────────────────────────────

def _prf1(tp: int, fp: int, fn: int) -> dict:
    p = tp / (tp + fp) * 100 if (tp + fp) > 0 else None
    r = tp / (tp + fn) * 100 if (tp + fn) > 0 else None
    f1 = 2 * p * r / (p + r) if (p is not None and r is not None and (p + r) > 0) else None
    return {"p": p, "r": r, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def _load_json(path: Path) -> dict | None:
    try:
        return json.load(open(path, "r", encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _from_prf1(obj: dict | None) -> dict | None:
    """Convert {precision, recall, f1, tp, fp, fn} (decimals) to our format (percent)."""
    if not obj:
        return None
    p = obj.get("precision")
    r = obj.get("recall")
    f1 = obj.get("f1")
    return {
        "p":  p * 100 if isinstance(p, (int, float)) else None,
        "r":  r * 100 if isinstance(r, (int, float)) else None,
        "f1": f1 * 100 if isinstance(f1, (int, float)) else None,
        "tp": obj.get("tp", 0),
        "fp": obj.get("fp", 0),
        "fn": obj.get("fn", 0),
    }


def _agg_top3_from_trace(trace_json: Path, trace_csv: Path) -> float | None:
    """Compute AggregatedTop3 as defined in paper Section 4.1.

    s(tg, tp) = 1 if hard_match=1
              = mean of the three highest non-hard similarity scores otherwise

    Averaged over EVERY candidate pair in the alignment trace (selected and
    rejected), not only the threshold-passing ones. This reports the overall
    alignment landscape rather than the confidence of the final 1-to-1 selection.
    """
    # Prefer JSON (richer, explicit agg_score field per candidate)
    if trace_json.exists():
        try:
            data = _load_json(trace_json)
            if isinstance(data, list) and data:
                scores = []
                for entry in data:
                    if not isinstance(entry, dict):
                        continue
                    v = entry.get("agg_score")
                    if isinstance(v, (int, float)):
                        scores.append(float(v))
                if scores:
                    return sum(scores) / len(scores)
        except (OSError, json.JSONDecodeError):
            pass

    # Fallback: CSV
    if trace_csv.exists():
        try:
            scores = []
            with open(trace_csv, "r", encoding="utf-8", newline="") as f:
                for row in csv.DictReader(f):
                    s = row.get("agg_score") or row.get("Score")
                    if s is None:
                        continue
                    try:
                        scores.append(float(s))
                    except ValueError:
                        pass
            if scores:
                return sum(scores) / len(scores)
        except OSError:
            pass
    return None


# ─────────────────────────────────────────────────────────────────
# CQ2Onto extractors (one (mode, model, dataset))
# ─────────────────────────────────────────────────────────────────

def _onto_class(dataset_dir: Path) -> dict | None:
    """Aggregated class P/R/F1 + per-method.

    NEW: if the JSON has an `aggregated_overall` entry (written by the
    patched eval_concept.py), use it directly. Otherwise fall back to
    counting rows in class_best_matching.csv against class_counts.
    """
    csv_path = dataset_dir / "01_class" / "class_best_matching.csv"
    json_path = dataset_dir / "01_class" / "class_result.json"
    if not json_path.exists():
        return None
    data = _load_json(json_path)
    if not data:
        return None

    # MOD: try aggregated_overall first
    agg_item = None
    for item in data.get("results", []):
        if isinstance(item, dict) and item.get("id") == "aggregated_overall":
            agg_item = item
            break

    if agg_item is not None:
        tp = int(agg_item.get("tp", 0))
        fp = int(agg_item.get("fp", 0))
        fn = int(agg_item.get("fn", 0))
        result = {"aggregated": _prf1(tp, fp, fn)}
    else:
        # FALLBACK: legacy CSV+counts path
        if not csv_path.exists():
            return None
        counts = data.get("config", {}).get("class_counts", {})
        try:
            gold = int(counts.get("gold_class_count", 0))
            pred = int(counts.get("pred_class_count", 0))
            with open(csv_path, "r", encoding="utf-8", newline="") as f:
                tp = sum(1 for _ in csv.DictReader(f))
        except (OSError, ValueError):
            return None
        result = {"aggregated": _prf1(tp, fp=pred - tp, fn=gold - tp)}

    # MOD: agg_top3 is the paper's AggregatedTop3 averaged over ALL candidate
    # pairs in the alignment trace (selected + rejected). This reflects the
    # overall alignment landscape, not just confidence of accepted pairs.
    trace_json = dataset_dir / "01_class" / "class_alignment_trace.json"
    trace_csv = dataset_dir / "01_class" / "class_alignment_trace.csv"
    a3 = _agg_top3_from_trace(trace_json, trace_csv)
    if a3 is not None:
        result["agg_top3"] = a3

    # Per-method (unchanged)
    method_map = {"semantic_embeddinggemma": "semantic"}
    per_method: dict = {}
    for item in data.get("results", []):
        if not isinstance(item, dict):
            continue
        mid = item.get("id", "")
        canonical = method_map.get(mid, mid)
        if canonical in METHODS:
            per_method[canonical] = _from_prf1(item)
    result["per_method"] = per_method
    return result


def _onto_property(dataset_dir: Path) -> dict | None:
    """Aggregated property P/R/F1 + per-method (overall across object/datatype).

    NEW: prefer aggregated_overall from JSON if the patched eval_property
    wrote it; fall back to CSV row count + summary counts otherwise.
    """
    csv_path = dataset_dir / "02_property" / "property_best_matching.csv"
    json_path = dataset_dir / "02_property" / "property_result.json"
    if not json_path.exists():
        return None
    data = _load_json(json_path)
    if not data:
        return None

    # MOD: try aggregated_overall first
    agg_item = None
    for item in data.get("results", []):
        if isinstance(item, dict) and item.get("id") == "aggregated_overall":
            agg_item = item
            break

    if agg_item is not None:
        tp = int(agg_item.get("tp", 0))
        fp = int(agg_item.get("fp", 0))
        fn = int(agg_item.get("fn", 0))
        result = {"aggregated": _prf1(tp, fp, fn)}
    else:
        # FALLBACK: legacy CSV+summary path
        if not csv_path.exists():
            return None
        summary = data.get("config", {}).get("summary", {})
        gold = summary.get("n_gold")
        pred = summary.get("n_pred")
        if gold is None or pred is None:
            return None
        try:
            with open(csv_path, "r", encoding="utf-8", newline="") as f:
                tp = sum(1 for _ in csv.DictReader(f))
        except OSError:
            return None
        result = {"aggregated": _prf1(tp, fp=int(pred) - tp, fn=int(gold) - tp)}

    # MOD: agg_top3 is the paper's AggregatedTop3 averaged over ALL candidate
    # pairs in the alignment trace (selected + rejected). This reflects the
    # overall alignment landscape, not just confidence of accepted pairs.
    trace_json = dataset_dir / "02_property" / "property_alignment_trace.json"
    trace_csv = dataset_dir / "02_property" / "property_alignment_trace.csv"
    a3 = _agg_top3_from_trace(trace_json, trace_csv)
    if a3 is not None:
        result["agg_top3"] = a3

    # Per-method: aggregate object+datatype TP/FP/FN per method
    per_method: dict = {}
    for item in data.get("results", []):
        if not isinstance(item, dict) or item.get("id") != "label_matching":
            continue
        for method in METHODS:
            tp_m = fp_m = fn_m = 0
            present = False
            for ptype in ("ObjectProperty", "DatatypeProperty", "AnnotationProperty"):
                block = item.get(ptype, {})
                if not isinstance(block, dict):
                    continue
                pm = block.get("metrics_per_method", {})
                if method in pm:
                    present = True
                    m = pm[method]
                    tp_m += m.get("tp", 0)
                    fp_m += m.get("fp", 0)
                    fn_m += m.get("fn", 0)
            if present:
                per_method[method] = _prf1(tp_m, fp_m, fn_m)
        break
    result["per_method"] = per_method
    return result


def _onto_property_chars(dataset_dir: Path) -> dict | None:
    """Property characteristics: AC + G P/R/F1."""
    json_path = dataset_dir / "02_property" / "property_result.json"
    if not json_path.exists():
        return None
    data = _load_json(json_path)
    if not data:
        return None
    ac = g = None
    for item in data.get("results", []):
        if isinstance(item, dict) and item.get("id") == "characteristics_check":
            ac = _from_prf1(item.get("overall"))
            g = _from_prf1(item.get("overall_ontology"))
            break
    if ac is None and g is None:
        return None
    return {"ac": ac, "g": g}


def _onto_triple(dataset_dir: Path) -> dict | None:
    """Triple: AC + G + cosine."""
    json_path = dataset_dir / "03_triple" / "triple_result.json"
    if not json_path.exists():
        return None
    data = _load_json(json_path)
    if not data:
        return None
    ac = g = cosine = None
    for item in data.get("results", []):
        if not isinstance(item, dict):
            continue
        if item.get("id") == "layer3_strict":
            ac = _from_prf1(item.get("grand_overall"))
        elif item.get("id") == "layer4_global":
            g = _from_prf1(item.get("grand_overall"))
        elif item.get("id") == "layer2_semantic":
            cosine = _from_prf1(item.get("overall"))
    if ac is None and g is None and cosine is None:
        return None
    return {"ac": ac, "g": g, "cosine": cosine}


def _onto_axiom(dataset_dir: Path) -> dict | None:
    """Axiom: AC (layer3) + G (layer4) + CQ coverage."""
    json_path = dataset_dir / "04_axiom" / "eval_axioms_result.json"
    csv_path = dataset_dir / "04_axiom" / "strict_cq_coverage.csv"
    data = _load_json(json_path)
    if not data:
        return None

    ac = None
    g = None
    cosine = None
    results = data.get("results", {})

    if isinstance(results, dict):
        l3 = results.get("layer3", {}).get("counts_overall", {})
        if l3:
            tp = l3.get("tp", 0)
            mm = l3.get("mismatch", 0)
            ac = _prf1(tp, fp=l3.get("fp", 0) + mm, fn=l3.get("fn", 0) + mm)
        l4 = results.get("layer4", {}).get("grand", {})
        if l4:
            g = _from_prf1(l4)
        # Layer 2 cosine (only present if --no_layer2 was off)
        l2 = results.get("layer2", {}).get("overall")
        if l2:
            cosine = _from_prf1(l2)

    # CQ coverage from CSV
    cq = None
    if csv_path.exists():
        try:
            n = n_any = n_full = 0
            rate_sum = 0.0
            with open(csv_path, "r", encoding="utf-8", newline="") as f:
                for row in csv.DictReader(f):
                    n += 1
                    if row.get("covered", "").lower() == "true":
                        n_any += 1
                    if row.get("fully_covered", "").lower() == "true":
                        n_full += 1
                    try:
                        rate_sum += float(row.get("rate", "0") or 0)
                    except ValueError:
                        pass
            if n > 0:
                cq = {
                    "any": 100 * n_any / n,
                    "mean": 100 * rate_sum / n,
                    "full": 100 * n_full / n,
                }
        except OSError:
            pass

    if ac is None and g is None and cq is None and cosine is None:
        return None
    return {"ac": ac, "g": g, "cosine": cosine, "cq": cq}


def _onto_hierarchy(dataset_dir: Path) -> dict | None:
    """Hierarchy closure: G F1 + closure-rescued CQ coverage."""
    json_path = dataset_dir / "05_hierarchy" / "hierarchy_result.json"
    if not json_path.exists():
        return None
    data = _load_json(json_path)
    if not data:
        return None

    g = None
    cq = None
    for item in data.get("results", []):
        if not isinstance(item, dict):
            continue
        if item.get("id") == "combined_metrics":
            g = _from_prf1(item)
        elif item.get("id") == "cq_coverage_closure":
            cq = {
                "any": 100 * float(item.get("any_coverage", 0) or 0),
                "mean": 100 * float(item.get("average_rate", 0) or 0),
                "full": 100 * float(item.get("fully_coverage", 0) or 0),
            }
    if g is None and cq is None:
        return None
    return {"g": g, "cq": cq}


# ─────────────────────────────────────────────────────────────────
# Config extraction (CQ2Onto)
# ─────────────────────────────────────────────────────────────────

LAYER_FILES = [
    ("concept",   "01_class/class_result.json"),
    ("property",  "02_property/property_result.json"),
    ("triple",    "03_triple/triple_result.json"),
    ("axiom",     "04_axiom/eval_axioms_result.json"),
    ("hierarchy", "05_hierarchy/hierarchy_result.json"),
]


def _onto_config(dataset_dir: Path) -> dict | None:
    """Merge cli_args from all CQ2Onto layer JSONs (prefix keys by layer).

    Only metric-affecting parameters are kept. Path arguments and output
    sink flags differ run-to-run and would prevent identical-setting runs
    from grouping together.
    """
    # Whitelist of cli arg names that actually affect the metric values.
    # Anything not in this set is dropped from the grouping key.
    GROUPING_KEYS = {
        "final_threshold", "top_n",
        "hard_threshold", "lexical_threshold", "semantic_threshold",
        "threshold", "literal_relax", "no_layer2",
        "model_id", "methods",
        "reasoner",
    }
    cfg: dict = {}
    has_any = False
    for layer, fname in LAYER_FILES:
        data = _load_json(dataset_dir / fname)
        if not data:
            continue
        cli_args = data.get("config", {}).get("cli_args")
        if cli_args:
            has_any = True
            for k, v in cli_args.items():
                if k not in GROUPING_KEYS:
                    continue
                cfg[f"{layer}.{k}"] = v
        else:
            # Legacy fallback: axiom JSON may have layer2_threshold/skipped
            if layer == "axiom":
                old = data.get("config", {})
                if "layer2_threshold" in old:
                    cfg["axiom.threshold"] = old["layer2_threshold"]
                if "layer2_skipped" in old:
                    cfg["axiom.no_layer2"] = old["layer2_skipped"]
                if cfg:
                    has_any = True
    return cfg if has_any else None


# ─────────────────────────────────────────────────────────────────
# CQ2Term extractor (one (model, dataset))
# ─────────────────────────────────────────────────────────────────

def _term_run(dataset_dir: Path) -> dict | None:
    """Extract CQ2Term metrics: aggregated class/property F1, per-method, CQ coverage."""
    json_path = dataset_dir / "06_cq_terms" / "eval_cq_terms_result.json"
    cq_csv = dataset_dir / "06_cq_terms" / "cq_coverage.csv"
    if not json_path.exists():
        return None
    data = _load_json(json_path)
    if not data:
        return None

    metrics = data.get("results", {}).get("metrics_overall", {})
    cls = _from_prf1(metrics.get("class_only"))
    prop = _from_prf1(metrics.get("property_only"))
    combined = _from_prf1(metrics.get("combined"))

    # Per-method: scan results list — CQ2Term may also have per-method blocks
    per_method_class: dict = {}
    per_method_prop: dict = {}
    results = data.get("results", {})
    # MOD: read per-method P/R/F1 blocks written by the patched eval_cq_terms.
    # Each block is {method_name: {coverage, precision, recall, f1, n_matched,
    # n_gold, n_pred}}. _from_prf1 turns these into the leaderboard's standard
    # {p, r, f1, tp, fp, fn} shape — but per-method here doesn't carry
    # tp/fp/fn, so tp/fp/fn default to 0 in those cells.
    for src_key, dest_dict in (("per_method_class", per_method_class),
                               ("per_method_property", per_method_prop)):
        block = results.get(src_key)
        if not isinstance(block, dict):
            continue
        for method_name, m in block.items():
            if not isinstance(m, dict):
                continue
            if method_name in METHODS:
                dest_dict[method_name] = _from_prf1(m)

    # CQ coverage from cq_coverage.csv
    cq = None
    if cq_csv.exists():
        try:
            n = n_any = n_full = 0
            cov_sum = 0.0
            with open(cq_csv, "r", encoding="utf-8", newline="") as f:
                for row in csv.DictReader(f):
                    n += 1
                    try:
                        c = float(row.get("coverage", "0") or 0)
                    except ValueError:
                        c = 0.0
                    cov_sum += c
                    if c > 0:
                        n_any += 1
                    if c >= 1.0:
                        n_full += 1
            if n > 0:
                cq = {
                    "any": 100 * n_any / n,
                    "mean": 100 * cov_sum / n,
                    "full": 100 * n_full / n,
                }
        except OSError:
            pass

    # MOD: AggregatedTop3 from CQ2Term trace files. Same definition as CQ2Onto
    # (paper Section 4.1). Computed across ALL candidate pairs in the trace,
    # not just selected ones. Reports overall alignment landscape.
    # The HTML's CQ2Term column config expects FLAT fields on term_recovery:
    #   run.term_recovery.agg_top3_class
    #   run.term_recovery.agg_top3_property
    # (Different from CQ2Onto which nests them under .class.agg_top3 and
    # .property.agg_top3.) So we expose both names.
    trace_dir = dataset_dir / "06_cq_terms"
    class_a3 = _agg_top3_from_trace(
        trace_dir / "cqterm_class_trace.json",
        trace_dir / "cqterm_class_trace.csv",
    )
    prop_a3 = _agg_top3_from_trace(
        trace_dir / "cqterm_prop_trace.json",
        trace_dir / "cqterm_prop_trace.csv",
    )

    return {
        "class": cls,
        "property": prop,
        "combined": combined,
        "cq": cq,
        "per_method_class": per_method_class,
        "per_method_property": per_method_prop,
        "agg_top3_class":    class_a3,
        "agg_top3_property": prop_a3,
    }


def _term_config(dataset_dir: Path) -> dict | None:
    """CQ2Term config from eval_cq_terms_result.json."""
    json_path = dataset_dir / "06_cq_terms" / "eval_cq_terms_result.json"
    data = _load_json(json_path)
    if not data:
        return None
    cfg = data.get("config", {})
    cli_args = cfg.get("cli_args")
    if cli_args:
        return {f"cq_terms.{k}": v for k, v in cli_args.items()}
    # Legacy: pull a few known fields
    fallback = {}
    for k in ("methods", "top_n", "final_threshold", "semantic_model"):
        if k in cfg:
            fallback[f"cq_terms.{k}"] = cfg[k]
    return fallback or None


# ─────────────────────────────────────────────────────────────────
# Collection
# ─────────────────────────────────────────────────────────────────

def collect_onto(root: Path, assumed_config: dict | None) -> list[dict]:
    """Walk CQ2Onto results: <root>/<mode>/<model>/<dataset>/...

    Each run's grouping config comes from the cli_args block written by the
    patched eval_*.py scripts. Legacy runs that pre-date the patches should
    be migrated once with backfill_legacy_cli_args.py so they group with
    fresh runs that share the same parameters.

    --assume_config_onto is still honoured as a fallback override for runs
    that genuinely have no cli_args after backfill.
    """
    runs = []
    for csv_path in root.rglob("strict_cq_coverage.csv"):
        parts = csv_path.relative_to(root).parts
        if len(parts) < 5:
            continue
        mode, model, dataset = parts[0], parts[1], parts[2]
        ds_dir = csv_path.parent.parent

        cfg = _onto_config(ds_dir)
        if assumed_config:
            merged = dict(assumed_config)
            if cfg:
                merged.update({k: v for k, v in cfg.items() if v is not None})
            cfg = merged

        runs.append({
            "benchmark": "cq2onto",
            "mode": mode, "model": model, "dataset": dataset,
            "config": cfg,
            "term_recovery": {
                "class":    _onto_class(ds_dir),
                "property": _onto_property(ds_dir),
            },
            "property_chars": _onto_property_chars(ds_dir),
            "triple":         _onto_triple(ds_dir),
            "axiom":          _onto_axiom(ds_dir),
            "hierarchy":      _onto_hierarchy(ds_dir),
        })
    return runs


def collect_term(root: Path, assumed_config: dict | None) -> list[dict]:
    """Walk CQ2Term results: <root>/<model>/<dataset>/06_cq_terms/."""
    runs = []
    for json_path in root.rglob("eval_cq_terms_result.json"):
        parts = json_path.relative_to(root).parts
        if len(parts) < 4:
            continue
        model, dataset = parts[0], parts[1]
        ds_dir = json_path.parent.parent

        cfg = _term_config(ds_dir)
        if assumed_config:
            merged = dict(assumed_config)
            if cfg:
                merged.update({k: v for k, v in cfg.items() if v is not None})
            cfg = merged

        metrics = _term_run(ds_dir)
        if metrics:
            runs.append({
                "benchmark": "cq2term",
                "mode": None,
                "model": model,
                "dataset": dataset,
                "config": cfg,
                "term_recovery": metrics,
            })
    return runs


# ─────────────────────────────────────────────────────────────────
# Config grouping
# ─────────────────────────────────────────────────────────────────

def config_key(config: dict | None) -> tuple:
    if not config:
        return (("__unknown__", True),)
    # Convert list values to tuple, others kept as-is
    items = []
    for k, v in sorted(config.items()):
        if isinstance(v, list):
            v = tuple(v)
        elif isinstance(v, dict):
            v = tuple(sorted(v.items()))
        items.append((k, v))
    return tuple(items)


def config_label(config: dict | None) -> str:
    if not config:
        return "Unknown configuration"
    parts = []
    for k, v in sorted(config.items()):
        if isinstance(v, list):
            v = "[" + ",".join(str(x) for x in v) + "]"
        parts.append(f"{k}={v}")
    return ", ".join(parts)


# ─────────────────────────────────────────────────────────────────
# Output: JS data
# ─────────────────────────────────────────────────────────────────

def write_js(payload: dict, path: Path):
    js = "const LEADERBOARD_DATA = " + json.dumps(payload, indent=2) + ";\n"
    path.write_text(js, encoding="utf-8")


def _avg(vals):
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


def _fmt(v):
    return f"{v:.1f}%" if v is not None else "—"


def _agg_by_model(runs, getter):
    """Group runs by (mode, model), apply getter to each run, return list of
    (mode, model, value, n_datasets) sorted by value desc.
    Entries whose averaged value is None are dropped (no signal on this metric)."""
    from collections import defaultdict
    g = defaultdict(list)
    for r in runs:
        g[(r.get("mode"), r["model"])].append(r)
    out = []
    for (mode, model), recs in g.items():
        v = _avg([getter(r) for r in recs])
        if v is None:
            continue
        out.append((mode, model, v, len(recs)))
    out.sort(key=lambda x: -x[2])
    return out


def _markdown_table(rows, headers, top_n=10):
    """Render rows as a Markdown table."""
    L = []
    L.append("| " + " | ".join(headers) + " |")
    L.append("|" + "|".join(["---:" if i > 0 else "---" for i in range(len(headers))]) + "|")
    for r in rows[:top_n]:
        L.append("| " + " | ".join(r) + " |")
    return L


def write_markdown(payload: dict, path: Path):
    """Markdown leaderboard. Top-10 per task across all domains (Overall view)."""
    L = []
    L.append("# CQ4OE Leaderboard")
    L.append("")
    L.append("Top 10 ranking per task, macro-averaged across all six domains "
             "(Wine, AWO, ODRL, SAREF4WATR, VGO, SWO). Numbers are F1 percentages "
             "unless otherwise noted. For the full interactive leaderboard with "
             "per-domain tabs, sortable columns, expanded Precision and Recall, "
             "and per-method breakdowns, open `leaderboard.html`.")
    L.append("")
    cq2t_runs = payload.get("cq2term", {}).get("runs", [])
    cq2o_runs = payload.get("cq2onto", {}).get("runs", [])
    L.append(f"**Total runs.** CQ2Term {len(cq2t_runs)}, CQ2Onto {len(cq2o_runs)}.")
    L.append("")

    # ─── Glossary ───
    L.append("## Reading the tables")
    L.append("")
    L.append("Each task in CQ4OE is scored with one or more of the metrics below. "
             "Tables show F1 by default. The full Precision (P), Recall (R), F1 "
             "triple is available in the interactive HTML viewer.")
    L.append("")
    L.append("**Tasks.**")
    L.append("")
    L.append("- **CQ2Term.** Term-level task. Does the model produce the explicit "
             "classes and properties each Competency Question (CQ) requires?")
    L.append("- **CQ2Onto.** Ontology-level task. Does the generated ontology "
             "capture the terms, property semantics, domain and range relations, "
             "TBox axioms (the schema-level class and property axioms), and "
             "hierarchy entailments needed to answer each CQ?")
    L.append("")
    L.append("**Score columns.**")
    L.append("")
    L.append("- **Class F1, Property F1.** F1 over the predicted vocabulary, "
             "aggregated by a top-3 mean over five string and embedding similarity "
             "methods (hard match, sequence match, Levenshtein, Jaro-Winkler, "
             "semantic embedding).")
    L.append("- **F1-AC (Alignment-Conditioned).** Restricted to items whose "
             "named terms align with gold names. Isolates structural errors from "
             "vocabulary errors.")
    L.append("- **F1-G (Global).** Evaluated over the full gold and predicted "
             "sets so unaligned items count as errors.")
    L.append("- **Cosine.** Embedding-based diagnostic that compares triples by "
             "vector similarity instead of strict structural equality.")
    L.append("- **CQ-Mean, Axiom-Mean, Closure-Mean.** Average per-CQ recovery "
             "rate. For each CQ, how many of its required items did the model "
             "recover, averaged across all CQs.")
    L.append("- **Closure-Any.** Share of CQs with at least one required item "
             "recovered after the reasoner closure rescue.")
    L.append("")

    # ─── CQ2Term ───
    if cq2t_runs:
        L.append("## CQ2Term")
        L.append("")
        L.append("### Term Recovery")
        L.append("")
        L.append("_Ranked by CQ-Mean over 99 CQs._")
        L.append("")
        # Composite getter: pick CQ-mean for ranking
        def cq_mean(r):
            tr = r.get("term_recovery") or {}
            cq = tr.get("cq")
            return cq.get("mean") if cq else None
        rows = _agg_by_model(cq2t_runs, cq_mean)
        # For each top entry, also fetch class/property F1
        def cls_f1(r):
            tr = r.get("term_recovery") or {}
            c = tr.get("class")
            return c.get("f1") if c else None
        def prop_f1(r):
            tr = r.get("term_recovery") or {}
            p = tr.get("property")
            return p.get("f1") if p else None
        # Build table rows: per (mode, model) recompute class/prop avgs
        from collections import defaultdict
        by_mm = defaultdict(list)
        for r in cq2t_runs:
            by_mm[(r.get("mode"), r["model"])].append(r)
        table_rows = []
        for rank, (mode, model, cqm, n) in enumerate(rows, 1):
            recs = by_mm[(mode, model)]
            cf = _avg([cls_f1(r) for r in recs])
            pf = _avg([prop_f1(r) for r in recs])
            table_rows.append([str(rank), f"`{model}`", _fmt(cf), _fmt(pf), _fmt(cqm)])
        L.extend(_markdown_table(table_rows,
                                  ["Rank", "Model", "Class F1", "Property F1", "CQ-Mean"]))
        L.append("")

    # ─── CQ2Onto ───
    if cq2o_runs:
        L.append("## CQ2Onto")
        L.append("")

        def model_cell(mode, model):
            return f"`{mode}` / `{model}`"

        from collections import defaultdict
        by_mm = defaultdict(list)
        for r in cq2o_runs:
            by_mm[(r["mode"], r["model"])].append(r)

        # ── Term Recovery ──
        L.append("### Term Recovery")
        L.append("")
        L.append("_Recovery of the gold vocabulary across the full predicted "
                 "ontology. Ranked by Property F1._")
        L.append("")
        def cls_agg(r):
            tr = r.get("term_recovery") or {}
            c = tr.get("class") or {}
            ag = c.get("aggregated")
            return ag.get("f1") if ag else None
        def prop_agg(r):
            tr = r.get("term_recovery") or {}
            p = tr.get("property") or {}
            ag = p.get("aggregated")
            return ag.get("f1") if ag else None
        rows = _agg_by_model(cq2o_runs, prop_agg)
        table_rows = []
        for rank, (mode, model, pf, n) in enumerate(rows, 1):
            recs = by_mm[(mode, model)]
            cf = _avg([cls_agg(r) for r in recs])
            table_rows.append([str(rank), model_cell(mode, model), _fmt(cf), _fmt(pf)])
        L.extend(_markdown_table(table_rows,
                                  ["Rank", "Mode / Model", "Class F1", "Property F1"]))
        L.append("")

        # ── Property Characteristics ──
        L.append("### Property Characteristics")
        L.append("")
        L.append("_Recovery of OWL property flags (functional, inverse, "
                 "transitive, symmetric, reflexive). Ranked by F1-AC._")
        L.append("")
        def pc_ac(r):
            pc = r.get("property_chars") or {}
            ac = pc.get("ac")
            return ac.get("f1") if ac else None
        def pc_g(r):
            pc = r.get("property_chars") or {}
            g = pc.get("g")
            return g.get("f1") if g else None
        rows = _agg_by_model(cq2o_runs, pc_ac)
        table_rows = []
        for rank, (mode, model, ac, n) in enumerate(rows, 1):
            recs = by_mm[(mode, model)]
            g = _avg([pc_g(r) for r in recs])
            table_rows.append([str(rank), model_cell(mode, model), _fmt(ac), _fmt(g)])
        L.extend(_markdown_table(table_rows,
                                  ["Rank", "Mode / Model", "F1-AC", "F1-G"]))
        L.append("")

        # ── Triple ──
        L.append("### Triple (domain/range)")
        L.append("")
        L.append("_Recovery of (subject, predicate, object) triples derived "
                 "from the rdfs domain and rdfs range axioms of each property. "
                 "Ranked by F1-AC._")
        L.append("")
        def t_ac(r):
            t = r.get("triple") or {}
            ac = t.get("ac")
            return ac.get("f1") if ac else None
        def t_g(r):
            t = r.get("triple") or {}
            g = t.get("g")
            return g.get("f1") if g else None
        def t_cos(r):
            t = r.get("triple") or {}
            cos = t.get("cosine")
            return cos.get("f1") if cos else None
        rows = _agg_by_model(cq2o_runs, t_ac)
        table_rows = []
        for rank, (mode, model, ac, n) in enumerate(rows, 1):
            recs = by_mm[(mode, model)]
            g = _avg([t_g(r) for r in recs])
            c = _avg([t_cos(r) for r in recs])
            table_rows.append([str(rank), model_cell(mode, model), _fmt(ac), _fmt(g), _fmt(c)])
        L.extend(_markdown_table(table_rows,
                                  ["Rank", "Mode / Model", "F1-AC", "F1-G", "Cosine"]))
        L.append("")

        # ── Axioms ──
        L.append("### TBox Axioms")
        L.append("")
        L.append("_Recovery of TBox axioms by strict structural matching "
                 "after alignment translation. Ranked by Axiom-Mean, the per-CQ "
                 "strict axiom coverage rate._")
        L.append("")
        def a_ac(r):
            a = r.get("axiom") or {}
            ac = a.get("ac")
            return ac.get("f1") if ac else None
        def a_g(r):
            a = r.get("axiom") or {}
            g = a.get("g")
            return g.get("f1") if g else None
        def a_mean(r):
            a = r.get("axiom") or {}
            cq = a.get("cq")
            return cq.get("mean") if cq else None
        rows = _agg_by_model(cq2o_runs, a_mean)
        table_rows = []
        for rank, (mode, model, am, n) in enumerate(rows, 1):
            recs = by_mm[(mode, model)]
            ac = _avg([a_ac(r) for r in recs])
            g = _avg([a_g(r) for r in recs])
            table_rows.append([str(rank), model_cell(mode, model), _fmt(ac), _fmt(g), _fmt(am)])
        L.extend(_markdown_table(table_rows,
                                  ["Rank", "Mode / Model", "F1-AC", "F1-G", "Axiom-Mean"]))
        L.append("")

        # ── Hierarchy Closure ──
        L.append("### Hierarchy Closure")
        L.append("")
        L.append("_Recovery of inferred subClassOf and subPropertyOf "
                 "entailments using the HermiT reasoner. Ranked by Closure-Mean._")
        L.append("")
        def h_g(r):
            h = r.get("hierarchy") or {}
            g = h.get("g")
            return g.get("f1") if g else None
        def h_mean(r):
            h = r.get("hierarchy") or {}
            cq = h.get("cq")
            return cq.get("mean") if cq else None
        def h_any(r):
            h = r.get("hierarchy") or {}
            cq = h.get("cq")
            return cq.get("any") if cq else None
        rows = _agg_by_model(cq2o_runs, h_mean)
        table_rows = []
        for rank, (mode, model, hm, n) in enumerate(rows, 1):
            recs = by_mm[(mode, model)]
            g = _avg([h_g(r) for r in recs])
            a = _avg([h_any(r) for r in recs])
            table_rows.append([str(rank), model_cell(mode, model),
                              _fmt(g), _fmt(a), _fmt(hm)])
        L.extend(_markdown_table(table_rows,
                                  ["Rank", "Mode / Model", "F1-G", "Closure-Any", "Closure-Mean"]))
        L.append("")

    # ─── Configuration footer ───
    L.append("---")
    L.append("")
    L.append("**Configuration groups.** Runs that differ in any CLI argument "
             "appear in separate groups and are ranked independently. The "
             "tables above merge runs from all configuration groups for "
             "brevity. Open `leaderboard.html` to see per-config rankings.")
    L.append("")
    cfgs = set()
    for r in cq2t_runs + cq2o_runs:
        cfgs.add(config_label(r["config"]))
    for c in sorted(cfgs):
        L.append(f"- `{c}`")
    L.append("")

    path.write_text("\n".join(L), encoding="utf-8")


# ─────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────

def parse_assume_config(s: str) -> dict:
    """Parse --assume_config_onto.

    Bare keys (e.g. "threshold=0.6") expand to all layers that actually accept
    that flag, mirroring how the patched eval scripts write `cli_args` into
    each layer's JSON. This lets legacy runs and freshly-evaluated runs land
    in the same configuration group when their parameters truly match.

    Layer-prefixed keys (e.g. "axiom.threshold=0.6") are passed through
    unchanged so users can still override per-layer settings explicitly.
    """
    # Which layers consume each bare flag, based on the eval scripts'
    # argparse definitions and the runner (run_all_evaluation_agent_datasets.py).
    BARE_KEY_LAYERS = {
        "literal_relax": ("triple", "axiom"),
        "threshold":     ("triple", "axiom"),
        "no_layer2":     ("axiom",),
    }

    def _coerce(v: str):
        v = v.strip()
        if v.lower() in ("true", "false"):
            return v.lower() == "true"
        try: return int(v)
        except ValueError: pass
        try: return float(v)
        except ValueError: pass
        return v

    out: dict = {}
    for piece in s.split(","):
        piece = piece.strip()
        if not piece or "=" not in piece:
            continue
        k, v = piece.split("=", 1)
        k = k.strip()
        coerced = _coerce(v)

        if "." in k:
            # already layer-prefixed: leave alone
            out[k] = coerced
            continue

        # bare key: fan out to all layers that consume it
        if k in BARE_KEY_LAYERS:
            for layer in BARE_KEY_LAYERS[k]:
                out[f"{layer}.{k}"] = coerced
        else:
            # unknown bare key: keep as-is so grouping is at least stable
            out[k] = coerced

    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cq2term_root", default="CQ2Term/03_evaluation_results")
    p.add_argument("--cq2onto_root", default="CQ2Onto/03_evaluation_results")
    p.add_argument("--html_data",    default="leaderboard_data.js")
    p.add_argument("--markdown_out", default="leaderboard.md")
    p.add_argument("--assume_config_onto", default=None,
                   help="Comma-separated k=v for legacy CQ2Onto runs (CLI args missing). "
                        "Keys are prefixed automatically.")
    p.add_argument("--assume_config_term", default=None,
                   help="Same for CQ2Term legacy runs.")
    args = p.parse_args()

    onto_root = Path(args.cq2onto_root)
    term_root = Path(args.cq2term_root)

    assumed_onto = parse_assume_config(args.assume_config_onto) if args.assume_config_onto else None
    assumed_term = parse_assume_config(args.assume_config_term) if args.assume_config_term else None

    onto_runs = collect_onto(onto_root, assumed_onto) if onto_root.exists() else []
    term_runs = collect_term(term_root, assumed_term) if term_root.exists() else []

    print(f"[build_leaderboard] CQ2Term runs: {len(term_runs)}")
    print(f"[build_leaderboard] CQ2Onto runs: {len(onto_runs)}")

    # Build per-benchmark payload, grouping by config
    def _group(runs):
        groups = {}
        for r in runs:
            key = config_key(r["config"])
            g = groups.setdefault(key, {
                "label": config_label(r["config"]),
                "config": dict(key) if key != (("__unknown__", True),) else None,
                "runs": [],
            })
            g["runs"].append(r)
        # Sort: larger groups first
        return sorted(groups.values(), key=lambda g: (-len(g["runs"]), g["label"]))

    payload = {
        "cq2term": {
            "groups":   _group(term_runs),
            "datasets": order_datasets({r["dataset"] for r in term_runs}),
            "models":   sorted({r["model"] for r in term_runs}),
            "runs":     term_runs,
        },
        "cq2onto": {
            "groups":   _group(onto_runs),
            "datasets": order_datasets({r["dataset"] for r in onto_runs}),
            "modes":    sorted({r["mode"] for r in onto_runs if r["mode"]}),
            "models":   sorted({r["model"] for r in onto_runs}),
            "runs":     onto_runs,
        },
        "methods": METHODS,
    }

    write_js(payload, Path(args.html_data))
    print(f"[build_leaderboard] Wrote: {args.html_data}")
    write_markdown(payload, Path(args.markdown_out))
    print(f"[build_leaderboard] Wrote: {args.markdown_out}")


if __name__ == "__main__":
    main()
