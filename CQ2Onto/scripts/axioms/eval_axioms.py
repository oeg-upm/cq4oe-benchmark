from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Set, Tuple

try:
    import requests
except ImportError:
    requests = None  
global LITERAL_RELAX



def load_axioms(json_path: str) -> List[dict]:

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Axioms JSON not found: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "axioms" in data and isinstance(data["axioms"], list):
        return data["axioms"]
    if "gold_axioms" in data and isinstance(data["gold_axioms"], list):
        return data["gold_axioms"]
    raise ValueError(
        f"Unrecognized JSON in {json_path!r}. "
        f"Expected top-level 'axioms' or 'gold_axioms' list."
    )


def load_cq_definitions(json_path: str) -> List[dict]:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("cq_definitions", [])


def _norm(text):

    if text is None:
        return ""
    s = str(text).strip().lower()
    return re.sub(r"[\s_\-]+", "", s)

def load_alignment_csv(csv_path: str) -> Dict[str, str]:

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Alignment CSV not found: {csv_path}")

    raw_entries: List[Tuple[str, str, float]] = []
    seen_gold: Set[str] = set()
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            g = (row.get("Gold_term") or row.get("gold_term") or "").strip()
            p = (row.get("Pre_term") or row.get("pre_term")
                 or row.get("Pred_term") or row.get("pred_term") or "").strip()
            if not (g and p):
                continue
            if g in seen_gold:
                continue
            seen_gold.add(g)
            try:
                score = float(row.get("Score") or row.get("score") or 0.0)
            except (TypeError, ValueError):
                score = 0.0
            raw_entries.append((g, p, score))

    pred_to_best: Dict[str, Tuple[str, float]] = {}     
    pred_conflicts: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
    for g, p, score in raw_entries:
        pred_conflicts[p].append((g, score))
        if p not in pred_to_best or score > pred_to_best[p][1]:
            pred_to_best[p] = (g, score)

    out: Dict[str, str] = {}
    dropped: List[Tuple[str, str, float]] = []  # (gold, pred, score) entries that lost
    for g, p, score in raw_entries:
        winner_gold, winner_score = pred_to_best[p]
        if g == winner_gold:
            out[g] = p
        else:
            dropped.append((g, p, score))

    if dropped:
        conflicting_preds = sorted(
            {p for g, ps in pred_conflicts.items() if len(ps) > 1
             for p in [g]}
        )
        print(f"  [alignment] WARNING: {len(dropped)} gold→pred mapping(s) "
              f"dropped due to multi-to-one conflicts on the pred side:",
              file=sys.stderr)
        for gold, pred, score in dropped:
            kept_gold, kept_score = pred_to_best[pred]
            print(f"    dropped: '{gold}' → '{pred}' (score={score:.4f})  "
                  f"[kept: '{kept_gold}' → '{pred}' (score={kept_score:.4f})]",
                  file=sys.stderr)
        print(f"  [alignment] If this is incorrect, edit the CSV to "
              f"resolve the conflict manually.", file=sys.stderr)

    return out


def label_map_for(json_path: str, axioms: List[dict]) -> Dict[str, str]:

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            doc = json.load(f)
        global_map = doc.get("name_to_label", {})
        if global_map:
            return dict(global_map)
    except Exception:
        pass
    m: Dict[str, str] = {}
    for ax in axioms:
        for k_iri, k_lbl in [("subject", "subject_label"),
                             ("term", "term_label")]:
            iri = ax.get(k_iri); lbl = ax.get(k_lbl)
            if iri and lbl and iri not in m:
                m[iri] = lbl
    return m


def label_map_from_owl(owl_path: str) -> Dict[str, str]:

    try:
        from rdflib import Graph, RDF, RDFS, OWL, URIRef, Literal
    except ImportError:
        print("[warn] rdflib not installed; cannot read labels from OWL.",
              file=sys.stderr)
        return {}
    if not os.path.exists(owl_path):
        print(f"[warn] OWL file not found: {owl_path}", file=sys.stderr)
        return {}

    g = Graph()
    fmt_used = None
    for fmt in ("xml", "turtle", "n3", "json-ld"):
        try:
            g.parse(owl_path, format=fmt)
            fmt_used = fmt
            break
        except Exception:
            g = Graph()
            continue
    if fmt_used is None:
        try:
            g.parse(owl_path)
            fmt_used = "auto"
        except Exception as e:
            print(f"[warn] Could not parse OWL {owl_path}: {e}",
                  file=sys.stderr)
            return {}

    def _resolve_label(uri_node):
        labels = list(g.objects(uri_node, RDFS.label))
        for lb in labels:
            if isinstance(lb, Literal) and getattr(lb, "language", None) == "en":
                return str(lb).strip()
        for lb in labels:
            if isinstance(lb, Literal) and getattr(lb, "language", None) in (None, ""):
                return str(lb).strip()
        for lb in labels:
            if isinstance(lb, Literal):
                return str(lb).strip()
        s = str(uri_node)
        if "#" in s:
            return s.split("#")[-1]
        return s.rstrip("/").split("/")[-1]

    out: Dict[str, str] = {}
    for type_class in (OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty):
        for s in g.subjects(RDF.type, type_class):
            if isinstance(s, URIRef):
                name = (str(s).split("#")[-1] if "#" in str(s)
                        else str(s).rstrip("/").split("/")[-1])
                out[name] = _resolve_label(s)
    return out


_TERM_TYPE_ORDER = ["Class", "ObjectProperty", "DatatypeProperty"]

_AXIOM_TYPES_BY_TERM_TYPE = {
    "Class":            ["SubClassOf", "EquivalentClasses", "DisjointClasses"],
    "ObjectProperty":   ["SubPropertyOf", "Domain", "Range",
                         "Characteristics", "InverseOf", "DisjointProperties"],
    "DatatypeProperty": ["SubPropertyOf", "Domain", "Range", "Characteristics"],
}


def compute_layer1(axioms: List[dict]) -> dict:
    counts: Dict[str, Counter] = defaultdict(Counter)
    for ax in axioms:
        tt = ax.get("term_type", "Unknown")
        at = ax.get("axiom_type", "Unknown")
        counts[tt][at] += 1
    return {
        "total": len(axioms),
        "by_term_type": {tt: sum(c.values()) for tt, c in counts.items()},
        "by_term_axiom": {tt: dict(c) for tt, c in counts.items()},
    }


def _format_layer1_table(stats_g: dict, stats_p: dict) -> str:
    lines = []
    lines.append(f"{'Category':<32}  {'Gold':>6}  {'Pred':>6}")
    lines.append("─" * 50)
    for tt in _TERM_TYPE_ORDER:
        g_total = stats_g["by_term_type"].get(tt, 0)
        p_total = stats_p["by_term_type"].get(tt, 0)
        if g_total == 0 and p_total == 0:
            continue
        lines.append(f"{tt + ' axioms':<32}  {g_total:>6}  {p_total:>6}")
        ordered = _AXIOM_TYPES_BY_TERM_TYPE.get(tt, [])
        observed = set(stats_g["by_term_axiom"].get(tt, {}).keys()) \
                 | set(stats_p["by_term_axiom"].get(tt, {}).keys())
        extras = sorted(observed - set(ordered))
        for at in ordered + extras:
            g_n = stats_g["by_term_axiom"].get(tt, {}).get(at, 0)
            p_n = stats_p["by_term_axiom"].get(tt, {}).get(at, 0)
            if g_n == 0 and p_n == 0:
                continue
            lines.append(f"  {at:<30}  {g_n:>6}  {p_n:>6}")
    lines.append("─" * 50)
    lines.append(f"{'TOTAL':<32}  {stats_g['total']:>6}  {stats_p['total']:>6}")
    return "\n".join(lines)


class EmbeddingClient:
    def __init__(self, model: str = "embeddinggemma",
                 base_url: str = "http://localhost:11434",
                 cache_path: Optional[str] = ".embed_cache.json",
                 use_cache: bool = True):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.use_cache = use_cache
        self.cache_path = cache_path
        self._cache: Dict[str, List[float]] = {}
        if use_cache and cache_path and os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            except Exception as e:
                print(f"[warn] Could not load embedding cache: {e}",
                      file=sys.stderr)

    def _key(self, text: str) -> str:
        return hashlib.sha256(f"{self.model}|{text}".encode("utf-8")).hexdigest()

    def embed(self, text: str) -> List[float]:
        if not text:
            return []
        if self.use_cache:
            k = self._key(text)
            if k in self._cache:
                return self._cache[k]
        if requests is None:
            raise RuntimeError(
                "The 'requests' library is required for embeddings.")
        for endpoint, payload, picker in [
            (f"{self.base_url}/api/embed",
             {"model": self.model, "input": text},
             lambda j: (j.get("embeddings") or [None])[0] or j.get("embedding")),
            (f"{self.base_url}/api/embeddings",
             {"model": self.model, "prompt": text},
             lambda j: j.get("embedding")),
        ]:
            try:
                r = requests.post(endpoint, json=payload, timeout=60)
                if r.status_code == 200:
                    vec = picker(r.json())
                    if vec:
                        if self.use_cache:
                            self._cache[self._key(text)] = vec
                        return vec
            except requests.RequestException:
                continue
        raise RuntimeError(
            f"Failed to get embedding from Ollama at {self.base_url} "
            f"for model '{self.model}'")

    def flush_cache(self) -> None:
        if self.use_cache and self.cache_path:
            try:
                with open(self.cache_path, "w", encoding="utf-8") as f:
                    json.dump(self._cache, f)
            except Exception as e:
                print(f"[warn] Could not save embedding cache: {e}",
                      file=sys.stderr)


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _axiom_embed_text(ax: dict) -> str:
    return ax.get("dl") or (ax.get("subject", "") + " " + ax.get("object", ""))


def _greedy_one_to_one(g_items, p_items, threshold: float):
    if not g_items or not p_items:
        return []
    sims = []
    for gi, (_, g_vec) in enumerate(g_items):
        for pi, (_, p_vec) in enumerate(p_items):
            sim = _cosine(g_vec, p_vec)
            if sim >= threshold:
                sims.append((sim, gi, pi))
    sims.sort(reverse=True)
    used_g, used_p = set(), set()
    out = []
    for sim, gi, pi in sims:
        if gi in used_g or pi in used_p:
            continue
        used_g.add(gi); used_p.add(pi)
        out.append((g_items[gi][0], p_items[pi][0], sim))
    return out


def compute_layer2(gold_axioms, pred_axioms, client, threshold=0.6):
    print(f"\n[Layer 2] Embedding {len(gold_axioms)} gold + "
          f"{len(pred_axioms)} pred axioms with model='{client.model}', "
          f"threshold={threshold}", file=sys.stderr)

    gold_vecs = []
    for i, ax in enumerate(gold_axioms):
        gold_vecs.append((ax, client.embed(_axiom_embed_text(ax))))
        if (i + 1) % 20 == 0:
            print(f"  ...gold {i+1}/{len(gold_axioms)}", file=sys.stderr)
    pred_vecs = []
    for i, ax in enumerate(pred_axioms):
        pred_vecs.append((ax, client.embed(_axiom_embed_text(ax))))
        if (i + 1) % 20 == 0:
            print(f"  ...pred {i+1}/{len(pred_axioms)}", file=sys.stderr)

    client.flush_cache()

    def _bucket(ax):
        return (ax.get("term_type", "Unknown"), ax.get("axiom_type", "Unknown"))

    buckets = sorted(set(_bucket(ax) for ax, _ in gold_vecs)
                   | set(_bucket(ax) for ax, _ in pred_vecs))

    bucket_results = {}
    for bk in buckets:
        g_items = [(ax, v) for ax, v in gold_vecs if _bucket(ax) == bk]
        p_items = [(ax, v) for ax, v in pred_vecs if _bucket(ax) == bk]
        pairs = _greedy_one_to_one(g_items, p_items, threshold)
        bucket_results[bk] = _attach_prf({
            "gold_count": len(g_items),
            "pred_count": len(p_items),
            "matched": len(pairs),
            "match_rate": (len(pairs) / max(len(g_items), len(p_items))
                           if max(len(g_items), len(p_items)) else 0.0),
            "pairs": pairs,
        })

    per_term_type = {}
    for tt in set(b[0] for b in buckets):
        g_n = sum(r["gold_count"] for k, r in bucket_results.items() if k[0] == tt)
        p_n = sum(r["pred_count"] for k, r in bucket_results.items() if k[0] == tt)
        m = sum(r["matched"] for k, r in bucket_results.items() if k[0] == tt)
        per_term_type[tt] = _attach_prf({
            "gold_count": g_n, "pred_count": p_n, "matched": m,
            "match_rate": (m / max(g_n, p_n)) if max(g_n, p_n) else 0.0,
        })

    overall_pairs = _greedy_one_to_one(gold_vecs, pred_vecs, threshold)
    overall = _attach_prf({
        "gold_count": len(gold_vecs), "pred_count": len(pred_vecs),
        "matched": len(overall_pairs),
        "match_rate": (len(overall_pairs) /
                       max(len(gold_vecs), len(pred_vecs))
                       if max(len(gold_vecs), len(pred_vecs)) else 0.0),
        "pairs": overall_pairs,
    })

    return {
        "threshold": threshold, "model": client.model,
        "buckets": bucket_results,
        "per_term_type": per_term_type,
        "overall": overall,
    }


def _attach_prf(metrics: dict) -> dict:
    tp = metrics.get("matched", 0)
    g = metrics.get("gold_count", 0)
    p = metrics.get("pred_count", 0)
    fp = max(p - tp, 0)
    fn = max(g - tp, 0)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall    = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) \
        if (precision + recall) else 0.0
    metrics["precision"] = precision
    metrics["recall"]    = recall
    metrics["f1"]        = f1
    return metrics


def _format_layer2_table(layer2: dict) -> str:
    lines = []
    lines.append(f"Embedding model: {layer2['model']}, "
                 f"cosine threshold: {layer2['threshold']}, "
                 f"matching: greedy one-to-one")
    lines.append("")
    lines.append("Embedding-based semantic matching")
    lines.append("Match rate: matched / max(gold, pred).")
    lines.append("")
    header = (f"{'Type / AxiomType':<36}  {'Gold':>5}  {'Pred':>5}  "
              f"{'Match':>5}  {'Rate':>6}  {'P':>6}  {'R':>6}  {'F1':>6}")
    lines.append(header)
    lines.append("─" * len(header))
    for tt in _TERM_TYPE_ORDER:
        if tt not in layer2["per_term_type"]:
            continue
        ptt = layer2["per_term_type"][tt]
        if ptt["gold_count"] == 0 and ptt["pred_count"] == 0:
            continue
        lines.append(f"{tt + ' axioms':<36}  "
                     f"{ptt['gold_count']:>5}  {ptt['pred_count']:>5}  "
                     f"{ptt['matched']:>5}  {ptt['match_rate']*100:>5.1f}%  "
                     f"{ptt['precision']*100:>5.1f}%  "
                     f"{ptt['recall']*100:>5.1f}%  "
                     f"{ptt['f1']*100:>5.1f}%")
        ordered = _AXIOM_TYPES_BY_TERM_TYPE.get(tt, [])
        observed = sorted({k[1] for k in layer2["buckets"] if k[0] == tt})
        extras = [a for a in observed if a not in ordered]
        for at in ordered + extras:
            br = layer2["buckets"].get((tt, at))
            if not br or (br["gold_count"] == 0 and br["pred_count"] == 0):
                continue
            lines.append(f"  {at:<34}  "
                         f"{br['gold_count']:>5}  {br['pred_count']:>5}  "
                         f"{br['matched']:>5}  {br['match_rate']*100:>5.1f}%  "
                         f"{br['precision']*100:>5.1f}%  "
                         f"{br['recall']*100:>5.1f}%  "
                         f"{br['f1']*100:>5.1f}%")
    lines.append("─" * len(header))
    o = layer2["overall"]
    lines.append(f"{'Overall (one greedy pass)':<36}  "
                 f"{o['gold_count']:>5}  {o['pred_count']:>5}  "
                 f"{o['matched']:>5}  {o['match_rate']*100:>5.1f}%  "
                 f"{o['precision']*100:>5.1f}%  "
                 f"{o['recall']*100:>5.1f}%  "
                 f"{o['f1']*100:>5.1f}%")
    return "\n".join(lines)


def _save_layer2_pairs_csv(layer2: dict, csv_path: str) -> None:
    rows = []
    for g_ax, p_ax, sim in layer2["overall"]["pairs"]:
        rows.append({
            "gold_id": g_ax.get("id", ""), "gold_dl": g_ax.get("dl", ""),
            "pred_id": p_ax.get("id", ""), "pred_dl": p_ax.get("dl", ""),
            "cosine": f"{sim:.4f}",
        })
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["gold_id", "gold_dl",
                                          "pred_id", "pred_dl", "cosine"])
        w.writeheader()
        w.writerows(rows)


STATUSES = ("tp", "fn", "fp", "mismatch", "skip")

_XSD_PREFIXES = (
    "http://www.w3.org/2001/XMLSchema#",
    "http://www.w3.org/2001/xmlschema#",
)



#default
LITERAL_RELAX = False

def normalize_datatype(s: str) -> str:
    if not s:
        return ""
    t = str(s).strip()
    lower = t.lower()
    if t.count("xsd:") > 1 or ("#" in t and "xsd:" in lower):
        if t.count("xsd:") > 1:
            idx = lower.rfind("xsd:")
            t = t[idx:]
        elif "#" in t:
            t = t.rsplit("#", 1)[1]
    for p in _XSD_PREFIXES:
        if t.lower().startswith(p.lower()):
            t = t[len(p):]
            break
    for prefix in ("xsd:", "xs:", "xsd1:"):
        if t.lower().startswith(prefix):
            t = t[len(prefix):]
            break
    t = t.lower().strip()
    aliases = {
        "int": "integer",
        "bool": "boolean",
        "datetime": "dateTime",
        "date time": "dateTime",
        "positiveinteger": "positiveInteger",
        "positive integer": "positiveInteger",
        "nonnegativeinteger": "nonNegativeInteger",
        "gyear": "gYear",
    }
    t = aliases.get(t, t)
    return f"xsd:{t}"


def normalize_oneof(struct: dict) -> dict:
    if not isinstance(struct, dict):
        return struct
    if struct.get("expr_type") == "ObjectHasValue":
        return {
            "expr_type": "ObjectSomeValuesFrom",
            "property": struct.get("property"),
            "filler": {
                "expr_type": "ObjectOneOf",
                "individuals": [struct.get("value")],
            },
        }
    return struct


def _norm_entity(x) -> str:

    if x is None:
        return ""
    s = str(x).strip()
    if "#" in s:
        s = s.split("#", 1)[1]
    elif "/" in s and ":" in s.split("/", 1)[0]:   # http://... URI
        s = s.rstrip("/").split("/")[-1]
    return s.lower().replace(" ", "").replace("_", "")


def _aligned_subject(g_ax: dict, term_type: str,
                     class_align: Dict[str, str],
                     prop_align: Dict[str, str]) -> Optional[str]:

    table = class_align if term_type == "Class" else prop_align
    table_norm = {_norm(k): v for k, v in table.items()}
    label = g_ax.get("subject_label") or g_ax.get("term_label")
    if label:
        nk = _norm(label)
        if nk in table_norm:
            return table_norm[nk]
    name = g_ax.get("subject") or g_ax.get("term") or ""
    if name:
        nk = _norm(name)
        if nk in table_norm:
            return table_norm[nk]
    return None


def _equal_under_class_align(gold_class, pred_class, class_align,
                             gold_label_map=None, pred_label_map=None):

    if not gold_class or not pred_class:
        return False
    gold_label_map = gold_label_map or {}
    pred_label_map = pred_label_map or {}
    g_label = gold_label_map.get(gold_class, gold_class)
    p_label = pred_label_map.get(pred_class, pred_class)
    table_norm = {_norm(k): _norm(v) for k, v in class_align.items()}
    for g, p in [(g_label, p_label), (g_label, pred_class),
                 (gold_class, p_label), (gold_class, pred_class)]:
        expected = table_norm.get(_norm(g))
        if expected is not None and expected == _norm(p):
            return True
    return False


def _equal_under_prop_align(gold_prop, pred_prop, prop_align,
                            gold_label_map=None, pred_label_map=None):

    if not gold_prop or not pred_prop:
        return False
    gold_label_map = gold_label_map or {}
    pred_label_map = pred_label_map or {}
    g_label = gold_label_map.get(gold_prop, gold_prop)
    p_label = pred_label_map.get(pred_prop, pred_prop)
    table_norm = {_norm(k): _norm(v) for k, v in prop_align.items()}
    for g, p in [(g_label, p_label), (g_label, pred_prop),
                 (gold_prop, p_label), (gold_prop, pred_prop)]:
        expected = table_norm.get(_norm(g))
        if expected is not None and expected == _norm(p):
            return True
    return False

def _struct_equal(g, p, class_align, prop_align, pred_entity_names,
                  gold_label_map=None, pred_label_map=None):
    g = normalize_oneof(g) if g else g
    p = normalize_oneof(p) if p else p

    if g is None and p is None:
        return True, ""
    if g is None or p is None:
        return False, "one side is None"


    gt = g.get("expr_type")
    pt = p.get("expr_type")
    if gt != pt:
        return False, f"expr_type {gt} vs {pt}"
    if gt == "Class":
        gn, pn = g.get("name", ""), p.get("name", "")
        if _equal_under_class_align(gn, pn, class_align,
                                    gold_label_map, pred_label_map):
            return True, ""
        return False, f"class {gn!r} not aligned to {pn!r}"

    if gt in ("ObjectProperty", "DatatypeProperty"):
        gn, pn = g.get("name", ""), p.get("name", "")
        if _equal_under_prop_align(gn, pn, prop_align,
                                   gold_label_map, pred_label_map):
            return True, ""
        return False, f"property {gn!r} not aligned to {pn!r}"

    if gt == "Datatype":
        g_norm = normalize_datatype(g.get("name", ""))
        p_norm = normalize_datatype(p.get("name", ""))
        if g_norm == p_norm:
            return True, ""
        # Relaxation (opt-in via --literal_relax yes)
        if LITERAL_RELAX:
            gl = g_norm.lower() if g_norm else ""
            pl = p_norm.lower() if p_norm else ""
            literal_roots = {
                "rdfs:literal", "xsd:literal",
                "xsd:anysimpletype", "xsd:anyatomictype",
                "xsd:rdfs:literal",
                "xsd:xsd:anysimpletype", "xsd:xsd:anyatomictype",
            }
            if gl in literal_roots and pl and pl not in literal_roots:
                return True, ""
        return False, f"datatype {g.get('name')!r} != {p.get('name')!r}"
    


    if gt == "Top":
        return True, ""


    if gt == "Declaration":
        g_tt = g.get("term_type")
        p_tt = p.get("term_type")
        if g_tt == p_tt:
            return True, ""
        return False, f"declaration term_type {g_tt!r} vs {p_tt!r}"

    if gt == "ObjectOneOf":
       
        
        g_members = {_norm_entity(m) for m in (g.get("individuals") or [])}
        p_members = {_norm_entity(m) for m in (p.get("individuals") or [])}
        if g_members == p_members: #must be exact match
            return True, ""
        only_gold = g_members - p_members
        only_pred = p_members - g_members
        return False, (f"OneOf members differ — only-gold: "
                       f"{sorted(only_gold) or '∅'}, only-pred: "
                       f"{sorted(only_pred) or '∅'}")

    if gt in ("ObjectIntersectionOf", "ObjectUnionOf"):
        g_ops = g.get("operands") or []
        p_ops = p.get("operands") or []
        if len(g_ops) != len(p_ops): 
            return False, f"{gt} operand count {len(g_ops)} vs {len(p_ops)}"
        used = set()
        for gi, gop in enumerate(g_ops):
            found = None
            reasons = []
            for pi, pop in enumerate(p_ops):
                if pi in used:
                    continue
                #equal and reson
                eq, why = _struct_equal(gop, pop, class_align, prop_align,
                                        pred_entity_names,
                                        gold_label_map, pred_label_map)
                if eq:
                    found = pi
                    break
                reasons.append(f"pred operand #{pi}: {why}")
            if found is None:
                detail = "; ".join(reasons[:3])
                if len(reasons) > 3:
                    detail += "; ..."
                return False, (f"{gt}: gold operand #{gi} has no match "
                               f"in pred ({detail})")
            used.add(found)
        return True, ""

    if gt in ("ObjectSomeValuesFrom", "ObjectAllValuesFrom"):
        gp, pp = g.get("property", ""), p.get("property", "")
        if not _equal_under_prop_align(gp, pp, prop_align,
                                       gold_label_map, pred_label_map):
            return False, f"property {gp!r} not aligned to {pp!r}"
        eq, why = _struct_equal(g.get("filler"), p.get("filler"),
                                class_align, prop_align, pred_entity_names,
                                gold_label_map, pred_label_map)
        if eq:
            return True, ""
        return False, f"filler differs: {why}"

    if gt in ("ObjectMinCardinality", "ObjectMaxCardinality",
              "ObjectExactCardinality"):

        g_n = g.get("n", g.get("cardinality"))
        p_n = p.get("n", p.get("cardinality"))
        if g_n != p_n:
            return False, f"cardinality n differs: {g_n} vs {p_n}"
        gp, pp = g.get("property", ""), p.get("property", "")
        if not _equal_under_prop_align(gp, pp, prop_align,
                                       gold_label_map, pred_label_map):
            return False, f"cardinality property {gp!r} not aligned to {pp!r}"
        eq, why = _struct_equal(g.get("filler"), p.get("filler"),
                                class_align, prop_align, pred_entity_names,
                                gold_label_map, pred_label_map)
        if eq:
            return True, ""
        return False, f"cardinality filler differs: {why}"
    
 ##¬C, "expr_type": "ObjectComplementOf",
           # "operand": {
             # "expr_type": "Class",
            #  "name": "WhiteWine"}
            
    if gt == "ObjectComplementOf":
        eq, why = _struct_equal(g.get("operand"), p.get("operand"),
                                class_align, prop_align, pred_entity_names,
                                gold_label_map, pred_label_map)
        if eq:
            return True, ""
        return False, f"complement operand differs: {why}"

    if gt == "PropertyCharacteristic":
        if g.get("name") == p.get("name"):
            return True, ""
        return False, f"characteristic {g.get('name')} vs {p.get('name')}"


    if gt == "InverseObjectProperty":
        gn, pn = g.get("name", ""), p.get("name", "")
        if _equal_under_prop_align(gn, pn, prop_align,
                                   gold_label_map, pred_label_map):
            return True, ""
        return False, f"inverse-property {gn!r} not aligned to {pn!r}"

    return False, f"unsupported expr_type: {gt}"


def _collect_pred_entity_names(pred_axioms: List[dict]) -> set:
    names = set()
    for ax in pred_axioms:
        if ax.get("term"):
            names.add(ax["term"])

    def _walk(node):
        if not isinstance(node, dict):
            return
        et = node.get("expr_type")
        if et in ("Class", "ObjectProperty", "DatatypeProperty"):
            n = node.get("name")
            if n: names.add(n)
        if et == "ObjectOneOf":
            for ind in node.get("individuals") or []:
                names.add(ind)
        if et == "ObjectHasValue":
            v = node.get("value")
            if v: names.add(v)
        for k in ("filler", "lhs", "rhs", "operand"):
            if k in node:
                _walk(node.get(k))
        for o in node.get("operands", []) or []:
            _walk(o)

    for ax in pred_axioms:
        _walk(ax.get("rhs_struct"))
        _walk(ax.get("lhs_struct"))
    return names


def _judge_one_axiom(g_ax, pred_index, class_align, prop_align,
                     pred_entity_names,
                     gold_label_map=None, pred_label_map=None,
                     used_pred_ids=None):

    if used_pred_ids is None:
        used_pred_ids = set()
    aid = g_ax.get("id", "?")
    tt = g_ax.get("term_type", "")
    at = g_ax.get("axiom_type", "")
    g_subj = g_ax.get("subject") or g_ax.get("term") or ""
    g_dl = g_ax.get("dl", "")
    g_rhs = g_ax.get("rhs_struct")

    p_subj = _aligned_subject(g_ax, tt, class_align, prop_align)
    if p_subj is None:
        return {
            "side": "gold",
            "axiom_id": aid, "term": g_subj, "term_type": tt, "axiom_type": at,
            "dl": g_dl, "status": "skip",
            "reason": f"subject {g_subj!r} not in alignment table",
            "pred_match": None,
        }

    candidates = pred_index.get((_norm(p_subj), at), [])

    candidates = [c for c in candidates
                  if c.get("id") not in used_pred_ids]
    if not candidates:
        return {
            "side": "gold",
            "axiom_id": aid, "term": g_subj, "term_type": tt, "axiom_type": at,
            "dl": g_dl, "status": "fn",
            "reason": f"pred has no {at} axiom on {p_subj!r}",
            "pred_match": None,
        }

    failures = []
    for cand in candidates:
        eq, why = _struct_equal(g_rhs, cand.get("rhs_struct"),
                                class_align, prop_align, pred_entity_names,
                                gold_label_map, pred_label_map)
        if eq:
            return {
                "side": "gold",
                "axiom_id": aid, "term": g_subj, "term_type": tt, "axiom_type": at,
                "dl": g_dl, "status": "tp",
                "reason": f"matched pred {cand.get('id', '?')}",
                "pred_match": cand,
            }
        failures.append((cand, why))

    cand_ax, why = failures[0]
    return {
        "side": "gold",
        "axiom_id": aid, "term": g_subj, "term_type": tt, "axiom_type": at,
        "dl": g_dl, "status": "mismatch",
        "reason": f"pred {cand_ax.get('id', '?')} differs: {why}",
        "pred_match": cand_ax,
    }


def compute_layer3(gold, pred, class_align, prop_align,
                   gold_label_map=None, pred_label_map=None):

    pred_index: Dict[Tuple[str, str], List[dict]] = defaultdict(list)
    for ax in pred:
        at = ax.get("axiom_type") or ""
        s_iri = ax.get("subject") or ax.get("term") or ""
        if s_iri:
            pred_index[(_norm(s_iri), at)].append(ax)
        s_lbl = ax.get("subject_label") or ax.get("term_label") or ""
        if s_lbl and _norm(s_lbl) != _norm(s_iri):
            pred_index[(_norm(s_lbl), at)].append(ax)

    pred_entity_names = _collect_pred_entity_names(pred)


    evaluation = []
    pred_used_ids = set()
    for g_ax in gold:
        v = _judge_one_axiom(g_ax, pred_index, class_align, prop_align,
                             pred_entity_names,
                             gold_label_map, pred_label_map,
                             used_pred_ids=pred_used_ids)
        evaluation.append(v)
        if v["status"] in ("tp", "mismatch") and v.get("pred_match"):
            pred_used_ids.add(v["pred_match"].get("id"))

    aligned_pred_subjects = set(class_align.values()) | set(prop_align.values())
    inv_class = {v: k for k, v in class_align.items()}
    inv_prop = {v: k for k, v in prop_align.items()}

    for p_ax in pred:
        p_id = p_ax.get("id", "?")

        if p_id in pred_used_ids:
            continue

        p_subj_iri = p_ax.get("subject") or p_ax.get("term") or ""
        p_subj_lbl = p_ax.get("subject_label") or p_ax.get("term_label") or ""

        canonical = None
        if p_subj_lbl and p_subj_lbl in aligned_pred_subjects:
            canonical = p_subj_lbl
        elif p_subj_iri and p_subj_iri in aligned_pred_subjects:
            canonical = p_subj_iri
        if canonical is None:
            # Subject not in alignment table — Layer 4 handles as FP_unaligned
            continue


        at = p_ax.get("axiom_type") or ""
        gold_counterpart = (inv_class.get(canonical) or inv_prop.get(canonical)
                            or "?")
        evaluation.append({
            "side": "pred",
            "axiom_id": p_id,
            "term": p_ax.get("term", ""),
            "term_type": p_ax.get("term_type", ""),
            "axiom_type": at,
            "dl": p_ax.get("dl", ""),
            "status": "fp",
            "reason": (f"pred {at} axiom on {canonical!r} not matched "
                       f"by any gold axiom on {gold_counterpart!r}"),
            "pred_match": p_ax,
        })

    by_combo = defaultdict(lambda: {x: 0 for x in STATUSES})
    by_tt = defaultdict(lambda: {x: 0 for x in STATUSES})
    overall = {x: 0 for x in STATUSES}
    for v in evaluation:
        key = (v["term_type"], v["axiom_type"])
        by_combo[key][v["status"]] += 1
        by_tt[v["term_type"]][v["status"]] += 1
        overall[v["status"]] += 1

    return {
        "evaluation": evaluation,
        "counts_by_combo": {k: dict(v) for k, v in by_combo.items()},
        "counts_by_term": {k: dict(v) for k, v in by_tt.items()},
        "counts_overall": overall,
        "pred_used_ids": pred_used_ids,
    }


def _prf1(tp: int, fp: int, fn: int) -> Tuple[float, float, float]:
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return p, r, f


def _format_layer3_table(layer3: dict) -> str:
    lines = []
    lines.append("Status: TP / FP / FN / Mismatch / Skip")
    lines.append("Mismatch counts as BOTH FP and FN "
                 "(FP and FN columns include mismatch).")
    lines.append("")
    header = (f"{'Type / AxiomType':<36}  {'TP':>4}  {'FP':>4}  {'FN':>4}  "
              f"{'Mis':>4}  {'Skp':>4}  {'P':>6}  {'R':>6}  {'F1':>6}")
    lines.append(header)
    lines.append("─" * len(header))

    for tt in _TERM_TYPE_ORDER:
        if tt not in layer3["counts_by_term"]:
            continue
        c = layer3["counts_by_term"][tt]
        if sum(c.values()) == 0:
            continue
        tp = c["tp"]; mm = c["mismatch"]
        fp = c["fp"] + mm; fn = c["fn"] + mm
        p, r, f = _prf1(tp, fp, fn)
        lines.append(f"{tt + ' axioms':<36}  {tp:>4}  {fp:>4}  {fn:>4}  "
                     f"{mm:>4}  {c['skip']:>4}  "
                     f"{p*100:>5.1f}%  {r*100:>5.1f}%  {f*100:>5.1f}%")
        ordered = _AXIOM_TYPES_BY_TERM_TYPE.get(tt, [])
        observed = sorted({k[1] for k in layer3["counts_by_combo"] if k[0] == tt})
        extras = [a for a in observed if a not in ordered]
        for at in ordered + extras:
            cc = layer3["counts_by_combo"].get((tt, at))
            if not cc or sum(cc.values()) == 0:
                continue
            tp = cc["tp"]; mm = cc["mismatch"]
            fp = cc["fp"] + mm; fn = cc["fn"] + mm
            p, r, f = _prf1(tp, fp, fn)
            lines.append(f"  {at:<34}  {tp:>4}  {fp:>4}  {fn:>4}  "
                         f"{mm:>4}  {cc['skip']:>4}  "
                         f"{p*100:>5.1f}%  {r*100:>5.1f}%  {f*100:>5.1f}%")

    lines.append("─" * len(header))
    o = layer3["counts_overall"]
    tp = o["tp"]; mm = o["mismatch"]
    fp = o["fp"] + mm; fn = o["fn"] + mm
    p, r, f = _prf1(tp, fp, fn)
    lines.append(f"{'Overall (all axioms)':<36}  {tp:>4}  {fp:>4}  {fn:>4}  "
                 f"{mm:>4}  {o['skip']:>4}  "
                 f"{p*100:>5.1f}%  {r*100:>5.1f}%  {f*100:>5.1f}%")
    return "\n".join(lines)


def _format_layer3_details(layer3: dict, max_rows: int = None) -> str:
    lines = []
    rows = layer3["evaluation"]
    if max_rows:
        rows = rows[:max_rows]
    type_order = {"Class": 0, "ObjectProperty": 1, "DatatypeProperty": 2}
    rows = sorted(rows, key=lambda v: (
        type_order.get(v["term_type"], 99), v["axiom_type"], v["axiom_id"],
    ))
    label = {"tp": " TP ", "fn": " FN ", "fp": " FP ",
             "mismatch": "MIS ", "skip": "SKIP"}
    for v in rows:
        dl = v["dl"]
        if len(dl) > 70:
            dl = dl[:67] + "..."
        lines.append(f"  [{label[v['status']]}] {v['axiom_id']:<6} {dl}")
        lines.append(f"           reason: {v['reason']}")
    return "\n".join(lines)


def _save_details_csv(layer3: dict, csv_path: str) -> None:

    status_label = {
        "tp": "TP",
        "fn": "FN",
        "fp": "FP",
        "mismatch": "Mismatch",
        "skip": "Skip",
    }
    fields = ["id", "source", "term_type", "axiom_type",
              "term", "dl", "status", "note"]

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()

        for v in layer3["evaluation"]:
            base_id = v["axiom_id"]
            status = status_label.get(v["status"], v["status"].upper())
            note = v.get("reason", "")
            pm = v.get("pred_match") or {}

            if v["status"] == "fp":
                # Pure-FP: pred-only — pred row first, gold row as placeholder
                w.writerow({
                    "id":         f"{base_id}-pred",
                    "source":     "pred",
                    "term_type":  v["term_type"],
                    "axiom_type": v["axiom_type"],
                    "term":       v["term"],
                    "dl":         v["dl"],
                    "status":     status,
                    "note":       note,
                })
                w.writerow({
                    "id":         f"{base_id}-gold",
                    "source":     "gold",
                    "term_type":  "-",
                    "axiom_type": "-",
                    "term":       "-",
                    "dl":         "(no gold counterpart)",
                    "status":     "-",
                    "note":       "-",
                })
            else:
                # Gold row first
                w.writerow({
                    "id":         f"{base_id}-gold",
                    "source":     "gold",
                    "term_type":  v["term_type"],
                    "axiom_type": v["axiom_type"],
                    "term":       v["term"],
                    "dl":         v["dl"],
                    "status":     status,
                    "note":       note,
                })
                # Pred row (filled if a match was found, else placeholder)
                if pm:
                    w.writerow({
                        "id":         f"{base_id}-pred",
                        "source":     "pred",
                        "term_type":  pm.get("term_type", ""),
                        "axiom_type": pm.get("axiom_type", ""),
                        "term":       pm.get("term", ""),
                        "dl":         pm.get("dl", ""),
                        "status":     "-",
                        "note":       "-",
                    })
                else:
                    placeholder = ("(subject not in alignment table)"
                                   if v["status"] == "skip"
                                   else "(no pred axiom on aligned subject)")
                    w.writerow({
                        "id":         f"{base_id}-pred",
                        "source":     "pred",
                        "term_type":  "-",
                        "axiom_type": "-",
                        "term":       "-",
                        "dl":         placeholder,
                        "status":     "-",
                        "note":       "-",
                    })


def compute_layer4(layer3, gold, pred, class_align, prop_align):
    aligned_gold_classes = set(class_align.keys())
    aligned_pred_classes = set(class_align.values())
    aligned_gold_props = set(prop_align.keys())
    aligned_pred_props = set(prop_align.values())

    def _is_aligned(ax: dict, side: str) -> bool:
        tt = ax.get("term_type")
        term_iri = ax.get("subject") or ax.get("term") or ""
        term_label = ax.get("subject_label") or ax.get("term_label") or ""
        if tt == "Class":
            target = (aligned_gold_classes if side == "gold"
                      else aligned_pred_classes)
        else:
            target = (aligned_gold_props if side == "gold"
                      else aligned_pred_props)
        return (term_iri and term_iri in target) or \
               (term_label and term_label in target)

    unaligned_gold = [ax for ax in gold if not _is_aligned(ax, "gold")]
    unaligned_pred = [ax for ax in pred if not _is_aligned(ax, "pred")]

    by_term_l3 = layer3["counts_by_term"]

    def _layer3_for(tt: str) -> dict:
        c = by_term_l3.get(tt, {x: 0 for x in STATUSES})
        tp = c["tp"]; mm = c["mismatch"]
        return {"tp": tp,
                "fp_layer3": c["fp"] + mm, "fn_layer3": c["fn"] + mm,
                "mismatch": mm, "skip": c["skip"]}

    per_term = {}
    for tt in _TERM_TYPE_ORDER:
        l3 = _layer3_for(tt)
        unaligned_g = [ax for ax in unaligned_gold if ax.get("term_type") == tt]
        unaligned_p = [ax for ax in unaligned_pred if ax.get("term_type") == tt]
        fp = l3["fp_layer3"] + len(unaligned_p)
        fn = l3["fn_layer3"] + len(unaligned_g)
        p, r, f = _prf1(l3["tp"], fp, fn)
        per_term[tt] = {
            "tp": l3["tp"],
            "fp": fp, "fp_layer3": l3["fp_layer3"],
            "fp_unaligned": len(unaligned_p),
            "fn": fn, "fn_layer3": l3["fn_layer3"],
            "fn_unaligned": len(unaligned_g),
            "mismatch": l3["mismatch"], "skip": l3["skip"],
            "precision": p, "recall": r, "f1": f,
            "unaligned_gold_axioms": unaligned_g,
            "unaligned_pred_axioms": unaligned_p,
        }

    tp = sum(per_term[tt]["tp"] for tt in per_term)
    fp = sum(per_term[tt]["fp"] for tt in per_term)
    fn = sum(per_term[tt]["fn"] for tt in per_term)
    p, r, f = _prf1(tp, fp, fn)
    grand = {"tp": tp, "fp": fp, "fn": fn,
             "precision": p, "recall": r, "f1": f}
    return {"per_term": per_term, "grand": grand, "layer3_ref": layer3}


def _format_layer4(layer4: dict) -> str:
    lines = []
    lines.append("Layer 3 evaluates only axioms whose subject is in the "
                 "alignment table.")
    lines.append("Layer 4 — Global Evaluation:")
    lines.append(" Evaluation extended to the full ontology domain")
    lines.append("TP: unchanged from Layer 3.")
    lines.append("FP: Layer-3 FP + axioms from unaligned pred subjects.")
    lines.append("FN: Layer-3 FN + axioms from unaligned gold subjects.")
    
    lines.append("")
    for tt in _TERM_TYPE_ORDER:
        if tt not in layer4["per_term"]:
            continue
        p = layer4["per_term"][tt]
        if (p["tp"] + p["fp"] + p["fn"]) == 0:
            continue
        lines.append(f"[{tt}]")
        lines.append(f"  P={p['precision']*100:.1f}%  R={p['recall']*100:.1f}%  "
                     f"F1={p['f1']*100:.1f}%")
        lines.append(f"  TP = {p['tp']}")
        lines.append(f"  FP = {p['fp']:<3}  (Layer-3 FP: {p['fp_layer3']}  +  "
                     f"unaligned pred axioms: {p['fp_unaligned']})")
        lines.append(f"  FN = {p['fn']:<3}  (Layer-3 FN: {p['fn_layer3']}  +  "
                     f"unaligned gold axioms: {p['fn_unaligned']})")
        if p["unaligned_gold_axioms"]:
            grouped = defaultdict(list)
            for ax in p["unaligned_gold_axioms"]:
                grouped[ax.get("term", "?")].append(ax)
            lines.append(f"  Unaligned gold terms ({len(grouped)} term(s), "
                         f"{sum(len(v) for v in grouped.values())} axioms — "
                         f"each counts as FN):")
            for t in sorted(grouped):
                for ax in grouped[t]:
                    dl = ax.get("dl", "")
                    lines.append(f"    - {t} :: [{ax.get('id','')}] "
                                 f"{ax.get('axiom_type','')}: {dl}")
        if p["unaligned_pred_axioms"]:
            grouped = defaultdict(list)
            for ax in p["unaligned_pred_axioms"]:
                grouped[ax.get("term", "?")].append(ax)
            lines.append(f"  Unaligned pred terms ({len(grouped)} term(s), "
                         f"{sum(len(v) for v in grouped.values())} axioms — "
                         f"each counts as FP):")
            for t in sorted(grouped):
                for ax in grouped[t]:
                    dl = ax.get("dl", "")
                    lines.append(f"    - {t} :: [{ax.get('id','')}] "
                                 f"{ax.get('axiom_type','')}: {dl}")
        lines.append("")
    g = layer4["grand"]
    lines.append("[Overall — global, all term types]")
    lines.append(f"  P={g['precision']*100:.1f}%  R={g['recall']*100:.1f}%  "
                 f"F1={g['f1']*100:.1f}%")
    lines.append(f"  TP = {g['tp']}")
    lines.append(f"  FP = {g['fp']}")
    lines.append(f"  FN = {g['fn']}")
    return "\n".join(lines)


# ============================================================================
# 6. CQ Coverage
# ============================================================================

def compute_cq_coverage(layer3, gold, cq_definitions):

    status_by_id = {v["axiom_id"]: v for v in layer3["evaluation"]
                    if v.get("side") == "gold"}
    cq_to_axioms = defaultdict(list)
    for ax in gold:
        for cq_id in ax.get("cq_numbers") or []:
            cq_to_axioms[cq_id].append(ax)

    if cq_definitions:
        cq_ids = [c["id"] for c in cq_definitions]
        cq_q = {c["id"]: c.get("question", "") for c in cq_definitions}
    else:
        cq_ids = sorted(cq_to_axioms.keys(), key=lambda x: (len(x), x))
        cq_q = {cq: "" for cq in cq_ids}

    per_cq = {}
    n_fully = 0
    n_any = 0
    sum_rate = 0.0
    n_with_axioms = 0
    for cq_id in cq_ids:
        axs = cq_to_axioms.get(cq_id, [])
        tp_ids = [ax["id"] for ax in axs
                  if status_by_id.get(ax["id"], {}).get("status") == "tp"]
        # Missing axioms = gold axioms of this CQ that did NOT get TP
        missing_axs = [ax for ax in axs
                       if status_by_id.get(ax["id"], {}).get("status") != "tp"]
        missing_ids = [ax["id"] for ax in missing_axs]
        missing_dls = [
            {"id": ax["id"],
             "dl": ax.get("dl", ""),
             "status": status_by_id.get(ax["id"], {}).get("status", "?")}
            for ax in missing_axs
        ]

        n_ax = len(axs)
        n_tp = len(tp_ids)
        is_fully = (n_ax > 0 and n_tp == n_ax)
        is_any = (n_tp > 0)
        rate = (n_tp / n_ax) if n_ax else 0.0

        if is_fully:
            n_fully += 1
        if is_any:
            n_any += 1
        if n_ax > 0:
            sum_rate += rate
            n_with_axioms += 1

        per_cq[cq_id] = {
            "question": cq_q.get(cq_id, ""),
            "n_axioms": n_ax,
            "n_tp": n_tp,
            "rate": rate,
            "fully_covered": is_fully,
            "any_covered": is_any,
            # Backward-compat: keep `covered` as the at-least-one flag
            "covered": is_any,
            "axiom_ids": [ax["id"] for ax in axs],
            "tp_axiom_ids": tp_ids,
            "missing_axiom_ids": missing_ids,
            "missing_axioms": missing_dls,
        }

    n_total = len(cq_ids)
    avg_rate = (sum_rate / n_with_axioms) if n_with_axioms else 0.0

    return {
        "per_cq": per_cq,
        "n_total": n_total,
        # Three views:
        "n_fully_covered": n_fully,
        "n_any_covered": n_any,
        "average_rate": avg_rate,
        "fully_coverage": (n_fully / n_total) if n_total else 0.0,
        "any_coverage":   (n_any / n_total) if n_total else 0.0,
        # Backward-compat aliases (older code reads these):
        "n_covered": n_any,
        "coverage":  (n_any / n_total) if n_total else 0.0,
    }


def _format_cq_coverage(cov: dict) -> str:
    lines = []
    lines.append("CQ Coverage Metrics:")
    lines.append("")
    lines.append(f"  Fully covered CQs       : "
                 f"{cov['n_fully_covered']}/{cov['n_total']} = "
                 f"{cov['fully_coverage']*100:.1f}%   "
                 f"(all gold axiom got TP)")
    lines.append(f"  At-least-one covered    : "
                 f"{cov['n_any_covered']}/{cov['n_total']} = "
                 f"{cov['any_coverage']*100:.1f}%   "
                 f"(at least one gold axiom got TP)")
    lines.append(f"  Average per-CQ coverage : "
                 f"{cov['average_rate']*100:.1f}%   "
                 f"(mean of TP/total per CQ)")
    lines.append("")
    lines.append("Per-CQ detail:")
    for cq_id, info in cov["per_cq"].items():
        if info["fully_covered"]:
            status = "fully"
        elif info["any_covered"]:
            status = "partial"
        else:
            status = "none"
        q = info["question"]
        if q and len(q) > 60:
            q = q[:57] + "..."
        lines.append(f"  {cq_id:<8} ({info['n_tp']}/{info['n_axioms']} TP, "
                     f"{info['rate']*100:.0f}%) → {status}")
        if q:
            lines.append(f"           {q}")
        if info["tp_axiom_ids"]:
            ids = ", ".join(info["tp_axiom_ids"])
            lines.append(f"           TP axioms: {ids}")
        if info["missing_axiom_ids"]:
            ids = ", ".join(info["missing_axiom_ids"])
            lines.append(f"           Missing axioms: {ids}")
    return "\n".join(lines)


_TT_LABEL = {
    "Class":            "Axioms about Classes",
    "ObjectProperty":   "Axioms about Object Properties",
    "DatatypeProperty": "Axioms about Datatype Properties",
}


def _tt_label(tt: str) -> str:
    return _TT_LABEL.get(tt, f"{tt} axioms")


def build_axioms_report_md(stats_g, stats_p, layer2, layer3, layer4,
                            cov, args,
                            gold_axioms=None, pred_axioms=None) -> str:
    gold_axioms = gold_axioms or []
    pred_axioms = pred_axioms or []
    L = []
    L.append("# Axiom-Level TBox Evaluation Report")
    L.append("")
    L.append("_Generated by `eval_axioms.py`_  ")
    L.append(f"_Gold: `{args.gold}` · Pred: `{args.pred}`_  ")
    L.append(f"_Class alignment: `{args.class_csv}` "
             f"· Property alignment: `{args.property_csv}`_")
    L.append("")
    L.append("This report evaluates the predicted ontology against the "
             "gold ontology **at the axiom level only**. Each row counts "
             "TBox axioms (e.g. `SubClassOf`, `Domain`, `Range`, …) "
             "grouped by which kind of term the axiom is about "
             "(a class, an object property, or a datatype property). ")
    L.append("")

    L.append("## Layer 1 — Axiom Counts")
    L.append("")
    L.append("Side-by-side counts of axioms by `(term_type, axiom_type)`. "
             "No matching, just descriptive statistics.")
    L.append("")
    L.append("| Axiom Distribution | Gold | Pred |")
    L.append("|---|---:|---:|")
    for tt in _TERM_TYPE_ORDER:
        g_total = stats_g["by_term_type"].get(tt, 0)
        p_total = stats_p["by_term_type"].get(tt, 0)
        if g_total == 0 and p_total == 0:
            continue
        L.append(f"| **{_tt_label(tt)}** | **{g_total}** | **{p_total}** |")
        ordered = _AXIOM_TYPES_BY_TERM_TYPE.get(tt, [])
        observed = set(stats_g["by_term_axiom"].get(tt, {}).keys()) \
                 | set(stats_p["by_term_axiom"].get(tt, {}).keys())
        extras = sorted(observed - set(ordered))
        for at in ordered + extras:
            g_n = stats_g["by_term_axiom"].get(tt, {}).get(at, 0)
            p_n = stats_p["by_term_axiom"].get(tt, {}).get(at, 0)
            if g_n == 0 and p_n == 0:
                continue
            L.append(f"| &nbsp;&nbsp;{at} | {g_n} | {p_n} |")
    L.append(f"| **TOTAL** | **{stats_g['total']}** | **{stats_p['total']}** |")
    L.append("")

    if layer2 is not None:
        L.append("## Layer 2 — Semantic Overview (diagnostic)")
        L.append("")
        L.append(f"Each axiom is rendered as a Description Logic string "
                 f"and embedded with **`{layer2['model']}`**. Axioms are "
                 f"paired one-to-one greedily by cosine similarity at "
                 f"threshold **{layer2['threshold']}**.")
    
        L.append("- `Matched` = embedding-level semantic candidate pair "
                 "(retrieval-style)")
        L.append("- `Precision/Recall/F1` here are retrieval metrics "
                 "(matched as TP-like, unmatched as FP/FN-like) — "
                 "they reflect how well the embeddings retrieve "
                 "candidates, not how correct the axioms are")
        L.append("- `Match rate` = matched / max(gold, pred), informational only")
        L.append("")
        L.append("| Type / Axiom type | Gold | Pred | Matched | Match rate | "
                 "Precision | Recall | F1 |")
        L.append("|---|---:|---:|---:|---:|---:|---:|---:|")
        for tt in _TERM_TYPE_ORDER:
            if tt not in layer2["per_term_type"]:
                continue
            ptt = layer2["per_term_type"][tt]
            if ptt["gold_count"] == 0 and ptt["pred_count"] == 0:
                continue
            L.append(f"| **{_tt_label(tt)}** | {ptt['gold_count']} | "
                     f"{ptt['pred_count']} | {ptt['matched']} | "
                     f"{ptt['match_rate']*100:.1f}% | "
                     f"{ptt['precision']*100:.1f}% | "
                     f"{ptt['recall']*100:.1f}% | "
                     f"{ptt['f1']*100:.1f}% |")
            ordered = _AXIOM_TYPES_BY_TERM_TYPE.get(tt, [])
            observed = sorted({k[1] for k in layer2["buckets"] if k[0] == tt})
            extras = [a for a in observed if a not in ordered]
            for at in ordered + extras:
                br = layer2["buckets"].get((tt, at))
                if not br or (br["gold_count"] == 0 and br["pred_count"] == 0):
                    continue
                L.append(f"| &nbsp;&nbsp;{at} | {br['gold_count']} | "
                         f"{br['pred_count']} | {br['matched']} | "
                         f"{br['match_rate']*100:.1f}% | "
                         f"{br['precision']*100:.1f}% | "
                         f"{br['recall']*100:.1f}% | "
                         f"{br['f1']*100:.1f}% |")
        o = layer2["overall"]
        L.append(f"| **Overall (one greedy pass)** | **{o['gold_count']}** | "
                 f"**{o['pred_count']}** | **{o['matched']}** | "
                 f"**{o['match_rate']*100:.1f}%** | "
                 f"**{o['precision']*100:.1f}%** | "
                 f"**{o['recall']*100:.1f}%** | "
                 f"**{o['f1']*100:.1f}%** |")
        L.append("")

        pairs = layer2["overall"].get("pairs", [])
        if pairs:
            L.append("### Layer 2 — Semantic candidate pairs")
            L.append("")
            L.append("Greedy 1-to-1 pairings above the cosine-similarity "
                     "threshold, sorted by similarity descending. These "
                     "are **candidate** semantic matches not strict "
                     "correctness matched. Two axioms paired here may "
                     "still disagree structurally (different cardinality, "
                     "different description logic expressions, etc.); see Layer 3 for the "
                     "strict comparison. Long DL strings are truncated.")
            L.append("")
            L.append("| # | Sim | Gold axiom | Pred axiom |")
            L.append("|---:|---:|---|---|")
            sorted_pairs = sorted(pairs, key=lambda p: -p[2])
            for idx, (g_ax, p_ax, sim) in enumerate(sorted_pairs, start=1):
                g_dl = (g_ax.get("dl") if isinstance(g_ax, dict) else "") or ""
                p_dl = (p_ax.get("dl") if isinstance(p_ax, dict) else "") or ""
                g_dl_e = g_dl.replace("|", "\\|")
                p_dl_e = p_dl.replace("|", "\\|")
                if len(g_dl_e) > 70:
                    g_dl_e = g_dl_e[:67] + "..."
                if len(p_dl_e) > 70:
                    p_dl_e = p_dl_e[:67] + "..."
                L.append(f"| {idx} | {sim:.3f} | `{g_dl_e}` | "
                         f"`{p_dl_e}` |")
            L.append("")

    L.append("## Layer 3 — Axiom Alignment Check")
    L.append("For each gold axiom, look up its subject in the class or "
             "property alignment table. If pred has the same kind of "
             "axiom on the corresponding pred subject, compare the "
             "object from description logic representation: class names go through the class "
             "alignment table, property names through the property "
             "alignment table, datatypes by normalized string equality. "
             "Complex expressions (Intersection, Union, ∃p.C, ∀p.C, "
             "cardinality, OneOf, …) are broken down and each part is "
             "compared the same way.")


    L.append("")
    L.append("**Classification definitions** (per gold axiom):")
    L.append("")
    L.append("- `TP` term is aligned AND pred has a matching axiom")
    L.append("- `FN` term is aligned BUT pred has no axiom of this type "
             "for the corresponding pred term")
    L.append("- `mismatch` term is aligned AND pred has an axiom of this "
             "type, but the rest of the axiom does not align (counts as "
             "**both** FP and FN)")
    L.append("- `skip` gold term is NOT in the alignment table, this "
             "axiom is excluded from Layer 3 metrics (Layer 4 picks "
             "these up)")
    L.append("")
    L.append("After scanning gold axioms, we scan pred axioms whose "
             "subject IS in the alignment table. If such a pred axiom "
             "wasn't matched to any gold axiom in the first pass, it "
             "counts as a **pure FP** in Layer 3 pred produced "
             "extra material on a term that gold also talks about. "
             "Pred axioms whose subject is NOT in the alignment table "
             "are not counted in Layer 3 at all; they're picked up by "
             "Layer 4 as `FP_unaligned`.")
    L.append("")
    L.append("Each pred axiom is matched to **at most one** gold axiom "
             "(strict 1-to-1). Once a pred axiom is consumed as TP or "
             "Mismatch, it cannot be reused, preventing TP inflation "
             "when several gold axioms share the same subject.")
    L.append("")
    L.append("**Metric formula** (mismatch is double-counted):")
    L.append("")
    L.append("```")
    L.append("FP_total = fp + mismatch       # pred-side errors")
    L.append("FN_total = fn + mismatch       # gold-side gaps")
    L.append("P = TP / (TP + FP_total)")
    L.append("R = TP / (TP + FN_total)")
    L.append("```")
    L.append("")
    L.append("_In the table below: `FP_total = fp + mismatch`, "
             "`FN_total = fn + mismatch` (mismatch is double-counted "
             "into both columns)._")
    L.append("")
    L.append("| Type / Axiom type | TP | FP_total | FN_total | mismatch | "
             "skip | Precision | Recall | F1 |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")

    def _fmt_prf(tp, fp, fn, p, r, f, bold=False):
        p_zero = (tp + fp) == 0
        r_zero = (tp + fn) == 0
        f_zero = p_zero or r_zero
        p_str = "—" if p_zero else f"{p*100:.1f}%"
        r_str = "—" if r_zero else f"{r*100:.1f}%"
        f_str = "—" if f_zero else f"{f*100:.1f}%"
        if bold:
            return f"**{p_str}**", f"**{r_str}**", f"**{f_str}**"
        return p_str, r_str, f_str

    for tt in _TERM_TYPE_ORDER:
        if tt not in layer3["counts_by_term"]:
            continue
        c = layer3["counts_by_term"][tt]
        if sum(c.values()) == 0:
            continue
        tp = c["tp"]
        mm = c["mismatch"]
        fp = c["fp"] + mm
        fn = c["fn"] + mm
        p, r, f = _prf1(tp, fp, fn)
        p_s, r_s, f_s = _fmt_prf(tp, fp, fn, p, r, f, bold=True)
        L.append(f"| **{_tt_label(tt)}** | **{tp}** | **{fp}** | **{fn}** | "
                 f"{mm} | {c['skip']} | {p_s} | {r_s} | {f_s} |")
        ordered = _AXIOM_TYPES_BY_TERM_TYPE.get(tt, [])
        observed = sorted({k[1] for k in layer3["counts_by_combo"] if k[0] == tt})
        extras = [a for a in observed if a not in ordered]
        for at in ordered + extras:
            cc = layer3["counts_by_combo"].get((tt, at))
            if not cc or sum(cc.values()) == 0:
                continue
            tp = cc["tp"]
            mm = cc["mismatch"]
            fp = cc["fp"] + mm
            fn = cc["fn"] + mm
            p, r, f = _prf1(tp, fp, fn)
            p_s, r_s, f_s = _fmt_prf(tp, fp, fn, p, r, f)
            L.append(f"| &nbsp;&nbsp;{at} | {tp} | {fp} | {fn} | "
                     f"{mm} | {cc['skip']} | {p_s} | {r_s} | {f_s} |")
    o = layer3["counts_overall"]
    tp = o["tp"]
    mm = o["mismatch"]
    fp = o["fp"] + mm
    fn = o["fn"] + mm
    p, r, f = _prf1(tp, fp, fn)
    p_s, r_s, f_s = _fmt_prf(tp, fp, fn, p, r, f, bold=True)
    L.append(f"| **Overall (all axioms)** | **{tp}** | **{fp}** | **{fn}** | "
             f"{mm} | {o['skip']} | {p_s} | {r_s} | {f_s} |")
    L.append("")

    tps = [v for v in layer3["evaluation"] if v["status"] == "tp"]
    mismatches = [v for v in layer3["evaluation"]
                   if v["status"] == "mismatch"]
    fns = [v for v in layer3["evaluation"] if v["status"] == "fn"]
    fps = [v for v in layer3["evaluation"] if v["status"] == "fp"]
    skips = [v for v in layer3["evaluation"]
                     if v["status"] == "skip"]

    if tps:
        L.append("### Layer 3 — TP pairs (matched)")
        L.append("")
        L.append("Gold axioms that found a structurally-matching pred "
                 "axiom under the alignment tables.")
        L.append("")
        L.append("| Gold id | Term | Axiom type | Gold axiom | Pred axiom |")
        L.append("|---|---|---|---|---|")
        for v in tps:
            pm = v.get("pred_match") or {}
            g_dl = (v.get("dl") or "").replace("|", "\\|")
            p_dl = (pm.get("dl") or "").replace("|", "\\|")
            if len(g_dl) > 60: g_dl = g_dl[:57] + "..."
            if len(p_dl) > 60: p_dl = p_dl[:57] + "..."
            L.append(f"| {v.get('axiom_id', '')} | "
                     f"`{v.get('term', '')}` | "
                     f"{v.get('axiom_type', '')} | "
                     f"`{g_dl}` | `{p_dl}` |")
        L.append("")

    if mismatches:
        L.append("### Layer 3 — Mismatch pairs (counted as both FP and FN)")
        L.append("")
        L.append("Gold axioms whose term is in the alignment table and "
                 "pred has the same kind of axiom on the corresponding "
                 "pred term, but the description logic expression parts after the term do not align. The `Reason` "
                 "column shows why structural comparison failed.")
        L.append("")
        L.append("| Gold id | Term | Axiom type | Gold axiom | "
                 "Pred axiom | Reason |")
        L.append("|---|---|---|---|---|---|")
        for v in mismatches:
            pm = v.get("pred_match") or {}
            g_dl = (v.get("dl") or "").replace("|", "\\|")
            p_dl = (pm.get("dl") or "").replace("|", "\\|")
            reason = (v.get("reason") or "").replace("|", "\\|")
            if len(g_dl) > 50: g_dl = g_dl[:47] + "..."
            if len(p_dl) > 50: p_dl = p_dl[:47] + "..."
            if len(reason) > 60: reason = reason[:57] + "..."
            L.append(f"| {v.get('axiom_id', '')} | "
                     f"`{v.get('term', '')}` | "
                     f"{v.get('axiom_type', '')} | "
                     f"`{g_dl}` | `{p_dl}` | {reason} |")
        L.append("")

    if fns:
        L.append("### Layer 3 — FN (pred has no matching axiom)")
        L.append("")
        L.append("Gold axioms whose term is in the alignment table, but "
                 "pred has no axiom of the same `(term, axiom_type)` "
                 "combination. Counts as FN.")
        L.append("")
        L.append("| Gold id | Term | Axiom type | Gold axiom | Pred match |")
        L.append("|---|---|---|---|---|")
        for v in fns:
            g_dl = (v.get("dl") or "").replace("|", "\\|")
            reason = (v.get("reason") or "").replace("|", "\\|")
            if len(g_dl) > 60: g_dl = g_dl[:57] + "..."
            if len(reason) > 60: reason = reason[:57] + "..."
            L.append(f"| {v.get('axiom_id', '')} | "
                     f"`{v.get('term', '')}` | "
                     f"{v.get('axiom_type', '')} | "
                     f"`{g_dl}` | — ({reason}) |")
        L.append("")

    if fps:
        L.append("### Layer 3 — Pure FP (pred axiom with no gold counterpart)")
        L.append("")
        L.append("Pred axioms whose term is in the alignment table on the "
                 "pred side, but gold has no axiom of the same "
                 "`(term, axiom_type)` combination. Detected by the "
                 "pred-side scan that runs after the main gold-driven "
                 "loop. Counts as FP.")
        L.append("")
        L.append("| Pred id | Pred term | Axiom type | Pred axiom | "
                 "Gold match |")
        L.append("|---|---|---|---|---|")
        for v in fps:
            pm = v.get("pred_match") or {}
            p_dl = (pm.get("dl") or v.get("dl") or "").replace("|", "\\|")
            reason = (v.get("reason") or "").replace("|", "\\|")
            if len(p_dl) > 60: p_dl = p_dl[:57] + "..."
            if len(reason) > 60: reason = reason[:57] + "..."
            L.append(f"| {v.get('axiom_id', '')} | "
                     f"`{v.get('term', '')}` | "
                     f"{v.get('axiom_type', '')} | "
                     f"`{p_dl}` | — ({reason}) |")
        L.append("")

    if skips:
        from collections import defaultdict as _dd
        grouped_skip = _dd(list)
        for v in skips:
            grouped_skip[v.get("term", "?")].append(v)
        n_terms = len(grouped_skip)
        n_axs = len(skips)
        L.append(f"### Layer 3 — Skip (gold term not in alignment table)")
        L.append("")
        L.append(f"Gold axioms whose term is **not** in the alignment "
                 f"table at all. They never enter the comparison and "
                 f"are not counted as TP/FP/FN/mismatch — they are simply "
                 f"set aside. ({n_terms} term(s), {n_axs} axiom(s).) "
                 f"Layer 4 below adds these axioms back as FN to give a "
                 f"global-denominator view.")
        L.append("")
        L.append("| Gold term | Axiom id | Axiom type | Gold axiom |")
        L.append("|---|---|---|---|")
        for term in sorted(grouped_skip):
            for v in grouped_skip[term]:
                g_dl = (v.get("dl") or "").replace("|", "\\|")
                if len(g_dl) > 60: g_dl = g_dl[:57] + "..."
                L.append(f"| `{term}` | {v.get('axiom_id', '')} | "
                         f"{v.get('axiom_type', '')} | `{g_dl}` |")
        L.append("")


    pred_unaligned_per_tt = {}
    for tt in _TERM_TYPE_ORDER:
        info = layer4["per_term"].get(tt, {})
        for ax in info.get("unaligned_pred_axioms", []):
            pred_unaligned_per_tt.setdefault(tt, []).append(ax)

    total_pred_unaligned = sum(len(v) for v in pred_unaligned_per_tt.values())
    if total_pred_unaligned > 0:
        from collections import defaultdict as _dd
        grouped_pu = _dd(list)
        for tt, axs in pred_unaligned_per_tt.items():
            for ax in axs:
                grouped_pu[ax.get("term", "?")].append(ax)
        n_terms_pu = len(grouped_pu)
        L.append("### Layer 3 — Pred-side unaligned "
                 "(pred term not in alignment table)")
        L.append("")
        L.append(f"Pred axioms whose term is **not** in the alignment "
                 f"table at all (the symmetric counterpart to the Skip "
                 f"table above, but on the pred side). They never reach "
                 f"the comparison loop. ({n_terms_pu} term(s), "
                 f"{total_pred_unaligned} axiom(s).) Layer 4 below adds "
                 f"these as FP to the global denominator.")
        L.append("")
        L.append("| Pred term | Axiom id | Axiom type | Pred axiom |")
        L.append("|---|---|---|---|")
        for term in sorted(grouped_pu):
            for ax in grouped_pu[term]:
                p_dl = (ax.get("dl") or "").replace("|", "\\|")
                if len(p_dl) > 60: p_dl = p_dl[:57] + "..."
                L.append(f"| `{term}` | {ax.get('id', '')} | "
                         f"{ax.get('axiom_type', '')} | `{p_dl}` |")
        L.append("")

    L.append("## Layer 4 — Overall overview")
    L.append("")
    L.append("Layer 3's denominator is only axioms whose term is in the "
             "alignment table. Layer 4 reuses Layer 3's TP unchanged but "
             "expands the denominator to **all** axioms in the ontology: "
             "Layer-3 skip rows are now FN, and pred axioms whose term "
             "isn't in the alignment table are now FP. The detailed lists "
             "of which axioms moved into FN / FP this way are shown in "
             "the Layer 3 `Skip` table above and in pred's unaligned "
             "axioms (collected here only as counts).")
    L.append("")

    for tt in _TERM_TYPE_ORDER:
        if tt not in layer4["per_term"]:
            continue
        info = layer4["per_term"][tt]
        if (info["tp"] + info["fp"] + info["fn"]) == 0:
            continue
        i_p_zero = (info["tp"] + info["fp"]) == 0
        i_r_zero = (info["tp"] + info["fn"]) == 0
        i_f_zero = i_p_zero or i_r_zero
        i_p_str = "—" if i_p_zero else f"{info['precision']*100:.1f}%"
        i_r_str = "—" if i_r_zero else f"{info['recall']*100:.1f}%"
        i_f_str = "—" if i_f_zero else f"{info['f1']*100:.1f}%"
        L.append(f"### {_tt_label(tt)}")
        L.append("")
        L.append("| Metric | Value | Detail |")
        L.append("|---|---:|---|")
        L.append(f"| Precision | {i_p_str} | |")
        L.append(f"| Recall | {i_r_str} | |")
        L.append(f"| F1 | {i_f_str} | |")
        L.append(f"| TP | {info['tp']} | |")
        L.append(f"| FP | {info['fp']} | "
                 f"Layer-3 FP: {info['fp_layer3']} + unaligned pred "
                 f"axioms: {info['fp_unaligned']} |")
        L.append(f"| FN | {info['fn']} | "
                 f"Layer-3 FN: {info['fn_layer3']} + unaligned gold "
                 f"axioms: {info['fn_unaligned']} |")
        L.append("")

    g = layer4["grand"]
    g_p_zero = (g["tp"] + g["fp"]) == 0
    g_r_zero = (g["tp"] + g["fn"]) == 0
    g_f_zero = g_p_zero or g_r_zero
    g_p_str = "—" if g_p_zero else f"{g['precision']*100:.1f}%"
    g_r_str = "—" if g_r_zero else f"{g['recall']*100:.1f}%"
    g_f_str = "—" if g_f_zero else f"{g['f1']*100:.1f}%"
    L.append("### Grand Overall — Layer 4, all term types")
    L.append("")
    L.append("| Metric | Value |")
    L.append("|---|---:|")
    L.append(f"| Precision | **{g_p_str}** |")
    L.append(f"| Recall | **{g_r_str}** |")
    L.append(f"| F1 | **{g_f_str}** |")
    L.append(f"| TP | {g['tp']} |")
    L.append(f"| FP | {g['fp']} |")
    L.append(f"| FN | {g['fn']} |")
    L.append("")

    if cov is not None:
        L.append("## CQ Coverage (strict)")
        L.append("")
        L.append("For each gold CQ, count how many of its associated "
                 "gold axioms received a `TP` status in Layer 3.")
        L.append("")

        status_by_id = {v["axiom_id"]: v
                        for v in layer3["evaluation"]
                        if v.get("side") == "gold"}

        L.append("### Per-axiom Coverage Overview")
        L.append("")
        L.append("For each gold axiom that is tagged to a CQ, did it "
                 "receive a `TP` in Layer 3, and which gold CQs does it "
                 "belong to?")
        L.append("")

        rows = []
        for ax in gold_axioms:
            cq_nums = ax.get("cq_numbers") or []
            if not cq_nums:
                continue
            v = status_by_id.get(ax["id"], {})
            status = v.get("status", "?")
            pm = v.get("pred_match") or {}
            covered = (status == "tp")
            aligned_to = pm.get("dl", "") if covered else ""
            rows.append({
                "id": ax["id"],
                "dl": ax.get("dl", ""),
                "cq_ids": cq_nums,
                "covered": covered,
                "status": status,
                "aligned_to": aligned_to,
            })

        n_aligned = sum(1 for r in rows if r["covered"])
        L.append(f"**{n_aligned} / {len(rows)} gold axioms covered "
                 f"(TP) by some pred axiom.**")
        L.append("")
        L.append("| Axiom id | Gold axiom | CQs | Covered | Status | "
                 "Aligned to |")
        L.append("|---|---|---|:-:|---|---|")
        status_label = {
            "tp": "TP", "fn": "FN", "mismatch": "Mismatch",
            "skip": "Skip", "fp": "FP",
        }
        for r in rows:
            ok = "Y" if r["covered"] else "N"
            cqs = ", ".join(r["cq_ids"])
            v = status_label.get(r["status"],
                                  str(r["status"]).upper())
            g_dl = (r["dl"] or "").replace("|", "\\|")
            if len(g_dl) > 60:
                g_dl = g_dl[:57] + "..."
            p_dl = (r["aligned_to"] or "").replace("|", "\\|")
            if len(p_dl) > 60:
                p_dl = p_dl[:57] + "..."
            aligned_cell = f"`{p_dl}`" if p_dl else "``"
            L.append(f"| {r['id']} | `{g_dl}` | {cqs} | {ok} | "
                     f"{v} | {aligned_cell} |")
        L.append("")

        L.append("### Overall CQ coverage rate")
        L.append("")
        L.append("| View | Value | Meaning |")
        L.append("|---|---:|---|")
        L.append(f"| Covered CQs (partial counts) | "
                 f"**{cov['n_any_covered']}/{cov['n_total']} = "
                 f"{cov['any_coverage']*100:.1f}%** | "
                 f"CQs where at least one gold axiom got TP |")
        L.append(f"| Average per-CQ coverage | "
                 f"**{cov['average_rate']*100:.1f}%** | "
                 f"mean of each CQ's coverage % |")
        L.append(f"| Fully (100%) covered CQs | "
                 f"**{cov['n_fully_covered']}/{cov['n_total']} = "
                 f"{cov['fully_coverage']*100:.1f}%** | "
                 f"CQs where every gold axiom got TP |")
        L.append("")

        L.append("| CQ id | Question | TP / Total | Coverage | "
                 "Missing Gold Axioms |")
        L.append("|---|---|---:|---:|---|")
        for cq_id, info in cov["per_cq"].items():
            q = (info["question"] or "").replace("|", "\\|")
            missing = info.get("missing_axioms", [])
            if missing:
                miss_parts = []
                for m in missing:
                    v = status_label.get(m.get("status"),
                                          str(m.get("status")).upper())
                    miss_parts.append(f"{m.get('id', '')} ({v})")
                miss_str = ", ".join(miss_parts)
            else:
                miss_str = "—"
            rate_str = "—" if info['n_axioms'] == 0 else f"{info['rate']*100:.1f}%"
            L.append(f"| {cq_id} | {q} | "
                     f"{info['n_tp']} / {info['n_axioms']} | "
                     f"{rate_str} | {miss_str} |")
        L.append("")

        L.append("For hierarchy-level closure analysis and "
                 "possible closure rescue of missed simple hierarchy,"
                 "see the `eval_hermit.py` report.")
    
        L.append("")

    return "\n".join(L)


def append_axioms_report_to_md(report_text: str, output_path: str) -> None:

    axioms_marker = "# Axiom-Level TBox Evaluation Report"

    if not os.path.exists(output_path):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"\n[report] Note: '{output_path}' did not exist. "
              f"Created a new file containing ONLY the axiom-evaluation "
              f"report. To get a combined report, first run "
              f"concept_label_matching.py / eval_property.py / "
              f"eval_triple.py with --save_report_md pointing to the same file.",
              file=sys.stderr)
        return

    with open(output_path, "r", encoding="utf-8") as f:
        existing = f.read()

    if axioms_marker in existing:
        idx = existing.find(axioms_marker)
        prefix = existing[:idx].rstrip()
        if prefix.endswith("---"):
            prefix = prefix[:-3].rstrip()
        new_text = prefix + "\n\n---\n\n" + report_text
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"\n[report] Axiom-evaluation section already existed in "
              f"'{output_path}', replaced it with the new run.",
              file=sys.stderr)
        return

    if not existing.endswith("\n"):
        existing += "\n"
    new_text = existing + "\n---\n\n" + report_text
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_text)
    print(f"\n[report] Axiom-evaluation report appended to "
          f"'{output_path}'.", file=sys.stderr)


def save_cq_coverage_csv(cov: dict, csv_path: str) -> None:

    fields = ["cq_id", "covered", "fully_covered", "n_tp", "n_axioms",
              "rate", "tp_axiom_ids", "missing_axiom_ids"]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for cq_id, info in cov["per_cq"].items():
            w.writerow({
                "cq_id": cq_id,
                "covered": "true" if info["any_covered"] else "false",
                "fully_covered":
                    "true" if info["fully_covered"] else "false",
                "n_tp": info["n_tp"],
                "n_axioms": info["n_axioms"],
                "rate": f"{info['rate']:.4f}",
                "tp_axiom_ids": ";".join(info["tp_axiom_ids"]),
                "missing_axiom_ids":
                    ";".join(info.get("missing_axiom_ids", [])),
            })
    print(f"\nStrict CQ coverage CSV saved to: {csv_path}", file=sys.stderr)


def save_result_json(stats_g, stats_p, layer2, layer3, layer4, cov,
                     class_align, prop_align, args, path):

    config = {
        "gold_file": args.gold,
        "pred_file": args.pred,
        "class_csv": args.class_csv,
        "property_csv": args.property_csv,
        "layer2_threshold": args.threshold,
        "layer2_model": args.model,
        "layer2_skipped": bool(args.no_layer2),
    }

    def _compact_judgment(v):
        pm = v.get("pred_match")
        if pm and isinstance(pm, dict):
            pm_compact = {
                "id": pm.get("id", ""),
                "dl": pm.get("dl", ""),
                "axiom_type": pm.get("axiom_type", ""),
                "term": pm.get("term", ""),
            }
        else:
            pm_compact = None
        return {
            "side": v.get("side", "gold"),
            "axiom_id": v.get("axiom_id", ""),
            "term": v.get("term", ""),
            "term_type": v.get("term_type", ""),
            "axiom_type": v.get("axiom_type", ""),
            "dl": v.get("dl", ""),
            "status": v.get("status", ""),
            "reason": v.get("reason", ""),
            "pred_match": pm_compact,
        }

    layer3_out = {
        "evaluation": [_compact_judgment(v) for v in layer3["evaluation"]],
        "counts_overall": layer3["counts_overall"],
        "counts_by_term": layer3["counts_by_term"],
        "counts_by_combo": {
            f"{tt}|{at}": c
            for (tt, at), c in layer3["counts_by_combo"].items()
        },
    }


    layer4_out = {
        "per_term": {
            tt: {k: v for k, v in info.items()
                 if k not in ("unaligned_gold_axioms",
                              "unaligned_pred_axioms")}
            for tt, info in layer4["per_term"].items()
        },
        "grand": layer4["grand"],
    }

    layer4_out["unaligned_lists"] = {}
    for tt, info in layer4["per_term"].items():
        layer4_out["unaligned_lists"][tt] = {
            "gold": [{"id": ax.get("id", ""),
                      "term": ax.get("term", ""),
                      "axiom_type": ax.get("axiom_type", ""),
                      "dl": ax.get("dl", "")}
                     for ax in info.get("unaligned_gold_axioms", [])],
            "pred": [{"id": ax.get("id", ""),
                      "term": ax.get("term", ""),
                      "axiom_type": ax.get("axiom_type", ""),
                      "dl": ax.get("dl", "")}
                     for ax in info.get("unaligned_pred_axioms", [])],
        }

    results = {
        "layer1_stats_gold": stats_g,
        "layer1_stats_pred": stats_p,
        "layer3": layer3_out,
        "layer4": layer4_out,
        "alignments": {
            "class":    class_align,
            "property": prop_align,
        },
    }

    if layer2 is not None:

        l2_overall = layer2["overall"]
        l2_pairs_compact = [
            {"gold_id": g.get("id", ""), "gold_dl": g.get("dl", ""),
             "pred_id": p.get("id", ""), "pred_dl": p.get("dl", ""),
             "cosine": float(sim)}
            for g, p, sim in l2_overall.get("pairs", [])
        ]
        results["layer2"] = {
            "model": layer2["model"],
            "threshold": layer2["threshold"],
            "per_term_type": layer2["per_term_type"],
            "buckets": {f"{tt}|{at}": br
                        for (tt, at), br in layer2["buckets"].items()},
            "overall": {
                "gold_count": l2_overall["gold_count"],
                "pred_count": l2_overall["pred_count"],
                "matched": l2_overall["matched"],
                "match_rate": l2_overall["match_rate"],
                "precision": l2_overall["precision"],
                "recall": l2_overall["recall"],
                "f1": l2_overall["f1"],
                "pairs": l2_pairs_compact,
            },
        }

    if cov is not None:
        results["cq_coverage"] = {
            "per_cq": cov["per_cq"],
            "n_total": cov["n_total"],
            "n_fully_covered": cov["n_fully_covered"],
            "n_any_covered": cov["n_any_covered"],
            "fully_coverage": cov["fully_coverage"],
            "any_coverage": cov["any_coverage"],
            "average_rate": cov["average_rate"],
        }

    with open(path, "w", encoding="utf-8") as f:
        json.dump({"config": config, "results": results},
                  f, ensure_ascii=False, indent=2)
    print(f"\nResult JSON saved to: {path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--gold", required=True,
                        help="Gold axioms JSON")
    parser.add_argument("--pred", required=True,
                        help="Pred axioms JSON")
    parser.add_argument("--class_csv", default="best_matching.csv",
                        help="Class alignment CSV")
    parser.add_argument("--property_csv", default="property_best_matching.csv",
                        help="Property alignment CSV")
    parser.add_argument("--cq_csv", default=None,
                        help="(optional) CQ table CSV")
    parser.add_argument("--output", default=None,
                        help="Report output path (default: stdout)")
    parser.add_argument("--details_csv",
                        dest="details_csv", default=None,
                        help="(optional) Path for per-axiom comparison CSV "
                             "(2 rows per pair: gold + pred)")
    parser.add_argument("--pairs_csv", default=None,
                        help="(optional) Path for Layer-2 match-pairs CSV")
    parser.add_argument("--max_rows",
                        dest="max_rows", type=int, default=None,
                        help="Limit how many per-axiom comparisons are printed")
    parser.add_argument("--threshold", type=float, default=0.6,
                        help="Layer-2 cosine threshold (default 0.6)")
    parser.add_argument("--model", default="embeddinggemma",
                        help="Ollama embedding model (default 'embeddinggemma')")
    parser.add_argument("--ollama_url", default="http://localhost:11434",
                        help="Ollama base URL")
    parser.add_argument("--cache_path", default=".embed_cache.json",
                        help="Embedding disk cache (default .embed_cache.json)")
    parser.add_argument("--no_cache", action="store_true",
                        help="Disable embedding disk cache")
    parser.add_argument("--no_layer2", action="store_true",
                        help="Skip Layer 2 (Layer 1+3+4 only)")
    parser.add_argument("--gold_owl", default=None,
                        help="(optional) Gold OWL file. Used as a label "
                             "fallback when the gold JSON has no "
                             "'name_to_label' block. For HermiT-based "
                             "hierarchy evaluation, see eval_hermit.py "
                             "(separate script).")
    parser.add_argument("--pred_owl", default=None,
                        help="(optional) Pred OWL file. Same purpose as "
                             "--gold_owl.")
    parser.add_argument("--save_report_md", default=None,
                        help="Path to a Markdown file. If the file already "
                             "exists (from concept/property/triple scripts), "
                             "the axiom-evaluation report is appended after "
                             "those sections. Otherwise a new MD file is "
                             "created with only this report.")
    parser.add_argument("--save_cq_csv", default=None,
                        help="Path to save strict CQ coverage as CSV "
                             "(columns: cq_id, covered, n_tp, n_axioms, "
                             "tp_axiom_ids). Useful as input to "
                             "eval_hermit.py --strict_cq_csv so closure-"
                             "based CQ coverage knows which CQs were "
                             "already covered by strict matching.")
    parser.add_argument("--save_result_json", default=None,
                        help="Path to save the full result as JSON "
                             "(config + Layer 1-4 metrics + Layer-3 "
                             "evaluation + CQ coverage). Useful for "
                             "downstream programmatic checking.")
    

    parser.add_argument("--literal_relax",
                        choices=["yes", "no"], default="no",
                        help="If 'yes', a generic literal root in the "
                             "gold (rdfs:Literal / xsd:anySimpleType / "
                             "xsd:anyAtomicType) matches any concrete "
                             "xsd:* or rdf:* datatype in the prediction. "
                             "Default 'no' keeps strict equality.")
    args = parser.parse_args()


  
    LITERAL_RELAX = (args.literal_relax == "yes")
    print(f"[main] literal_relax = {args.literal_relax}", file=sys.stderr)

    print(f"Loading gold axioms from '{args.gold}'...", file=sys.stderr)
    gold = load_axioms(args.gold)
    print(f"  {len(gold)} gold axioms", file=sys.stderr)

    print(f"Loading pred axioms from '{args.pred}'...", file=sys.stderr)
    pred = load_axioms(args.pred)
    print(f"  {len(pred)} pred axioms", file=sys.stderr)

    print(f"Loading class alignment from '{args.class_csv}'...", file=sys.stderr)
    class_align = load_alignment_csv(args.class_csv)
    print(f"  {len(class_align)} class pairs", file=sys.stderr)

    print(f"Loading property alignment from '{args.property_csv}'...",
          file=sys.stderr)
    prop_align = load_alignment_csv(args.property_csv)
    print(f"  {len(prop_align)} property pairs", file=sys.stderr)

    gold_label_map = label_map_for(args.gold, gold)
    pred_label_map = label_map_for(args.pred, pred)

    if not gold_label_map and args.gold_owl:
        print(f"  [Gold JSON has no labels — reading from {args.gold_owl}]",
              file=sys.stderr)
        gold_label_map = label_map_from_owl(args.gold_owl)
        print(f"  Loaded {len(gold_label_map)} gold labels from OWL",
              file=sys.stderr)
    if not pred_label_map and args.pred_owl:
        print(f"  [Pred JSON has no labels — reading from {args.pred_owl}]",
              file=sys.stderr)
        pred_label_map = label_map_from_owl(args.pred_owl)
        print(f"  Loaded {len(pred_label_map)} pred labels from OWL",
              file=sys.stderr)
    if not gold_label_map:
        print("[warn] No gold labels available. Alignment will use IRI fragments only.",
              file=sys.stderr)
    if not pred_label_map:
        print("[warn] No pred labels available. Alignment will use IRI fragments only.",
              file=sys.stderr)

    def _enrich_axioms(axioms, label_map):
        for ax in axioms:
            subj = ax.get("subject") or ax.get("term") or ""
            term = ax.get("term") or ""
            if subj and "subject_label" not in ax:
                ax["subject_label"] = label_map.get(subj, subj)
            if term and "term_label" not in ax:
                ax["term_label"] = label_map.get(term, term)
    if gold_label_map:
        _enrich_axioms(gold, gold_label_map)
    if pred_label_map:
        _enrich_axioms(pred, pred_label_map)


    stats_g = compute_layer1(gold)
    stats_p = compute_layer1(pred)


    layer2 = None
    if not args.no_layer2:
        client = EmbeddingClient(
            model=args.model,
            base_url=args.ollama_url,
            cache_path=None if args.no_cache else args.cache_path,
            use_cache=not args.no_cache,
        )
        try:
            layer2 = compute_layer2(gold, pred, client, threshold=args.threshold)
        except Exception as e:
            print(f"[warn] Layer 2 failed: {e}\n"
                  f"       Producing Layer-1+3+4 report. "
                  f"Use --no_layer2 to suppress this attempt.",
                  file=sys.stderr)
            layer2 = None


    print("Computing Layer 3 (structural alignment)...", file=sys.stderr)
    layer3 = compute_layer3(gold, pred, class_align, prop_align,
                            gold_label_map, pred_label_map)


    print("Computing Layer 4 (global view)...", file=sys.stderr)
    layer4 = compute_layer4(layer3, gold, pred, class_align, prop_align)


    cq_defs = []
    try:
        cq_defs = load_cq_definitions(args.gold)
    except Exception:
        cq_defs = []
    if not cq_defs and args.cq_csv:
        try:
            with open(args.cq_csv, "r", encoding="utf-8", newline="") as f:
                for row in csv.DictReader(f):
                    cq_defs.append({
                        "id": row.get("ID") or row.get("id", ""),
                        "question": row.get("Question") or row.get("question", ""),
                    })
        except Exception as e:
            print(f"[warn] Could not load CQ CSV: {e}", file=sys.stderr)

    has_cqs_in_gold = any(ax.get("cq_numbers") for ax in gold)
    cov = compute_cq_coverage(layer3, gold, cq_defs) if has_cqs_in_gold else None

    out = []
    out.append("=" * 72)
    out.append("TBox Truth Evaluation")
    out.append("=" * 72)
    out.append("")
    out.append(f"Gold:  {args.gold}")
    out.append(f"Pred:  {args.pred}")
    out.append(f"Class alignments:    {len(class_align)}  (file: {args.class_csv})")
    out.append(f"Property alignments: {len(prop_align)}  (file: {args.property_csv})")
    out.append("")

    out.append("=" * 72)
    out.append("Layer 1 — Axiom Counts (statistics)")
    out.append("=" * 72)
    out.append("")
    out.append(_format_layer1_table(stats_g, stats_p))
    out.append("")

    if layer2 is not None:
        out.append("=" * 72)
        out.append("Layer 2 — Semantic Overview (DL-string cosine matching)")
        out.append("=" * 72)
        out.append("")
        out.append(_format_layer2_table(layer2))
        out.append("")
        if args.pairs_csv:
            _save_layer2_pairs_csv(layer2, args.pairs_csv)
            out.append(f"  → Match pairs CSV saved to: {args.pairs_csv}")
            out.append("")

    out.append("=" * 72)
    out.append("Layer 3 — Structural Alignment")
    out.append("=" * 72)
    out.append("")
    out.append(_format_layer3_table(layer3))
    out.append("")
    out.append("Per-axiom comparison detail:")
    out.append(_format_layer3_details(layer3, max_rows=args.max_rows))
    out.append("")
    if args.details_csv:
        _save_details_csv(layer3, args.details_csv)
        out.append(f"  → Per-axiom comparison CSV saved to: {args.details_csv}")
        out.append("")

    out.append("=" * 72)
    out.append("Layer 4 — Global View")
    out.append("=" * 72)
    out.append("")
    out.append(_format_layer4(layer4))
    out.append("")

    out.append("=" * 72)
    out.append("CQ Coverage (strict — based on Layer 3 TP)")
    out.append("=" * 72)
    out.append("")
    if cov is None:
        out.append("(Gold axioms do not carry 'cq_numbers'; skipping CQ coverage.)")
    else:
        out.append(_format_cq_coverage(cov))
    out.append("")

    text = "\n".join(out)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Report written to: {args.output}", file=sys.stderr)
    else:
        print(text)

    if args.save_report_md:
        report_text = build_axioms_report_md(
            stats_g, stats_p, layer2, layer3, layer4, cov, args,
            gold_axioms=gold, pred_axioms=pred)
        append_axioms_report_to_md(report_text, args.save_report_md)

    if args.save_cq_csv and cov is not None:
        save_cq_coverage_csv(cov, args.save_cq_csv)
    elif args.save_cq_csv and cov is None:
        print(f"\n[warn] --save_cq_csv requested but gold has no "
              f"cq_numbers; nothing to save.", file=sys.stderr)

    if args.save_result_json:
        save_result_json(stats_g, stats_p, layer2, layer3, layer4, cov,
                         class_align, prop_align, args,
                         args.save_result_json)


if __name__ == "__main__":
    main()
