from __future__ import annotations

import argparse
import csv
import difflib
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Optional

import Levenshtein
import textdistance
from langchain_ollama import OllamaEmbeddings
from rdflib import Graph, Literal, OWL, RDF, RDFS
from rdflib.term import BNode
from sentence_transformers import util
from eva_char_in_property import eval_characteristics


SEMANTIC_THRESHOLD = 0.6
LEXICAL_THRESHOLD = 0.8
HARD_THRESHOLD = 1.0

METHOD_THRESHOLDS: dict[str, float] = {
    "hard_match": HARD_THRESHOLD,
    "sequence_match": LEXICAL_THRESHOLD,
    "levenshtein": LEXICAL_THRESHOLD,
    "jaro_winkler": LEXICAL_THRESHOLD,
    "semantic": SEMANTIC_THRESHOLD,
}


CHAR_URIS = {
    "Functional": OWL.FunctionalProperty,
    "InverseFunctional": OWL.InverseFunctionalProperty,
    "Transitive": OWL.TransitiveProperty,
    "Symmetric": OWL.SymmetricProperty,
    "Asymmetric": OWL.AsymmetricProperty,
    "Reflexive": OWL.ReflexiveProperty,
    "Irreflexive": OWL.IrreflexiveProperty,
}

_RDFLIB_FORMATS = [
    ("xml", {".owl", ".rdf", ".xml"}),
    ("turtle", {".ttl", ".turtle"}),
    ("nt", {".nt"}),
    ("n3", {".n3"}),
    ("json-ld", {".jsonld", ".json"}),
    ("trig", {".trig"}),
]

ALL_PROP_TYPES = ["ObjectProperty", "DatatypeProperty", "AnnotationProperty"]


def split_camel_case(text: str) -> str:
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    text = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", text)
    return text


def normalize_key(text: str) -> str:
    t = str(text or "").strip()
    t = split_camel_case(t)
    t = t.lower()
    t = t.replace("_", " ").replace("-", " ")
    t = re.sub(r"[^\w\s]", "", t)
    t = re.sub(r"\s+", "", t)
    return t


def normalize_text(text: str) -> str:
    t = str(text or "").strip()
    t = split_camel_case(t)
    t = t.replace("_", " ").replace("-", " ")
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.lower().strip()


def check_normalized_duplicates(raw_terms: list[str], name: str, mode: str) -> None:
    if mode == "key":
        normalized = [normalize_key(x) for x in raw_terms]
    elif mode == "text":
        normalized = [normalize_text(x) for x in raw_terms]
    else:
        raise ValueError("mode must be 'key' or 'text'")

    counts = Counter(normalized)
    duplicated = {k: v for k, v in counts.items() if v > 1 and k}

    if duplicated:
        print(f"\n[WARNING] duplicated normalized {name} by normalize_{mode}:")
        for k, v in duplicated.items():
            print(f"  {k}: {v}")


def _label_from_uri(uri_str: str) -> str:
    frag = uri_str.split("#")[-1] if "#" in uri_str else uri_str.rstrip("/").split("/")[-1]
    return frag.strip()


def _get_label(node, g: Graph) -> str:
    if node is None or isinstance(node, BNode):
        return ""
    labels = list(g.objects(node, RDFS.label))
    for lb in labels:
        if isinstance(lb, Literal) and getattr(lb, "language", None) == "en":
            return str(lb).strip()
    for lb in labels:
        if isinstance(lb, Literal) and getattr(lb, "language", None) in (None, ""):
            return str(lb).strip()
    for lb in labels:
        if isinstance(lb, Literal):
            return str(lb).strip()
    iri_local = _label_from_uri(str(node))
    if iri_local:
        return iri_local
    return ""


def _norm(text):
    if text is None:
        return ""
    return str(text).strip().lower()


def _node_label(node, g: Graph) -> Optional[str]:
    if node is None or isinstance(node, BNode):
        return None
    label = _get_label(node, g)
    return label if label else None


def _parse_graph(file_path: str) -> Graph:
    ext = os.path.splitext(file_path)[1].lower()
    ordered = sorted(_RDFLIB_FORMATS, key=lambda x: 0 if ext in x[1] else 1)
    last_err = None
    for fmt, _ in ordered:
        try:
            g = Graph()
            g.parse(file_path, format=fmt)
            print(f"  Parsed '{file_path}' with format='{fmt}'")
            return g
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Cannot parse '{file_path}': {last_err}")

def _compute_lexical_sim_from_normalized(a_norm: str, b_norm: str, method: str) -> float:
    if method == "hard_match":
        return 1.0 if a_norm == b_norm else 0.0
    if method == "sequence_match":
        return difflib.SequenceMatcher(None, a_norm, b_norm).ratio()
    if method == "levenshtein":
        dist = Levenshtein.distance(a_norm, b_norm)
        return 1 - dist / max(len(a_norm), len(b_norm), 1)
    if method == "jaro_winkler":
        return textdistance.jaro_winkler.normalized_similarity(a_norm, b_norm)
    return 0.0


@dataclass
class PropertyRecord:
    uri: str
    label: str
    prop_type: str
    domain: Optional[str]
    range: Optional[str]
    characteristics: list[str] = field(default_factory=list)
    sub_properties: list[str] = field(default_factory=list)
    super_properties: list[str] = field(default_factory=list)


@dataclass
class NameRecord:
    id: int
    raw: str
    key: str
    text: str


def _build_name_records(labels: list[str]) -> list[NameRecord]:
    records: list[NameRecord] = []
    for i, label in enumerate(labels):
        records.append(NameRecord(
            id=i,
            raw=label,
            key=normalize_key(label),
            text=normalize_text(label),
        ))
    return records

def parse_properties(file_path: str) -> list[PropertyRecord]:
    g = _parse_graph(file_path)
    records: list[PropertyRecord] = []
    seen: set[str] = set()

    type_map = {
        OWL.ObjectProperty: "ObjectProperty",
        OWL.DatatypeProperty: "DatatypeProperty",
        OWL.AnnotationProperty: "AnnotationProperty",
    }

    for owl_type, type_name in type_map.items():
        for prop_uri in g.subjects(RDF.type, owl_type):
            if isinstance(prop_uri, BNode) or str(prop_uri) in seen:
                continue
            seen.add(str(prop_uri))

            label = _get_label(prop_uri, g)
            doms = list(g.objects(prop_uri, RDFS.domain))
            rngs = list(g.objects(prop_uri, RDFS.range))

            domain = _node_label(doms[0], g) if doms else None
            range_ = _node_label(rngs[0], g) if rngs else None

            chars = [n for n, u in CHAR_URIS.items() if (prop_uri, RDF.type, u) in g]

            sub_p = [
                _get_label(s, g)
                for s in g.subjects(RDFS.subPropertyOf, prop_uri)
                if not isinstance(s, BNode)
            ]
            sup_p = [
                _get_label(s, g)
                for s in g.objects(prop_uri, RDFS.subPropertyOf)
                if not isinstance(s, BNode)
            ]

            records.append(PropertyRecord(
                uri=str(prop_uri),
                label=label,
                prop_type=type_name,
                domain=domain,
                range=range_,
                characteristics=chars,
                sub_properties=[s for s in sub_p if s],
                super_properties=[s for s in sup_p if s],
            ))

    print(f"  -> {len(records)} properties total")
    return records


def _group_by_type(props: list[PropertyRecord]) -> dict[str, list[PropertyRecord]]:
    groups: dict[str, list[PropertyRecord]] = {t: [] for t in ALL_PROP_TYPES}
    for p in props:
        if p.prop_type in groups:
            groups[p.prop_type].append(p)
    return groups

def eval_type_distribution(
    gold_props: list[PropertyRecord],
    pred_props: list[PropertyRecord],
) -> dict:
    gold_dist = Counter(p.prop_type for p in gold_props)
    pred_dist = Counter(p.prop_type for p in pred_props)
    all_types = sorted(set(gold_dist) | set(pred_dist))

    distribution = {}
    print(f"\n  {'Type':<25s}  {'Gold':>6}  {'Pred':>6}  {'Diff':>6}  Note")
    print("  " + "-" * 62)

    for t in all_types:
        g_count = gold_dist.get(t, 0)
        p_count = pred_dist.get(t, 0)
        diff = p_count - g_count

        if diff == 0:
            note = "exact"
        elif diff > 0:
            note = f"pred has {diff} extra"
        else:
            note = f"pred missing {abs(diff)}"

        distribution[t] = {
            "gold_count": g_count,
            "pred_count": p_count,
            "diff": diff,
            "note": note,
        }
        print(f"  {t:<25s}  {g_count:>6}  {p_count:>6}  {diff:>+6}  {note}")

    return distribution


def _match_one_to_one_greedy(
    gold_records: list[NameRecord],
    pred_records: list[NameRecord],
    sim_func,
    threshold: float,
) -> tuple[dict[int, tuple[int, float]], dict[int, tuple[int, float]]]:
    candidates: list[tuple[float, int, int]] = []
    for g in gold_records:
        for p in pred_records:
            score = sim_func(g, p)
            if score >= threshold:
                candidates.append((score, g.id, p.id))
    candidates.sort(key=lambda x: x[0], reverse=True)

    used_gold: set[int] = set()
    used_pred: set[int] = set()
    gold_match: dict[int, tuple[int, float]] = {}
    pred_match: dict[int, tuple[int, float]] = {}

    for score, gold_id, pred_id in candidates:
        if gold_id in used_gold or pred_id in used_pred:
            continue
        gold_match[gold_id] = (pred_id, score)
        pred_match[pred_id] = (gold_id, score)
        used_gold.add(gold_id)
        used_pred.add(pred_id)

    return gold_match, pred_match


def _zero_metrics() -> dict:
    return {"coverage": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0,
            "gold_covered": 0, "pred_supported": 0}


def _calc_metrics(tp_g: int, tp_p: int, n_gold: int, n_pred: int) -> dict:
    precision = tp_p / n_pred if n_pred else 0.0
    recall = tp_g / n_gold if n_gold else 0.0
    coverage = recall
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "coverage": round(coverage, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "gold_covered": tp_g,
        "pred_supported": tp_p,
    }


def _match_one_method_standalone(
    gold_records: list[NameRecord],
    pred_records: list[NameRecord],
    method: str,
    model_id: Optional[str],
) -> dict:

    thr = METHOD_THRESHOLDS.get(method, LEXICAL_THRESHOLD)
    if not gold_records or not pred_records:
        return _zero_metrics()

    if method == "semantic":
        if not model_id:
            raise ValueError("semantic matching requires --model_id")
        encoder = OllamaEmbeddings(model=model_id)
        gold_texts = [g.text for g in gold_records]
        pred_texts = [p.text for p in pred_records]
        embeds = encoder.embed_documents(gold_texts + pred_texts)
        g_emb = embeds[:len(gold_records)]
        p_emb = embeds[len(gold_records):]
        sim_matrix = [
            [float(util.cos_sim(g_emb[i], p_emb[j]).item())
             for j in range(len(pred_records))]
            for i in range(len(gold_records))
        ]
        def sim_func(g, p):
            return sim_matrix[g.id][p.id]
    else:
        def sim_func(g, p):
            return _compute_lexical_sim_from_normalized(g.key, p.key, method)

    gold_match, pred_match = _match_one_to_one_greedy(
        gold_records, pred_records, sim_func, thr,
    )
    return _calc_metrics(
        tp_g=len(gold_match), tp_p=len(pred_match),
        n_gold=len(gold_records), n_pred=len(pred_records),
    )


def _compute_full_score_table(
    gold_records: list[NameRecord],
    pred_records: list[NameRecord],
    method: str,
    model_id: Optional[str],
) -> list[dict]:

    if not gold_records or not pred_records:
        return []

    if method == "semantic":
        if not model_id:
            raise ValueError("semantic matching requires --model_id")
        encoder = OllamaEmbeddings(model=model_id)
        gold_texts = [g.text for g in gold_records]
        pred_texts = [p.text for p in pred_records]
        embeds = encoder.embed_documents(gold_texts + pred_texts)
        g_emb = embeds[:len(gold_records)]
        p_emb = embeds[len(gold_records):]
        sim_matrix = [
            [float(util.cos_sim(g_emb[i], p_emb[j]).item())
             for j in range(len(pred_records))]
            for i in range(len(gold_records))
        ]
        def sim_func(g, p):
            return sim_matrix[g.id][p.id]
    else:
        def sim_func(g, p):
            return _compute_lexical_sim_from_normalized(g.key, p.key, method)

    out = []
    for g in gold_records:
        for p in pred_records:
            out.append({
                "gold_term": g.raw,
                "pred_term": p.raw,
                "method": method,
                "score": float(sim_func(g, p)),
            })
    return out


def _build_best_prop_map_top_n(
    all_score_tables: dict[str, list[dict]],
    top_n: int = 3,
    final_threshold: float = 0.0,
    return_trace: bool = False,
) -> dict:

    pair_scores = defaultdict(dict)
    hard_match_pairs = set()

    for method, table in all_score_tables.items():
        for entry in table:
            g = entry["gold_term"]
            p = entry["pred_term"]
            score = entry["score"]
            if method == "hard_match":
                if score >= 0.999:
                    hard_match_pairs.add((g, p))
                    pair_scores[(g, p)][method] = 1.0
            else:
                pair_scores[(g, p)][method] = score

    aggregated = []
    for (g, p), scores in pair_scores.items():
        is_hard = (g, p) in hard_match_pairs
        if is_hard:
            agg = 1.0
            label = "hard_match"
            top_methods = ["hard_match"]
        else:
            non_hard = {m: s for m, s in scores.items() if m != "hard_match"}
            if not non_hard:
                continue
            sorted_items = sorted(non_hard.items(),
                                  key=lambda kv: kv[1], reverse=True)
            top_items = sorted_items[:top_n]
            top_methods = [m for m, s in top_items]
            agg = sum(s for _, s in top_items) / len(top_items)
            label = (f"top{len(top_items)}_avg("
                     f"{'+'.join(sorted(top_methods))})")

        aggregated.append({
            "gold": g, "pred": p,
            "agg_score": agg,
            "matching_way": label,
            "scores_by_method": dict(scores),
            "top_methods": top_methods,
            "is_hard_match": is_hard,
        })

    aggregated.sort(key=lambda c: (c["is_hard_match"], c["agg_score"]),
                    reverse=True)
    final_map = {}
    used_preds = set()
    selection_log = {}

    for c in aggregated:
        key = (c["gold"], c["pred"])
        if not c["is_hard_match"] and c["agg_score"] < final_threshold:
            selection_log[key] = {
                "selected": False,
                "reason": (f"top-{top_n} avg score {c['agg_score']:.4f} "
                           f"< final_threshold {final_threshold}"),
            }
            continue
        if c["gold"] in final_map:
            selection_log[key] = {
                "selected": False,
                "reason": (f"gold already mapped to "
                           f"'{final_map[c['gold']]['pred_term']}'"),
            }
            continue
        if c["pred"] in used_preds:
            stealer = next((g for g, info in final_map.items()
                            if info["pred_term"] == c["pred"]), None)
            selection_log[key] = {
                "selected": False,
                "reason": f"pred already taken by '{stealer}'",
            }
            continue
        final_map[c["gold"]] = {
            "gold_term": c["gold"],
            "pred_term": c["pred"],
            "matching_way": c["matching_way"],
            "score": c["agg_score"],
        }
        used_preds.add(c["pred"])
        selection_log[key] = {"selected": True, "reason": "selected"}

    if return_trace:
        trace = []
        for c in aggregated:
            key = (c["gold"], c["pred"])
            log = selection_log.get(key, {"selected": False,
                                          "reason": "(not seen)"})
            trace.append({
                "gold_term": c["gold"],
                "pred_term": c["pred"],
                "top_methods_used": "+".join(c["top_methods"]),
                "scores_by_method": "; ".join(
                    f"{m}={s:.4f}" for m, s in
                    sorted(c["scores_by_method"].items())),
                "is_hard_match": c["is_hard_match"],
                "agg_score": round(c["agg_score"], 4),
                "selected": log["selected"],
                "reason": log["reason"],
            })
        trace.sort(key=lambda t: (not t["selected"], -t["agg_score"]))
        return final_map, trace

    return final_map


def _eval_within_type(
    gold_group: list[PropertyRecord],
    pred_group: list[PropertyRecord],
    prop_type: str,
    methods: list[str],
    model_id: Optional[str],
    top_n: int,
    final_threshold: float,
) -> dict:
    gold_labels = sorted(set(p.label for p in gold_group if p.label))
    pred_labels = sorted(set(p.label for p in pred_group if p.label))

    check_normalized_duplicates(gold_labels, f"gold {prop_type} labels", "key")
    check_normalized_duplicates(pred_labels, f"pred {prop_type} labels", "key")
    check_normalized_duplicates(gold_labels, f"gold {prop_type} labels", "text")
    check_normalized_duplicates(pred_labels, f"pred {prop_type} labels", "text")

    gold_records = _build_name_records(gold_labels)
    pred_records = _build_name_records(pred_labels)

    metrics_per_method = {}
    for method in methods:
        metrics_per_method[method] = _match_one_method_standalone(
            gold_records, pred_records, method, model_id,
        )

    all_score_tables = {}
    for method in methods:
        try:
            all_score_tables[method] = _compute_full_score_table(
                gold_records, pred_records, method, model_id,
            )
        except Exception as e:
            print(f"      [{method}] skipped (full-table compute failed: {e})")

    best_map = _build_best_prop_map_top_n(
        all_score_tables,
        top_n=top_n,
        final_threshold=final_threshold,
        return_trace=False,
    )

    n_aligned = len(best_map)
    used_preds = {info["pred_term"] for info in best_map.values()}
    metrics_best = _calc_metrics(
        tp_g=n_aligned, tp_p=len(used_preds),
        n_gold=len(gold_labels), n_pred=len(pred_labels),
    )

    print(f"    [{prop_type}]  gold={len(gold_labels)}  pred={len(pred_labels)}")
    for method, m in metrics_per_method.items():
        print(f"      [layer2 {method}]  cov={m['coverage']:.3f}  "
              f"P={m['precision']:.3f}  R={m['recall']:.3f}  F1={m['f1']:.3f}")
    print(f"      [layer3 best]  cov={metrics_best['coverage']:.3f}  "
          f"P={metrics_best['precision']:.3f}  R={metrics_best['recall']:.3f}  "
          f"F1={metrics_best['f1']:.3f}")

    g2p: dict[str, list] = {g: [] for g in gold_labels}
    p2g: dict[str, list] = {p: [] for p in pred_labels}
    for gold_term, info in best_map.items():
        g2p[gold_term].append({
            "pred": info["pred_term"],
            "score": round(info["score"], 4),
            "method": info["matching_way"],
        })
        p2g[info["pred_term"]].append({
            "gold": gold_term,
            "score": round(info["score"], 4),
            "method": info["matching_way"],
        })

    return {
        "n_gold_labels": len(gold_labels),
        "n_pred_labels": len(pred_labels),
        "gold_to_pred": g2p,
        "pred_to_gold": p2g,
        "metrics_per_method": metrics_per_method,
        "metrics_best": metrics_best,
        "best_map": best_map,
    }


def eval_label_matching(
    gold_props: list[PropertyRecord],
    pred_props: list[PropertyRecord],
    methods: list[str],
    model_id: Optional[str] = None,
    top_n: int = 3,
    final_threshold: float = 0.0,
) -> dict:
    gold_groups = _group_by_type(gold_props)
    pred_groups = _group_by_type(pred_props)

    result = {}
    tot_tp_g = tot_tp_p = tot_gold = tot_pred = 0

    for prop_type in ALL_PROP_TYPES:
        g_group = gold_groups[prop_type]
        p_group = pred_groups[prop_type]

        if not g_group and not p_group:
            result[prop_type] = None
            continue

        result[prop_type] = _eval_within_type(
            g_group, p_group, prop_type, methods,
            model_id, top_n, final_threshold,
        )
        m = result[prop_type]["metrics_best"]
        tot_tp_g += m["gold_covered"]
        tot_tp_p += m["pred_supported"]
        tot_gold += result[prop_type]["n_gold_labels"]
        tot_pred += result[prop_type]["n_pred_labels"]

    overall = _calc_metrics(tot_tp_g, tot_tp_p, tot_gold, tot_pred)
    result["overall"] = overall

    print(f"\n  [overall layer3 best]  cov={overall['coverage']:.3f}  "
          f"P={overall['precision']:.3f}  R={overall['recall']:.3f}  "
          f"F1={overall['f1']:.3f}")

    return result


def eval_functional(
    gold_props: list[PropertyRecord],
    pred_props: list[PropertyRecord],
    gold_to_pred_best: dict[str, set],
    char_result: Optional[dict] = None,
) -> dict:
    if char_result is None:

        char_result = eval_characteristics(
            gold_props, pred_props, gold_to_pred_best,
        )

    onto = char_result.get("per_characteristic_ontology", {})
    result: dict = {}
    for char in ("Functional", "InverseFunctional"):
        m = onto.get(char, {})
        tp = m.get("tp", 0)
        fp = m.get("fp", 0)
        fn = m.get("fn", 0)
        result[char] = {
            "precision": m.get("precision"),
            "recall":    m.get("recall"),
            "f1":        m.get("f1"),
            "tp": tp, "fp": fp, "fn": fn,
            "fn_from_pairs":     m.get("fn_from_pairs", 0),
            "fn_from_unaligned": m.get("fn_from_unaligned", 0),
        }

        def _fmt(v):
            return f"{v:.3f}" if v is not None else "  N/A"

        print(f"  [functional/{char}, ontology-level]  "
              f"P={_fmt(m.get('precision'))}  R={_fmt(m.get('recall'))}  "
              f"F1={_fmt(m.get('f1'))}  tp={tp}  fp={fp}  fn={fn}  "
              f"(fn_from_pairs={m.get('fn_from_pairs', 0)}, "
              f"fn_from_unaligned={m.get('fn_from_unaligned', 0)})")
    return result


def save_best_matching_csv(label_matching: dict, output_path: str) -> None:
    rows = []
    for prop_type in ALL_PROP_TYPES:
        data = label_matching.get(prop_type)
        if not data:
            continue
        for gold_term, entries in data.get("gold_to_pred", {}).items():
            if not entries:
                continue
            e = entries[0]
            rows.append({
                "prop_type": prop_type,
                "gold_term": gold_term,
                "pred_term": e["pred"],
                "method": e.get("method", "unknown"),
                "score": e.get("score", 0.0),
            })
    rows.sort(key=lambda x: (x["prop_type"], x["gold_term"]))

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Gold_term", "Pre_term", "Method", "Score"])
        for r in rows:
            writer.writerow([r["gold_term"], r["pred_term"],
                             r["method"], r["score"]])
    print(f"Best property matching CSV saved to: {output_path}")


def _compute_property_alignment_trace(
    gold_props, pred_props, methods, model_id,
    top_n, final_threshold,
):
    gold_groups = _group_by_type(gold_props)
    pred_groups = _group_by_type(pred_props)

    all_traces = []
    for prop_type in ALL_PROP_TYPES:
        g_group = gold_groups[prop_type]
        p_group = pred_groups[prop_type]
        if not g_group or not p_group:
            continue
        gold_labels = sorted(set(p.label for p in g_group if p.label))
        pred_labels = sorted(set(p.label for p in p_group if p.label))
        gold_records = _build_name_records(gold_labels)
        pred_records = _build_name_records(pred_labels)

        all_score_tables = {}
        for method in methods:
            try:
                all_score_tables[method] = _compute_full_score_table(
                    gold_records, pred_records, method, model_id,
                )
            except Exception:
                pass

        _, trace = _build_best_prop_map_top_n(
            all_score_tables,
            top_n=top_n,
            final_threshold=final_threshold,
            return_trace=True,
        )
        for row in trace:
            row["prop_type"] = prop_type
        all_traces.extend(trace)

    return all_traces


def save_property_alignment_trace_csv(
    gold_props, pred_props, methods, model_id,
    top_n, final_threshold, output_path,
):

    all_traces = _compute_property_alignment_trace(
        gold_props, pred_props, methods, model_id, top_n, final_threshold,
    )
    fields = ["prop_type", "gold_term", "pred_term", "top_methods_used",
              "scores_by_method", "is_hard_match", "agg_score",
              "selected", "reason"]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in all_traces:
            writer.writerow(row)
    print(f"Property alignment trace saved to: {output_path}")


def save_property_alignment_trace_json(
    gold_props, pred_props, methods, model_id,
    top_n, final_threshold, output_path,
):

    all_traces = _compute_property_alignment_trace(
        gold_props, pred_props, methods, model_id, top_n, final_threshold,
    )
    out = []
    for i, row in enumerate(all_traces, 1):

        scores_dict = {}
        scores_str = row.get("scores_by_method", "")
        for part in scores_str.split(";"):
            part = part.strip()
            if not part:
                continue
            if "=" in part:
                m, s = part.split("=", 1)
                try:
                    scores_dict[m.strip()] = float(s.strip())
                except ValueError:
                    scores_dict[m.strip()] = s.strip()
        top_methods = [m for m in row.get("top_methods_used", "").split("+")
                       if m]
        out.append({
            "id": i,
            "prop_type": row.get("prop_type"),
            "gold_term": row.get("gold_term"),
            "pred_term": row.get("pred_term"),
            "top_methods_used": top_methods,
            "scores_by_method": scores_dict,
            "is_hard_match": row.get("is_hard_match"),
            "agg_score": row.get("agg_score"),
            "selected": row.get("selected"),
            "reason": row.get("reason"),
        })
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Property alignment trace (JSON) saved to: {output_path}")


def build_property_report_md(
    gold_props, pred_props,
    type_dist: dict,
    label_matching: dict,
    func_result: dict,
    char_result: dict,
    top_n: int,
    final_threshold: float,
    model_id: str,
) -> str:
    lines = []

    lines.append("# Property-Level Label Matching Report")
    lines.append("")
    lines.append(f"_Generated by `eval_property.py`_  ")
    lines.append(f"_Methods compared: hard_match, jaro_winkler, "
                 f"levenshtein, sequence_match, semantic (model: "
                 f"`{model_id}`)_")
    lines.append("")

    lines.append("## Layer 1 — Property Statistics")
    lines.append("")
    lines.append("| Property type | Gold | Pred | Diff | Note |")
    lines.append("|---|---:|---:|---:|---|")
    for prop_type, info in type_dist.items():
        diff_str = f"{info['diff']:+d}" if info['diff'] else "0"
        lines.append(f"| {prop_type} | {info['gold_count']} | "
                     f"{info['pred_count']} | {diff_str} | {info['note']} |")
    lines.append("")
    n_gold = len(gold_props)
    n_pred = len(pred_props)
    lines.append(f"**Totals:** gold = {n_gold} properties, "
                 f"pred = {n_pred} properties.")
    lines.append("")

    lines.append("## Layer 2 — Per-Method Matching Results")
    lines.append("")
    lines.append("This layer reports the result of each matching method "
             "separately, grouped by property type. Each method applies "
             "one-to-one greedy matching with a fixed threshold "
             f"(hard_match {HARD_THRESHOLD}; lexical methods at "
             f"{LEXICAL_THRESHOLD}; semantic at {SEMANTIC_THRESHOLD}). "
             "These results are used for comparison before the final "
             "combined matching step.")
    lines.append("")

    for prop_type in ALL_PROP_TYPES:
        data = label_matching.get(prop_type)
        if not data:
            continue
        n_g = data["n_gold_labels"]
        n_p = data["n_pred_labels"]
        lines.append(f"### {prop_type}")
        lines.append("")
        lines.append(f"Gold: {n_g} | Pred: {n_p}")
        lines.append("")
        lines.append("| Method | TP_gold | Coverage | Precision | Recall | F1 |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for method, m in data["metrics_per_method"].items():
            tp_gold = int(round(m["recall"] * n_g))
            cov_str = "—" if n_g == 0 else f"{m['coverage']*100:.1f}%"
            p_str = "—" if n_p == 0 else f"{m['precision']*100:.1f}%"
            r_str = "—" if n_g == 0 else f"{m['recall']*100:.1f}%"
            f_str = "—" if (n_g == 0 or n_p == 0) else f"{m['f1']*100:.1f}%"
            lines.append(f"| `{method}` | {tp_gold}/{n_g} | "
                         f"{cov_str} | {p_str} | {r_str} | {f_str} |")
        lines.append("")


    lines.append("## Layer 3 — Best Matching Alignment Table")
    lines.append("")
    lines.append(f"Final gold–pred property matches are selected by "
             f"averaging the top {top_n} method scores for each pair, "
             f"then applying one-to-one greedy selection within each "
             f"property type.")
    if final_threshold > 0:
        lines.append("")
        lines.append(f"Threshold applied: **`final_threshold = "
                     f"{final_threshold}`** — pairs with averaged score "
                     f"below this are dropped (hard-match hits always "
                     f"pass).")
    else:
        lines.append("")
        lines.append("No threshold applied — every gold gets its best "
                     "candidate (subject to 1-to-1 conflict).")
    lines.append("")

    for prop_type in ALL_PROP_TYPES:
        data = label_matching.get(prop_type)
        if not data:
            continue
        best_map = data.get("best_map", {})
        n_g = data["n_gold_labels"]
        n_p = data["n_pred_labels"]

        if n_g == 0 and n_p == 0:
            continue

        lines.append(f"### {prop_type}")
        lines.append("")
        if best_map:
            lines.append("| Gold property | Pred property | Method(s) | Score |")
            lines.append("|---|---|---|---:|")
            sorted_items = sorted(
                best_map.items(), key=lambda kv: -kv[1].get("score", 0.0)
            )
            for gold, info in sorted_items:
                lines.append(f"| `{gold}` | `{info['pred_term']}` | "
                             f"{info['matching_way']} | "
                             f"{info['score']:.4f} |")
        else:
            lines.append(f"_No aligned pairs found for {prop_type} "
                         f"(gold has {n_g}, pred has {n_p}, no pair "
                         f"reached the threshold or all candidates "
                         f"failed 1-to-1)._")
        lines.append("")

        tp = len(best_map)
        used_preds = {info["pred_term"] for info in best_map.values()}
        fn = n_g - tp
        fp = n_p - len(used_preds)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)
              if (precision + recall) else 0.0)

        p_str = f"{precision*100:.1f}% ({tp}/{tp+fp})" if (tp + fp) else "— (0/0)"
        r_str = f"{recall*100:.1f}% ({tp}/{tp+fn})" if (tp + fn) else "— (0/0)"
        f_str = f"{f1*100:.1f}%" if (tp + fp) and (tp + fn) else "—"

        lines.append(f"**Alignment summary ({prop_type}):**")
        lines.append("")
        lines.append("| Metric | Count | Definition |")
        lines.append("|---|---:|---|")
        lines.append(f"| TP | {tp} | Gold properties aligned to a pred property |")
        lines.append(f"| FN | {fn} | Gold properties with no pred match |")
        lines.append(f"| FP | {fp} | Pred properties with no gold match |")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|---|---:|")
        lines.append(f"| Precision = TP / (TP + FP) | {p_str} |")
        lines.append(f"| Recall = TP / (TP + FN) | {r_str} |")
        lines.append(f"| F1 | {f_str} |")
        lines.append("")

    overall = label_matching.get("overall", {})
    if overall:
        total_tp = total_fn = total_fp = 0
        for prop_type in ALL_PROP_TYPES:
            data = label_matching.get(prop_type)
            if not data:
                continue
            best_map = data.get("best_map", {})
            n_g = data.get("n_gold_labels", 0)
            n_p = data.get("n_pred_labels", 0)
            used_preds = {info["pred_term"] for info in best_map.values()}
            total_tp += len(best_map)
            total_fn += n_g - len(best_map)
            total_fp += n_p - len(used_preds)

        o_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0.0
        o_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 0.0
        o_f1 = (2 * o_p * o_r / (o_p + o_r)) if (o_p + o_r) else 0.0

        lines.append("### Overall — Property Label Matching (across all property types)")
        lines.append("")
        lines.append("Sums TP/FN/FP across all property types and "
                     "computes aggregate Precision/Recall/F1. Every gold "
                     "property and every pred property contributes to "
                     "the denominator: unaligned gold properties count "
                     "as FN, unaligned pred properties count as FP.")
        lines.append("")
        lines.append("| Metric | Count | Definition |")
        lines.append("|---|---:|---|")
        lines.append(f"| TP | {total_tp} | Gold properties aligned to "
                     f"a pred property (across all types) |")
        lines.append(f"| FN | {total_fn} | Gold properties with no pred "
                     f"match (across all types) |")
        lines.append(f"| FP | {total_fp} | Pred properties with no gold "
                     f"match (across all types) |")
        lines.append("")
        op_str = f"**{o_p*100:.1f}%** ({total_tp}/{total_tp+total_fp})" if (total_tp + total_fp) else "**—** (0/0)"
        or_str = f"**{o_r*100:.1f}%** ({total_tp}/{total_tp+total_fn})" if (total_tp + total_fn) else "**—** (0/0)"
        of_str = f"**{o_f1*100:.1f}%**" if (total_tp + total_fp) and (total_tp + total_fn) else "**—**"
        lines.append("| Metric | Value |")
        lines.append("|---|---:|")
        lines.append(f"| Precision = TP / (TP + FP) | {op_str} |")
        lines.append(f"| Recall = TP / (TP + FN) | {or_str} |")
        lines.append(f"| F1 | {of_str} |")
        lines.append("")

    if func_result or char_result:

        lines.append("The characteristic evaluation is reported under two "
             "denominators, so the FN counts may differ between tables:")
        lines.append("")
        lines.append("- **Ontology-level** — denominator is all gold "
                     "ObjectProperty (unaligned ones still contribute FN). "
                     "\"How much of gold did we recover?\"")
        lines.append("- **Pair-level** — denominator is aligned "
                     "(gold, pred) pairs only. \"On what we could compare, "
                     "did we get it right?\"")
        lines.append("")
        lines.append("All 7 OWL object property characteristics are "
                     "evaluated (Functional, InverseFunctional, Transitive, "
                     "Symmetric, Asymmetric, Reflexive, Irreflexive). Rows "
                     "where both gold and pred declare nothing are shown "
                     "as zeros for completeness.")
        lines.append("")

        def _num(v, default=0):
            return v if v is not None else default
        def _pct(v):
            return "—" if v is None else f"{v*100:.1f}%"

        if char_result and isinstance(char_result, dict):
            per_char_pair = char_result.get("per_characteristic", {})
            per_char_onto = char_result.get("per_characteristic_ontology", {})
            overall_pair  = char_result.get("overall", {})
            overall_onto  = char_result.get("overall_ontology", {})
            n_eval        = char_result.get("n_pairs_evaluated", 0)
            n_skip        = char_result.get("n_pairs_skipped", 0)
            unaligned     = char_result.get("unaligned_gold_with_chars", []) or []

            char_order = list(per_char_onto.keys()) or list(per_char_pair.keys())

            if char_order or overall_pair or overall_onto:

                lines.append("### All Characteristics — ontology-level")
                lines.append("")
                if unaligned:
                    labels_str = ", ".join(f"`{e['label']}`" for e in unaligned)
                    lines.append(
                        f"_Denominator includes **{len(unaligned)}** unaligned "
                        f"gold ObjectProperty ({labels_str}). Their declared "
                        f"characteristics are counted as FN._"
                    )
                    lines.append("")
                lines.append("| Characteristic | TP | FP | FN | "
                             "FN (from pairs) | FN (from unaligned) | "
                             "Precision | Recall | F1 | Mutex |")
                lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
                for char in char_order:
                    m = per_char_onto.get(char, {})
                    if not isinstance(m, dict):
                        continue
                    mutex = m.get("mutex_partner") or "—"
                    lines.append(
                        f"| `{char}` | {_num(m.get('tp'))} | "
                        f"{_num(m.get('fp'))} | {_num(m.get('fn'))} | "
                        f"{_num(m.get('fn_from_pairs'))} | "
                        f"{_num(m.get('fn_from_unaligned'))} | "
                        f"{_pct(m.get('precision'))} | "
                        f"{_pct(m.get('recall'))} | "
                        f"{_pct(m.get('f1'))} | "
                        f"{mutex} |"
                    )
                lines.append("")

                if overall_onto:
                    lines.append("**Overall — ontology-level "
                                 "(all characteristics):**")
                    lines.append("")
                    lines.append("| TP | FP | FN | Precision | Recall | F1 |")
                    lines.append("|---:|---:|---:|---:|---:|---:|")
                    lines.append(f"| {_num(overall_onto.get('tp'))} | "
                                 f"{_num(overall_onto.get('fp'))} | "
                                 f"{_num(overall_onto.get('fn'))} | "
                                 f"{_pct(overall_onto.get('precision'))} | "
                                 f"{_pct(overall_onto.get('recall'))} | "
                                 f"{_pct(overall_onto.get('f1'))} |")
                    lines.append("")

                lines.append("### All Characteristics — pair-level")
                lines.append("")
                lines.append(f"_{n_eval} pair(s) evaluated, {n_skip} pair(s) "
                             f"skipped (both sides had no characteristics)._")
                lines.append("")
                lines.append("| Characteristic | TP | FP | FN | "
                             "Precision | Recall | F1 | Mutex |")
                lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
                for char in char_order:
                    m = per_char_pair.get(char, {})
                    if not isinstance(m, dict):
                        continue
                    mutex = m.get("mutex_partner") or "—"
                    lines.append(
                        f"| `{char}` | {_num(m.get('tp'))} | "
                        f"{_num(m.get('fp'))} | {_num(m.get('fn'))} | "
                        f"{_pct(m.get('precision'))} | "
                        f"{_pct(m.get('recall'))} | "
                        f"{_pct(m.get('f1'))} | "
                        f"{mutex} |"
                    )
                lines.append("")

                if overall_pair:
                    lines.append("**Overall — pair-level "
                                 "(all characteristics):**")
                    lines.append("")
                    lines.append("| TP | FP | FN | Precision | Recall | F1 |")
                    lines.append("|---:|---:|---:|---:|---:|---:|")
                    lines.append(f"| {_num(overall_pair.get('tp'))} | "
                                 f"{_num(overall_pair.get('fp'))} | "
                                 f"{_num(overall_pair.get('fn'))} | "
                                 f"{_pct(overall_pair.get('precision'))} | "
                                 f"{_pct(overall_pair.get('recall'))} | "
                                 f"{_pct(overall_pair.get('f1'))} |")
                    lines.append("")

    return "\n".join(lines)


def append_property_report_to_md(report_text: str, output_path: str) -> None:
   
    if not os.path.exists(output_path):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"\n[report] Note: '{output_path}' did not exist. "
              f"Created a new file containing ONLY the property-level "
              f"report. To get a combined class+property report, first "
              f"run concept_label_matching.py with --save_report_md "
              f"pointing to the same file.")
        return

    with open(output_path, "r", encoding="utf-8") as f:
        existing = f.read()

    placeholder_marker = "# Property-Level Label Matching Report"
    placeholder_text = "_To be appended in a subsequent run"
    has_placeholder = (placeholder_marker in existing
                       and placeholder_text in existing)

    if has_placeholder:
        idx = existing.find(placeholder_marker)
        prefix = existing[:idx].rstrip()
        if prefix.endswith("---"):
            prefix = prefix[:-3].rstrip()
        new_existing = prefix + "\n\n"
        new_text = new_existing + "\n---\n\n" + report_text
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"\n[report] Property report appended to '{output_path}' "
              f"(replaced placeholder from class step).")
        return

    has_existing_property = (placeholder_marker in existing
                             and not placeholder_text in existing)
    if has_existing_property:

        idx = existing.find(placeholder_marker)
        prefix = existing[:idx].rstrip()
        if prefix.endswith("---"):
            prefix = prefix[:-3].rstrip()
        new_existing = prefix + "\n\n"
        new_text = new_existing + "\n---\n\n" + report_text
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"\n[report] Property section already existed in "
              f"'{output_path}' — replaced it with the new run.")
        return

    if not existing.endswith("\n"):
        existing += "\n"
    new_text = existing + "\n---\n\n" + report_text
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_text)
    print(f"\n[report] '{output_path}' existed but had no class-level "
          f"placeholder — appended property report at the end.")


def evaluate_properties(
    pred_file: str,
    gold_file: str,
    model_id: str,
    methods: Optional[list[str]] = None,
    top_n: int = 3,
    final_threshold: float = 0.0,
) -> dict:
    if methods is None:
        methods = ["hard_match", "sequence_match", "levenshtein",
                   "jaro_winkler", "semantic"]

    print("\n" + "=" * 60)
    print("PROPERTY EVALUATION")
    print("=" * 60)

    gold_props = parse_properties(gold_file)
    pred_props = parse_properties(pred_file)

    print(f"\n  Gold: {len(gold_props)} properties")
    print(f"  Pred: {len(pred_props)} properties\n")

    print("-- Step 1: Type distribution ---")
    type_dist = eval_type_distribution(gold_props, pred_props)
    print()

    print("-- Step 2/3: Within-type label matching "
          f"(layer-2 standalone + layer-3 top-{top_n} avg, "
          f"final_threshold={final_threshold}) --")
    label_matching = eval_label_matching(
        gold_props, pred_props, methods, model_id,
        top_n=top_n, final_threshold=final_threshold,
    )
    print()

    obj_data = label_matching.get("ObjectProperty")
    obj_best: dict[str, set] = {}
    if obj_data:
        for g, entries in obj_data["gold_to_pred"].items():
            obj_best[g] = {e["pred"] for e in entries}

    print("-- Step 5: Characteristics check --")
    char_result = eval_characteristics(gold_props, pred_props, obj_best)
    print()

    print("-- Step 4: Functional check (ontology-level view) --")
    func_result = eval_functional(
        gold_props, pred_props, obj_best, char_result=char_result,
    )
    print()

    return {
        "summary": {"n_gold": len(gold_props), "n_pred": len(pred_props)},
        "type_distribution": type_dist,
        "label_matching": label_matching,
        "functional_check": func_result,
        "characteristics_check": char_result,
        "config": {
            "top_n": top_n,
            "final_threshold": final_threshold,
            "model_id": model_id,
            "methods": methods,
        },
        "_gold_props": gold_props,
        "_pred_props": pred_props,
    }

def get_parser():
    p = argparse.ArgumentParser(description="Property Node Evaluation")
    p.add_argument("--model_id", default="embeddinggemma")
    p.add_argument("--pred_onto", required=True)
    p.add_argument("--gold_onto", required=True)
    p.add_argument("--methods",
                   default="hard_match,sequence_match,levenshtein,jaro_winkler,semantic")
    p.add_argument("--top_n", type=int, default=3,
                   help="Top-N method scores to average per pair (default 3)")
    p.add_argument("--final_threshold", type=float, default=0.0,
                   help="Drop pairs with averaged score below this "
                        "threshold (default 0 = no filter; recommended 0.6)")
    p.add_argument("--save_result", default=None,
                   help="Save full result JSON")
    p.add_argument("--save_best_matching_csv", default=None,
                   help="Save final best property matching as CSV")
    p.add_argument("--save_alignment_trace_csv", default=None,
                   help="Save per-pair alignment audit trace as CSV")
    p.add_argument("--save_alignment_trace_json", default=None,
                   help="Save per-pair alignment audit trace as JSON "
                        "(list-of-objects with id field). Same content "
                        "as --save_alignment_trace_csv but easier to "
                        "consume programmatically.")
    p.add_argument("--save_report_md", default=None,
                   help="Save Markdown report. If the file already exists "
                        "and contains a placeholder for property-level "
                        "results, the property report is appended to it; "
                        "otherwise a new file is written.")
    p.add_argument("--hard_threshold", type=float, default=None,
                   help="Override the hard_match threshold "
                        "(default 1.0).")
    p.add_argument("--lexical_threshold", type=float, default=None,
                   help="Override the lexical methods threshold "
                        "(sequence_match / levenshtein / jaro_winkler, "
                        "default 0.8).")
    p.add_argument("--semantic_threshold", type=float, default=None,
                   help="Override the semantic threshold "
                        "(default 0.6).")
    return p


def main():
    args = get_parser().parse_args()

    # Apply per-method threshold overrides FIRST, before any evaluation.
    global SEMANTIC_THRESHOLD, LEXICAL_THRESHOLD, HARD_THRESHOLD
    if args.semantic_threshold is not None:
        SEMANTIC_THRESHOLD = float(args.semantic_threshold)
    if args.lexical_threshold is not None:
        LEXICAL_THRESHOLD = float(args.lexical_threshold)
    if args.hard_threshold is not None:
        HARD_THRESHOLD = float(args.hard_threshold)
    # Rebuild the dict so downstream lookups see the new values.
    METHOD_THRESHOLDS["hard_match"]     = HARD_THRESHOLD
    METHOD_THRESHOLDS["sequence_match"] = LEXICAL_THRESHOLD
    METHOD_THRESHOLDS["levenshtein"]    = LEXICAL_THRESHOLD
    METHOD_THRESHOLDS["jaro_winkler"]   = LEXICAL_THRESHOLD
    METHOD_THRESHOLDS["semantic"]       = SEMANTIC_THRESHOLD
    print(f"[main] Per-method thresholds: "
          f"hard={HARD_THRESHOLD}, "
          f"lexical={LEXICAL_THRESHOLD}, "
          f"semantic={SEMANTIC_THRESHOLD}")

    methods = [m.strip() for m in args.methods.split(",") if m.strip()]
    valid_methods = set(METHOD_THRESHOLDS.keys())
    for m in methods:
        if m not in valid_methods:
            raise ValueError(f"Unsupported method '{m}'. "
                             f"Available methods: {sorted(valid_methods)}")

    result = evaluate_properties(
        pred_file=args.pred_onto,
        gold_file=args.gold_onto,
        model_id=args.model_id,
        methods=methods,
        top_n=args.top_n,
        final_threshold=args.final_threshold,
    )

    if args.save_result:

        clean = {k: v for k, v in result.items()
                 if not k.startswith("_")}
        if "label_matching" in clean:
            stripped_lm = {}
            for k, v in clean["label_matching"].items():
                if isinstance(v, dict):
                    stripped_lm[k] = {kk: vv for kk, vv in v.items()
                                      if kk != "best_map"}
                else:
                    stripped_lm[k] = v
            clean["label_matching"] = stripped_lm
        if "functional_check" in clean:
            clean["functional_check"] = {
                k: {kk: vv for kk, vv in v.items() if kk != "details"}
                for k, v in clean["functional_check"].items()
            }

        config = clean.pop("config", {})
        if "summary" in clean:
            config["summary"] = clean.pop("summary")

        results_list = []
        for section_name, section_data in clean.items():
            if isinstance(section_data, dict):
                results_list.append({"id": section_name, **section_data})
            else:
                results_list.append({"id": section_name, "value": section_data})

        out = {"config": config, "results": results_list}
        with open(args.save_result, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=True, indent=2)
        print(f"\nResult JSON saved to: {args.save_result}")

    if args.save_best_matching_csv:
        save_best_matching_csv(result["label_matching"],
                               args.save_best_matching_csv)

    if args.save_alignment_trace_csv:
        save_property_alignment_trace_csv(
            gold_props=result["_gold_props"],
            pred_props=result["_pred_props"],
            methods=methods,
            model_id=args.model_id,
            top_n=args.top_n,
            final_threshold=args.final_threshold,
            output_path=args.save_alignment_trace_csv,
        )

    if args.save_alignment_trace_json:
        save_property_alignment_trace_json(
            gold_props=result["_gold_props"],
            pred_props=result["_pred_props"],
            methods=methods,
            model_id=args.model_id,
            top_n=args.top_n,
            final_threshold=args.final_threshold,
            output_path=args.save_alignment_trace_json,
        )

    if args.save_report_md:
        report_text = build_property_report_md(
            gold_props=result["_gold_props"],
            pred_props=result["_pred_props"],
            type_dist=result["type_distribution"],
            label_matching=result["label_matching"],
            func_result=result["functional_check"],
            char_result=result["characteristics_check"],
            top_n=args.top_n,
            final_threshold=args.final_threshold,
            model_id=args.model_id,
        )
        append_property_report_to_md(report_text, args.save_report_md)


if __name__ == "__main__":
    main()
