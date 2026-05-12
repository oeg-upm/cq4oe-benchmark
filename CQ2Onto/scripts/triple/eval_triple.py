from __future__ import annotations


import argparse
import csv
import json
import os
import re
from dataclasses import dataclass
from typing import Optional

from langchain_ollama import OllamaEmbeddings
from rdflib import Graph, Literal, OWL, RDF, RDFS
from rdflib.term import BNode
from sentence_transformers import util


SEMANTIC_THRESHOLD = 0.6

_RDFLIB_FORMATS = [
    ("xml", {".owl", ".rdf", ".xml"}),
    ("turtle", {".ttl", ".turtle"}),
    ("nt", {".nt"}),
    ("n3", {".n3"}),
    ("json-ld", {".jsonld", ".json"}),
    ("trig", {".trig"}),
]


def split_camel_case(text: str) -> str:
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    text = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", text)
    return text


def normalize_text(text: Optional[str]) -> str:

    t = str(text or "").strip()
    t = split_camel_case(t)
    t = t.replace("_", " ").replace("-", " ")
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.lower().strip()


def normalize_datatype(dt: Optional[str]) -> Optional[str]:

    if dt is None:
        return None
    t = str(dt).strip()


    lower = t.lower()
    if t.count("xsd:") > 1 or ("#" in t and "xsd:" in lower):

        if t.count("xsd:") > 1:
            idx = lower.rfind("xsd:")
            t = t[idx:]

        elif "#" in t:
            t = t.rsplit("#", 1)[1]

    for prefix in (
        "http://www.w3.org/2001/XMLSchema#",
        "http://www.w3.org/2001/xmlschema#",
    ):
        if t.lower().startswith(prefix.lower()):
            t = t[len(prefix):]
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


@dataclass
class PropertyAxiom:

    predicate: str
    predicate_type: str
    domain_set: Optional[tuple]
    range_set: Optional[tuple]

    def shape(self) -> str:
        has_d = self.domain_set is not None
        has_r = self.range_set is not None
        if has_d and has_r:
            return "full"
        if has_d:
            return "domain_only"
        if has_r:
            return "range_only"
        return "undefined"

    def to_text(self) -> str:
        pred = normalize_text(self.predicate)
        dom = (
            " and ".join(normalize_text(d) for d in self.domain_set)
            if self.domain_set else None
        )
        rng = (
            " and ".join(normalize_text(r) for r in self.range_set)
            if self.range_set else None
        )
        if dom and rng:
            return f"{dom} {pred} {rng}"
        if dom:
            return f"{dom} {pred}"
        if rng:
            return f"{pred} {rng}"
        return pred


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


def _label_from_uri(uri_str: str) -> str:
    frag = uri_str.split("#")[-1] if "#" in uri_str else uri_str.rstrip("/").split("/")[-1]
    return frag.strip()


def _get_label(node, g: Graph) -> str:

    if node is None or isinstance(node, BNode):
        return ""

    labels = list(g.objects(node, RDFS.label))

    for lb in labels:
        if isinstance(lb, Literal) and getattr(lb, "language", None) == "en":
            text = str(lb).strip()
            if text:
                return text

    for lb in labels:
        if isinstance(lb, Literal) and getattr(lb, "language", None) in (None, ""):
            text = str(lb).strip()
            if text:
                return text

    for lb in labels:
        if isinstance(lb, Literal):
            text = str(lb).strip()
            if text:
                return text

    # 4. Final fallback: IRI local name
    iri_local = _label_from_uri(str(node))
    return iri_local if iri_local else ""


def _norm(text):

    if text is None:
        return ""

    s = str(text).strip()

    if "#" in s:
        s = s.split("#")[-1]
    elif "/" in s and ":" in s.split("/", 1)[0]:
        s = s.rstrip("/").split("/")[-1]

    s = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", s)

    s = s.lower()
    s = s.replace("_", " ").replace("-", " ")
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", "", s)
    return s



def _class_label(node, g: Graph) -> Optional[str]:
    if node is None or isinstance(node, BNode):
        return None
    label = _get_label(node, g)
    return label if label else None


def parse_property_axioms(file_path: str) -> list[PropertyAxiom]:
    g = _parse_graph(file_path)
    axioms: list[PropertyAxiom] = []
    seen: set = set()

    type_map = {
        OWL.ObjectProperty: "ObjectProperty",
        OWL.DatatypeProperty: "DatatypeProperty",
    }

    for owl_type, prop_type_name in type_map.items():
        for prop_uri in g.subjects(RDF.type, owl_type):
            if isinstance(prop_uri, BNode):
                continue
            label = _get_label(prop_uri, g)
            if not label:
                continue

            domains = list(g.objects(prop_uri, RDFS.domain))
            ranges = list(g.objects(prop_uri, RDFS.range))

            dom_classes: list[str] = []
            for d in domains:
                dc = _class_label(d, g)
                if dc:
                    dom_classes.append(dc)

            rng_values: list[str] = []
            for r in ranges:
                if prop_type_name == "ObjectProperty":
                    rv = _class_label(r, g)
                else:
                    rv = normalize_datatype(str(r))
                if rv:
                    rng_values.append(rv)

            domain_set = tuple(sorted(set(dom_classes))) if dom_classes else None
            range_set = tuple(sorted(set(rng_values))) if rng_values else None

            key = (label, prop_type_name)
            if key in seen:
                continue
            seen.add(key)

            axioms.append(PropertyAxiom(
                predicate=label,
                predicate_type=prop_type_name,
                domain_set=domain_set,
                range_set=range_set,
            ))

    return axioms

def _load_alignment_csv(csv_path: str, label: str) -> dict[str, dict]:
    if not csv_path or not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"{label} CSV not found: {csv_path!r}. "
            f"Run the upstream alignment step first."
        )

    out: dict[str, dict] = {}
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gold = (row.get("Gold_term") or row.get("gold_term") or "").strip()
            pred = (row.get("Pre_term") or row.get("Pred_term")
                    or row.get("pred_term") or "").strip()
            method = (row.get("Method") or row.get("matching_way") or "").strip()
            score_raw = (row.get("Score") or row.get("score") or "0").strip()
            try:
                score = float(score_raw) if score_raw else 0.0
            except ValueError:
                score = 0.0
            if not gold:
                continue
            out[gold] = {
                "pred": pred if pred else None,
                "method": method,
                "score": score,
            }

    matched = sum(1 for v in out.values() if v["pred"])
    print(f"  Loaded {label} from '{csv_path}': {matched}/{len(out)} aligned")
    return out


def load_class_alignment(csv_path: str) -> dict[str, set]:
    raw = _load_alignment_csv(csv_path, "class alignment")
    return {g: ({v["pred"]} if v["pred"] else set()) for g, v in raw.items()}


def load_property_alignment(csv_path: str) -> dict[str, str]:

    raw = _load_alignment_csv(csv_path, "property alignment")
    return {g: v["pred"] for g, v in raw.items() if v["pred"]}


def evaluate_layer1(
    gold_axioms: list[PropertyAxiom],
    pred_axioms: list[PropertyAxiom],
) -> dict:

    def _bucket(axioms):
        result = {
            "ObjectProperty":   {"full": 0, "domain_only": 0, "range_only": 0, "undefined": 0},
            "DatatypeProperty": {"full": 0, "domain_only": 0, "range_only": 0, "undefined": 0},
        }
        for ax in axioms:
            if ax.predicate_type in result:
                result[ax.predicate_type][ax.shape()] += 1
        return result

    gold_b = _bucket(gold_axioms)
    pred_b = _bucket(pred_axioms)

    def _totals(bucket):
        return {ptype: sum(bucket[ptype].values()) for ptype in bucket}

    return {
        "gold": gold_b,
        "pred": pred_b,
        "gold_totals": _totals(gold_b),
        "pred_totals": _totals(pred_b),
        "gold_grand_total": sum(_totals(gold_b).values()),
        "pred_grand_total": sum(_totals(pred_b).values()),
    }


def evaluate_layer2(
    gold_axioms: list[PropertyAxiom],
    pred_axioms: list[PropertyAxiom],
    model_id: str,
    threshold: float = SEMANTIC_THRESHOLD,
) -> dict:

    encoder = OllamaEmbeddings(model=model_id)

    def _eval_group(gold_group, pred_group):
        if not gold_group or not pred_group:
            return {
                "n_gold": len(gold_group),
                "n_pred": len(pred_group),
                "tp": 0, "fp": len(pred_group), "fn": len(gold_group),
                "precision": 0.0, "recall": 0.0, "f1": 0.0,
                "matches": [],
            }

        gold_texts = [ax.to_text() for ax in gold_group]
        pred_texts = [ax.to_text() for ax in pred_group]
        embeds = encoder.embed_documents(pred_texts + gold_texts)
        p_emb = embeds[:len(pred_group)]
        g_emb = embeds[len(pred_group):]

        cands = []
        for i in range(len(pred_group)):
            for j in range(len(gold_group)):
                s = float(util.cos_sim(p_emb[i], g_emb[j]).item())
                if s >= threshold:
                    cands.append((s, i, j))
        cands.sort(key=lambda x: x[0], reverse=True)

        used_p, used_g = set(), set()
        matches = []
        for s, i, j in cands:
            if i in used_p or j in used_g:
                continue
            used_p.add(i)
            used_g.add(j)
            matches.append({
                "gold_predicate": gold_group[j].predicate,
                "pred_predicate": pred_group[i].predicate,
                "gold_text": gold_texts[j],
                "pred_text": pred_texts[i],
                "score": round(s, 4),
            })

        tp = len(matches)
        fp = len(pred_group) - tp
        fn = len(gold_group) - tp
        p = tp / (tp + fp) if (tp + fp) else 0.0
        r = tp / (tp + fn) if (tp + fn) else 0.0
        f = 2 * p * r / (p + r) if (p + r) else 0.0
        return {
            "n_gold": len(gold_group),
            "n_pred": len(pred_group),
            "tp": tp, "fp": fp, "fn": fn,
            "precision": round(p, 4), "recall": round(r, 4), "f1": round(f, 4),
            "matches": matches,
        }

    by_type = {}
    for ptype in ("ObjectProperty", "DatatypeProperty"):
        gg = [a for a in gold_axioms if a.predicate_type == ptype]
        pp = [a for a in pred_axioms if a.predicate_type == ptype]
        by_type[ptype] = _eval_group(gg, pp)

    tp = sum(by_type[t]["tp"] for t in by_type)
    fp = sum(by_type[t]["fp"] for t in by_type)
    fn = sum(by_type[t]["fn"] for t in by_type)
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    overall = {
        "n_gold": sum(by_type[t]["n_gold"] for t in by_type),
        "n_pred": sum(by_type[t]["n_pred"] for t in by_type),
        "tp": tp, "fp": fp, "fn": fn,
        "precision": round(p, 4), "recall": round(r, 4), "f1": round(f, 4),
    }

    return {
        "threshold": threshold,
        "model_id": model_id,
        "overall": overall,
        "ObjectProperty": by_type["ObjectProperty"],
        "DatatypeProperty": by_type["DatatypeProperty"],
    }

def _judge_class_set(
    gold_set: Optional[tuple], pred_set: Optional[tuple],
    class_g2p: dict[str, set],
) -> str:

    if gold_set is None and pred_set is None:
        return "skip"
    if gold_set is None and pred_set is not None:
        return "fp"
    if gold_set is not None and pred_set is None:
        return "fn"

    class_g2p_norm = {
        _norm(g): {_norm(p) for p in preds}
        for g, preds in class_g2p.items()
    }
    pred_norm = {_norm(p) for p in pred_set}

    used_p: set = set()
    for gv in gold_set:
        allowed = class_g2p_norm.get(_norm(gv), set())
        found = None
        for pv in pred_norm:
            if pv in used_p:
                continue
            if pv in allowed:
                found = pv
                break
        if found is None:
            return "mismatch"
        used_p.add(found)

    if used_p != pred_norm:
        return "mismatch"
    return "tp"


#expand the soft verion for Literals with string, int...
def _is_literal_root(norm_dt: Optional[str]) -> bool:
    """Return True if a normalized datatype string refers to a generic
    'any literal' root (rdfs:Literal / xsd:anySimpleType / xsd:anyAtomicType).

    normalize_datatype() force-prepends 'xsd:', so 'rdfs:Literal' becomes
    'xsd:rdfs:literal'; this helper covers both raw and normalized spellings.
    """
    if not norm_dt:
        return False
    t = norm_dt.lower().strip()
    return t in {
        "rdfs:literal", "xsd:literal",
        "xsd:anysimpletype", "xsd:anyatomictype",
        "xsd:rdfs:literal",
        "xsd:xsd:anysimpletype", "xsd:xsd:anyatomictype",
    }



# When True, _judge_datatype_set treats a generic literal root in the gold
# as compatible with any concrete xsd:* / rdf:* datatype in the prediction.
# Off by default; turn on with --literal_relax yes.
LITERAL_RELAX = False



def _judge_datatype_set(
    gold_set: Optional[tuple], pred_set: Optional[tuple],
) -> str:

    if gold_set is None and pred_set is None:
        return "skip"
    if gold_set is None and pred_set is not None:
        return "fp"
    if gold_set is not None and pred_set is None:
        return "fn"
    g_norm = {normalize_datatype(x) for x in gold_set}
    p_norm = {normalize_datatype(x) for x in pred_set}
    if g_norm == p_norm:
        return "tp"

    # Relaxation (opt-in via --literal_relax yes): if the gold side is
    # a generic literal root, any non-empty set of concrete datatypes on
    # the prediction side is a sound specialization and is treated as TP.
    if (
        LITERAL_RELAX
        and len(g_norm) == 1
        and _is_literal_root(next(iter(g_norm)))
        and p_norm
        and not any(_is_literal_root(p) for p in p_norm)
    ):
        return "tp"

    return "mismatch"




def evaluate_layer3(
    gold_axioms: list[PropertyAxiom],
    pred_axioms: list[PropertyAxiom],
    prop_alignment: dict[str, str],
    class_g2p: dict[str, set],
) -> dict:
    by_gold = {_norm(ax.predicate): ax for ax in gold_axioms}
    by_pred = {_norm(ax.predicate): ax for ax in pred_axioms}

    pairs: list[dict] = []
    type_mismatches: list[dict] = []

    for g_pred, p_pred in prop_alignment.items():
        g_ax = by_gold.get(_norm(g_pred))
        p_ax = by_pred.get(_norm(p_pred))

        if g_ax is None and p_ax is None:
            continue

        if g_ax is None:
            ptype = p_ax.predicate_type
            domain_verdict = _judge_class_set(None, p_ax.domain_set, class_g2p)
            if ptype == "ObjectProperty":
                range_verdict = _judge_class_set(None, p_ax.range_set, class_g2p)
            else:
                range_verdict = _judge_datatype_set(None, p_ax.range_set)
            pairs.append({
                "predicate_type": ptype,
                "gold_predicate": g_pred,
                "pred_predicate": p_pred,
                "gold_type": None,
                "pred_type": ptype,
                "gold_domain": None,
                "pred_domain": list(p_ax.domain_set) if p_ax.domain_set else None,
                "gold_range": None,
                "pred_range": list(p_ax.range_set) if p_ax.range_set else None,
                "type_verdict": "fp",
                "domain_verdict": domain_verdict,
                "range_verdict": range_verdict,
                "is_full_match": False,
                "note": "gold side has no axiom for this aligned property",
            })
            continue
        if p_ax is None:
            ptype = g_ax.predicate_type
            domain_verdict = _judge_class_set(g_ax.domain_set, None, class_g2p)
            if ptype == "ObjectProperty":
                range_verdict = _judge_class_set(g_ax.range_set, None, class_g2p)
            else:
                range_verdict = _judge_datatype_set(g_ax.range_set, None)
            pairs.append({
                "predicate_type": ptype,
                "gold_predicate": g_pred,
                "pred_predicate": p_pred,
                "gold_type": ptype,
                "pred_type": None,
                "gold_domain": list(g_ax.domain_set) if g_ax.domain_set else None,
                "pred_domain": None,
                "gold_range": list(g_ax.range_set) if g_ax.range_set else None,
                "pred_range": None,
                "type_verdict": "fn",
                "domain_verdict": domain_verdict,
                "range_verdict": range_verdict,
                "is_full_match": False,
                "note": "pred side has no axiom for this aligned property",
            })
            continue

        if g_ax.predicate_type != p_ax.predicate_type:
            type_mismatches.append({
                "gold_predicate": g_pred, "gold_type": g_ax.predicate_type,
                "pred_predicate": p_pred, "pred_type": p_ax.predicate_type,
            })
            pairs.append({
                "predicate_type": g_ax.predicate_type,
                "gold_predicate": g_pred,
                "pred_predicate": p_pred,
                "gold_type": g_ax.predicate_type,
                "pred_type": p_ax.predicate_type,
                "gold_domain": list(g_ax.domain_set) if g_ax.domain_set else None,
                "pred_domain": list(p_ax.domain_set) if p_ax.domain_set else None,
                "gold_range": list(g_ax.range_set) if g_ax.range_set else None,
                "pred_range": list(p_ax.range_set) if p_ax.range_set else None,
                "type_verdict": "mismatch",
                "domain_verdict": "skip",
                "range_verdict": "skip",
                "is_full_match": False,
                "note": (f"predicate type differs: gold={g_ax.predicate_type}, "
                         f"pred={p_ax.predicate_type} — domain/range not "
                         f"evaluated"),
            })
            continue

        ptype = g_ax.predicate_type
        domain_verdict = _judge_class_set(g_ax.domain_set, p_ax.domain_set, class_g2p)
        if ptype == "ObjectProperty":
            range_verdict = _judge_class_set(g_ax.range_set, p_ax.range_set, class_g2p)
        else:
            range_verdict = _judge_datatype_set(g_ax.range_set, p_ax.range_set)

        full_match = (domain_verdict == "tp" and range_verdict == "tp")

        pairs.append({
            "predicate_type": ptype,
            "gold_predicate": g_pred,
            "pred_predicate": p_pred,
            "gold_type": ptype,
            "pred_type": ptype,
            "gold_domain": list(g_ax.domain_set) if g_ax.domain_set else None,
            "pred_domain": list(p_ax.domain_set) if p_ax.domain_set else None,
            "gold_range": list(g_ax.range_set) if g_ax.range_set else None,
            "pred_range": list(p_ax.range_set) if p_ax.range_set else None,
            "type_verdict": "tp",
            "domain_verdict": domain_verdict,
            "range_verdict": range_verdict,
            "is_full_match": full_match,
        })

    def _rollup(group):
        out_typ = {"tp": 0, "fp": 0, "fn": 0, "mismatch": 0, "skip": 0}
        out_dom = {"tp": 0, "fp": 0, "fn": 0, "mismatch": 0, "skip": 0}
        out_rng = {"tp": 0, "fp": 0, "fn": 0, "mismatch": 0, "skip": 0}
        for d in group:
            out_typ[d["type_verdict"]] += 1
            out_dom[d["domain_verdict"]] += 1
            out_rng[d["range_verdict"]] += 1
        return out_typ, out_dom, out_rng

    def _prf(d: dict) -> dict:
        tp = d["tp"]
        fp = d["fp"] + d["mismatch"]
        fn = d["fn"] + d["mismatch"]
        p = tp / (tp + fp) if (tp + fp) else 0.0
        r = tp / (tp + fn) if (tp + fn) else 0.0
        f = 2 * p * r / (p + r) if (p + r) else 0.0
        return {**d,
                "precision": round(p, 4),
                "recall": round(r, 4),
                "f1": round(f, 4)}

    def _combine(*counts):
        out = {"tp": 0, "fp": 0, "fn": 0, "mismatch": 0, "skip": 0}
        for c in counts:
            for k in out:
                out[k] += c[k]
        return out

    by_type = {}
    grand_typ = {"tp": 0, "fp": 0, "fn": 0, "mismatch": 0, "skip": 0}
    grand_dom = {"tp": 0, "fp": 0, "fn": 0, "mismatch": 0, "skip": 0}
    grand_rng = {"tp": 0, "fp": 0, "fn": 0, "mismatch": 0, "skip": 0}
    for ptype in ("ObjectProperty", "DatatypeProperty"):
        group = [p for p in pairs if p["predicate_type"] == ptype]
        typ_counts, dom_counts, rng_counts = _rollup(group)
        overall_counts = _combine(dom_counts, rng_counts)
        by_type[ptype] = {
            "n_aligned_pairs": len(group),
            "type":   _prf(typ_counts),
            "domain": _prf(dom_counts),
            "range":  _prf(rng_counts),
            "overall": _prf(overall_counts),
            "fully_aligned": [p for p in group if p["is_full_match"]],
        }
        for k in grand_dom:
            grand_typ[k] += typ_counts[k]
            grand_dom[k] += dom_counts[k]
            grand_rng[k] += rng_counts[k]

    grand_overall = _prf(_combine(grand_dom, grand_rng))
    grand_type_only   = _prf(grand_typ)
    grand_domain_only = _prf(grand_dom)
    grand_range_only  = _prf(grand_rng)

    return {
        "n_aligned_total": len(pairs),
        "ObjectProperty": by_type["ObjectProperty"],
        "DatatypeProperty": by_type["DatatypeProperty"],
        "grand_overall": grand_overall,
        "grand_type":    grand_type_only,
        "grand_domain":  grand_domain_only,
        "grand_range":   grand_range_only,
        "type_mismatches": type_mismatches,
        "all_pairs": pairs,
    }

def evaluate_layer4(
    gold_axioms: list[PropertyAxiom],
    pred_axioms: list[PropertyAxiom],
    prop_alignment: dict[str, str],
    layer3: dict,
) -> dict:

    aligned_gold_preds_norm = {_norm(k) for k in prop_alignment.keys()}
    aligned_pred_preds_norm = {_norm(v) for v in prop_alignment.values()}

    def _axioms_count(ax: PropertyAxiom) -> int:
        n = 0
        if ax.domain_set is not None:
            n += 1
        if ax.range_set is not None:
            n += 1
        return n

    types = ("ObjectProperty", "DatatypeProperty")
    unaligned_gold = {t: [] for t in types}
    unaligned_pred = {t: [] for t in types}

    for ax in gold_axioms:
        if _norm(ax.predicate) not in aligned_gold_preds_norm:
            unaligned_gold.setdefault(ax.predicate_type, []).append(ax)
    for ax in pred_axioms:
        if _norm(ax.predicate) not in aligned_pred_preds_norm:
            unaligned_pred.setdefault(ax.predicate_type, []).append(ax)

    def _layer3_raw(ptype):
        block = layer3[ptype]
        d = block["domain"]
        r = block["range"]
        return {
            "tp": d["tp"] + r["tp"],
            "fp": d["fp"] + r["fp"],
            "fn": d["fn"] + r["fn"],
            "mismatch": d["mismatch"] + r["mismatch"],
        }

    by_type = {}
    grand_matched = 0
    grand_extra_layer3 = 0
    grand_extra_unaligned = 0
    grand_missing_layer3 = 0
    grand_missing_unaligned = 0

    for ptype in types:
        layer3_raw = _layer3_raw(ptype)
        unaligned_gold_axiom_count = sum(_axioms_count(ax) for ax in unaligned_gold[ptype])
        unaligned_pred_axiom_count = sum(_axioms_count(ax) for ax in unaligned_pred[ptype])

        extra_layer3 = layer3_raw["fp"] + layer3_raw["mismatch"]
        extra_unaligned = unaligned_pred_axiom_count
        missing_layer3 = layer3_raw["fn"] + layer3_raw["mismatch"]
        missing_unaligned = unaligned_gold_axiom_count

        matched = layer3_raw["tp"]
        extra = extra_layer3 + extra_unaligned
        missing = missing_layer3 + missing_unaligned

        p = matched / (matched + extra) if (matched + extra) else 0.0
        r = matched / (matched + missing) if (matched + missing) else 0.0
        f = 2 * p * r / (p + r) if (p + r) else 0.0

        by_type[ptype] = {
            "matched": matched,
            "extra": extra,
            "extra_layer3": extra_layer3,
            "extra_unaligned": extra_unaligned,
            "missing": missing,
            "missing_layer3": missing_layer3,
            "missing_unaligned": missing_unaligned,
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f, 4),
            "unaligned_gold_count": len(unaligned_gold[ptype]),
            "unaligned_pred_count": len(unaligned_pred[ptype]),
            "unaligned_gold_axiom_count": unaligned_gold_axiom_count,
            "unaligned_pred_axiom_count": unaligned_pred_axiom_count,
            "unaligned_gold": [
                {
                    "predicate": ax.predicate,
                    "domain": list(ax.domain_set) if ax.domain_set else None,
                    "range": list(ax.range_set) if ax.range_set else None,
                    "axiom_count": _axioms_count(ax),
                }
                for ax in unaligned_gold[ptype]
            ],
            "unaligned_pred": [
                {
                    "predicate": ax.predicate,
                    "domain": list(ax.domain_set) if ax.domain_set else None,
                    "range": list(ax.range_set) if ax.range_set else None,
                    "axiom_count": _axioms_count(ax),
                }
                for ax in unaligned_pred[ptype]
            ],
        }

        grand_matched += matched
        grand_extra_layer3 += extra_layer3
        grand_extra_unaligned += extra_unaligned
        grand_missing_layer3 += missing_layer3
        grand_missing_unaligned += missing_unaligned

    grand_extra = grand_extra_layer3 + grand_extra_unaligned
    grand_missing = grand_missing_layer3 + grand_missing_unaligned
    p = grand_matched / (grand_matched + grand_extra) if (grand_matched + grand_extra) else 0.0
    r = grand_matched / (grand_matched + grand_missing) if (grand_matched + grand_missing) else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    grand = {
        "matched": grand_matched,
        "extra": grand_extra,
        "extra_layer3": grand_extra_layer3,
        "extra_unaligned": grand_extra_unaligned,
        "missing": grand_missing,
        "missing_layer3": grand_missing_layer3,
        "missing_unaligned": grand_missing_unaligned,
        "precision": round(p, 4),
        "recall": round(r, 4),
        "f1": round(f, 4),
    }

    return {
        "ObjectProperty": by_type["ObjectProperty"],
        "DatatypeProperty": by_type["DatatypeProperty"],
        "grand_overall": grand,
    }

def evaluate(
    pred_file: str, gold_file: str,
    class_csv: str, property_csv: str,
    model_id: str,
    threshold: float = SEMANTIC_THRESHOLD,
) -> dict:
    print("\n" + "=" * 60)
    print("THREE-LAYER PROPERTY-AXIOM EVALUATION")
    print("=" * 60)

    print("\n── Parsing ontologies ──")
    gold_axioms = parse_property_axioms(gold_file)
    pred_axioms = parse_property_axioms(pred_file)
    print(f"  Gold: {len(gold_axioms)} property axioms")
    print(f"  Pred: {len(pred_axioms)} property axioms")

    print("\n── Loading alignment tables ──")
    class_g2p = load_class_alignment(class_csv)
    prop_alignment = load_property_alignment(property_csv)

    print("\n── Layer 1: Statistics ──")
    layer1 = evaluate_layer1(gold_axioms, pred_axioms)

    print("\n── Layer 2: Semantic overview ──")
    layer2 = evaluate_layer2(gold_axioms, pred_axioms, model_id, threshold)
    print(f"  Overall  P={layer2['overall']['precision']:.3f}  "
          f"R={layer2['overall']['recall']:.3f}  "
          f"F1={layer2['overall']['f1']:.3f}")

    print("\n── Layer 3: Strict alignment ──")
    layer3 = evaluate_layer3(gold_axioms, pred_axioms, prop_alignment, class_g2p)
    print(f"  {layer3['n_aligned_total']} aligned pairs evaluated")

    print("\n── Layer 4: Global overview ──")
    layer4 = evaluate_layer4(gold_axioms, pred_axioms, prop_alignment, layer3)
    print(f"  Grand global  P={layer4['grand_overall']['precision']:.3f}  "
          f"R={layer4['grand_overall']['recall']:.3f}  "
          f"F1={layer4['grand_overall']['f1']:.3f}")

    return {
        "layer1_statistics": layer1,
        "layer2_semantic": layer2,
        "layer3_strict": layer3,
        "layer4_global": layer4,
        "config": {
            "semantic_threshold": threshold,
            "embedding_model": model_id,
            "class_csv": class_csv,
            "property_csv": property_csv,
        },
    }


def generate_report(result: dict, output_path: str):
    L: list[str] = []
    sep = "=" * 72
    sub = "─" * 72

    L.append(sep)
    L.append("THREE-LAYER PROPERTY-AXIOM EVALUATION REPORT")
    L.append(sep)
    L.append("")

    L1 = result["layer1_statistics"]
    L.append("LAYER 1 — Triple Statistics")
    L.append(sub)
    L.append("  Property counts by axiom shape, per property type.")
    L.append("    full         = both rdfs:domain and rdfs:range declared")
    L.append("    domain_only  = only rdfs:domain declared")
    L.append("    range_only   = only rdfs:range declared")
    L.append("    undefined    = neither declared")
    L.append("")

    header = (f"  {'':18s}  {'Full':>6s}  {'Dom-only':>9s}  "
              f"{'Rng-only':>9s}  {'Undef':>6s}  {'Total':>6s}")
    L.append(header)

    for side_label, side_key, totals_key in [("Gold", "gold", "gold_totals"),
                                              ("Pred", "pred", "pred_totals")]:
        L.append(f"  {side_label}:")
        for ptype in ("ObjectProperty", "DatatypeProperty"):
            b = L1[side_key][ptype]
            total = L1[totals_key][ptype]
            L.append(f"    {ptype:<16s}  "
                     f"{b['full']:>6d}  {b['domain_only']:>9d}  "
                     f"{b['range_only']:>9d}  {b['undefined']:>6d}  "
                     f"{total:>6d}")
        grand = L1[f"{side_key}_grand_total"]
        L.append(f"    {'TOTAL':<16s}  {'─':>6s}  {'─':>9s}  "
                 f"{'─':>9s}  {'─':>6s}  {grand:>6d}")
        L.append("")

    L2 = result["layer2_semantic"]
    L.append("LAYER 2 — Semantic Overview")
    L.append(sub)
    L.append("  Each property is represented as a normalized text string derived from its axioms.")
    L.append("  string and embedded; one-to-one greedy match by cosine.")
    L.append(f"  Threshold: {L2['threshold']}    Model: {L2['model_id']}")
    L.append("")
    L.append(f"  Standard precision/recall definitions are used.")
    L.append(f"  {'':22s}  {'P':>6s}  {'R':>6s}  {'F1':>6s}  "
             f"{'TP':>6s}  {'FP':>6s}  {'FN':>6s}  "
             f"{'gold':>5s}  {'pred':>5s}")
    for label, key in [("Overall", "overall"),
                        ("ObjectProperty", "ObjectProperty"),
                        ("DatatypeProperty", "DatatypeProperty")]:
        m = L2[key]
        L.append(f"  {label:<22s}  "
                 f"{m['precision']:>6.3f}  {m['recall']:>6.3f}  {m['f1']:>6.3f}  "
                 f"{m['tp']:>6d}  {m['fp']:>6d}  {m['fn']:>6d}  "
                 f"{m['n_gold']:>5d}  {m['n_pred']:>5d}")
    L.append("")
    for ptype in ("ObjectProperty", "DatatypeProperty"):
        m = L2[ptype]
        if not m["matches"]:
            continue
        L.append(f"  {ptype} aligned pairs (showing up to 10):")
        for pair in m["matches"][:10]:
            L.append(f"    [{pair['score']:.3f}]  "
                     f"gold:'{pair['gold_text']}'")
            L.append(f"            pred:'{pair['pred_text']}'")
        if len(m["matches"]) > 10:
            L.append(f"    ... {len(m['matches']) - 10} more")
        L.append("")

    L3 = result["layer3_strict"]
    L.append("LAYER 3 — Strict Alignment (via best-matching tables)")
    L.append(sub)
    L.append(f"  {L3['n_aligned_total']} property pairs from "
             f"property_best_matching.csv.")
    L.append("  Domain evaluated via class_best_matching.csv;")
    L.append("  Range evaluated via class_best_matching.csv (ObjectProperty)")
    L.append("  or normalized XSD equality (DatatypeProperty).")
    L.append("")
    L.append("  Evaluation criteria:")
    L.append("    skip      — gold None and pred None (nothing declared on either side)")
    L.append("    TP        — both declared and set-equal under the alignment table")
    L.append("    FP        — pred declared but gold did not")
    L.append("    FN        — gold declared but pred did not")
    L.append("    mismatch  — both declared but they disagree under the alignment table")
    L.append("                (mismatch contributes to both FP and FN)")
    L.append("")
    L.append("  Metric formula (mismatch counts as both FP and FN):")
    L.append("    FP_total = fp + mismatch       (pred-side errors)")
    L.append("    FN_total = fn + mismatch       (gold-side gaps)")
    L.append("    P  = TP / (TP + FP_total)")
    L.append("    R  = TP / (TP + FN_total)")
    L.append("")

    for ptype in ("ObjectProperty", "DatatypeProperty"):
        block = L3[ptype]
        n = block["n_aligned_pairs"]
        if n == 0:
            L.append(f"  [{ptype}]  no aligned pairs.")
            L.append("")
            continue
        d = block["domain"]
        r = block["range"]
        t = block["type"]
        ov = block["overall"]
        d_tp = d["tp"]
        d_fp = d["fp"] + d["mismatch"]
        d_fn = d["fn"] + d["mismatch"]
        r_tp = r["tp"]
        r_fp = r["fp"] + r["mismatch"]
        r_fn = r["fn"] + r["mismatch"]
        t_tp = t["tp"]
        t_fp = t["fp"] + t["mismatch"]
        t_fn = t["fn"] + t["mismatch"]
        o_tp = ov["tp"]
        o_fp = ov["fp"] + ov["mismatch"]
        o_fn = ov["fn"] + ov["mismatch"]

        L.append(f"  [{ptype}]  {n} aligned pair(s)")
        L.append(f"    Type     P={t['precision']:.3f}  R={t['recall']:.3f}  "
                 f"F1={t['f1']:.3f}  "
                 f"(TP={t_tp}, FP={t_fp}, FN={t_fn}; "
                 f"FP and FN include mismatch={t['mismatch']}; skip={t['skip']})")
        L.append(f"    Domain   P={d['precision']:.3f}  R={d['recall']:.3f}  "
                 f"F1={d['f1']:.3f}  "
                 f"(TP={d_tp}, FP={d_fp}, FN={d_fn}; "
                 f"FP and FN include mismatch={d['mismatch']}; skip={d['skip']})")
        L.append(f"    Range    P={r['precision']:.3f}  R={r['recall']:.3f}  "
                 f"F1={r['f1']:.3f}  "
                 f"(TP={r_tp}, FP={r_fp}, FN={r_fn}; "
                 f"FP and FN include mismatch={r['mismatch']}; skip={r['skip']})")
        L.append(f"    Overall  P={ov['precision']:.3f}  R={ov['recall']:.3f}  "
                 f"F1={ov['f1']:.3f}  "
                 f"(TP={o_tp}, FP={o_fp}, FN={o_fn}; "
                 f"type + domain + range judgments combined)")
        L.append("")

        L.append("    Per-pair detail:")
        for p in result["layer3_strict"]["all_pairs"]:
            if p["predicate_type"] != ptype:
                continue
            L.append(f"      gold:{p['gold_predicate']}  ↔  pred:{p['pred_predicate']}")
            L.append(f"        type    gold={p.get('gold_type')}  pred={p.get('pred_type')}  "
                     f"→ {p['type_verdict'].upper()}")
            L.append(f"        domain  gold={p['gold_domain']}  pred={p['pred_domain']}  "
                     f"→ {p['domain_verdict'].upper()}")
            L.append(f"        range   gold={p['gold_range']}   pred={p['pred_range']}   "
                     f"→ {p['range_verdict'].upper()}")
        L.append("")

        full = block["fully_aligned"]
        if full:
            L.append(f"    Fully aligned triples (domain TP and range TP) — "
                     f"{len(full)}:")
            for p in full:
                gtxt = (f"{p['gold_domain']} -[{p['gold_predicate']}]-> "
                        f"{p['gold_range']}")
                ptxt = (f"{p['pred_domain']} -[{p['pred_predicate']}]-> "
                        f"{p['pred_range']}")
                L.append(f"      gold: {gtxt}")
                L.append(f"      pred: {ptxt}")
        else:
            L.append("    No fully aligned triples.")
        L.append("")

    if L3["type_mismatches"]:
        L.append(f"  Type-mismatched alignments ({len(L3['type_mismatches'])}):")
        for tm in L3["type_mismatches"]:
            L.append(f"    gold:{tm['gold_predicate']} ({tm['gold_type']}) "
                     f"↔ pred:{tm['pred_predicate']} ({tm['pred_type']})")
        L.append("")

    # Grand Overall — all property types combined
    go = L3["grand_overall"]
    go_tp = go["tp"]
    go_fp = go["fp"] + go["mismatch"]
    go_fn = go["fn"] + go["mismatch"]
    L.append("  [Grand Overall — all property types, domain + range combined]")
    L.append(f"    P={go['precision']:.3f}  R={go['recall']:.3f}  "
             f"F1={go['f1']:.3f}  "
             f"(TP={go_tp}, FP={go_fp}, FN={go_fn}; "
             f"FP and FN include mismatch={go['mismatch']})")
    L.append("")

    L4 = result["layer4_global"]
    L.append("LAYER 4 — Global Overview")
    L.append(sub)
    L.append("  Layer 3 evaluates only properties already aligned by the upstream")
    L.append("  step. Layer 4 extends the evaluation to the full ontology:")
    L.append("    FP_global = Layer-3 FP + every domain/range axiom of every")
    L.append("                              UNALIGNED pred property")
    L.append("    FN_global = Layer-3 FN + every domain/range axiom of every")
    L.append("                              UNALIGNED gold property")
    L.append("  TP is unchanged. P / R / F1 reflect the whole ontology.")
    L.append("  (Layer-3 FP/FN already include mismatch — see Layer 3 above.)")
    L.append("")

    for ptype in ("ObjectProperty", "DatatypeProperty"):
        b = L4[ptype]
        L.append(f"  [{ptype}]")
        L.append(f"    P={b['precision']:.3f}  R={b['recall']:.3f}  F1={b['f1']:.3f}")
        L.append(f"    TP = {b['matched']}")
        L.append(f"    FP = {b['extra']:<3d}  "
                 f"(Layer-3 FP: {b['extra_layer3']}  +  "
                 f"unaligned pred axioms: {b['extra_unaligned']})")
        L.append(f"    FN = {b['missing']:<3d}  "
                 f"(Layer-3 FN: {b['missing_layer3']}  +  "
                 f"unaligned gold axioms: {b['missing_unaligned']})")
        L.append(f"    Unaligned gold properties: {b['unaligned_gold_count']} "
                 f"(contributing {b['unaligned_gold_axiom_count']} axioms to FN)")
        L.append(f"    Unaligned pred properties: {b['unaligned_pred_count']} "
                 f"(contributing {b['unaligned_pred_axiom_count']} axioms to FP)")

        if b["unaligned_gold"]:
            L.append("    Gold properties with no aligned pred (full axioms count as FN):")
            for u in b["unaligned_gold"]:
                L.append(f"      - {u['predicate']}: domain={u['domain']}  range={u['range']}  "
                         f"({u['axiom_count']} axiom{'s' if u['axiom_count'] != 1 else ''})")
        if b["unaligned_pred"]:
            L.append("    Pred properties with no aligned gold (full axioms count as FP):")
            for u in b["unaligned_pred"]:
                L.append(f"      - {u['predicate']}: domain={u['domain']}  range={u['range']}  "
                         f"({u['axiom_count']} axiom{'s' if u['axiom_count'] != 1 else ''})")
        L.append("")

    g = L4["grand_overall"]
    L.append("  [Grand Overall — global, all property types]")
    L.append(f"    P={g['precision']:.3f}  R={g['recall']:.3f}  F1={g['f1']:.3f}")
    L.append(f"    TP = {g['matched']}")
    L.append(f"    FP = {g['extra']:<3d}  "
             f"(Layer-3 FP: {g['extra_layer3']}  +  "
             f"unaligned pred axioms: {g['extra_unaligned']})")
    L.append(f"    FN = {g['missing']:<3d}  "
             f"(Layer-3 FN: {g['missing_layer3']}  +  "
             f"unaligned gold axioms: {g['missing_unaligned']})")
    L.append("")

    L.append(sep)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print(f"Readable report saved to: {output_path}")


def save_layer3_pairs_csv(result: dict, path: str):
    headers = [
        "PropertyType",
        "GoldPredicate", "PredPredicate",
        "GoldPredicateNorm", "PredPredicateNorm",
        "GoldType", "PredType", "TypeVerdict",
        "GoldDomain", "PredDomain",
        "GoldDomainNorm", "PredDomainNorm",
        "DomainStatus",
        "GoldRange", "PredRange",
        "GoldRangeNorm", "PredRangeNorm",
        "RangeStatus",
        "FullMatch", "Note",
    ]
    rows = []

    def _fmt(v):
        return "" if v is None else "; ".join(str(x) for x in v)

    def _fmt_norm(v):
        return "" if v is None else "; ".join(_norm(x) for x in v)

    for p in result["layer3_strict"]["all_pairs"]:
        rows.append({
            "PropertyType": p["predicate_type"],
            "GoldPredicate": p["gold_predicate"],
            "PredPredicate": p["pred_predicate"],
            "GoldPredicateNorm": _norm(p["gold_predicate"]),
            "PredPredicateNorm": _norm(p["pred_predicate"]),
            "GoldType":  p.get("gold_type") or "",
            "PredType":  p.get("pred_type") or "",
            "TypeVerdict": p.get("type_verdict", ""),
            "GoldDomain": _fmt(p["gold_domain"]),
            "PredDomain": _fmt(p["pred_domain"]),
            "GoldDomainNorm": _fmt_norm(p["gold_domain"]),
            "PredDomainNorm": _fmt_norm(p["pred_domain"]),
            "DomainStatus": p["domain_verdict"],
            "GoldRange": _fmt(p["gold_range"]),
            "PredRange": _fmt(p["pred_range"]),
            "GoldRangeNorm": _fmt_norm(p["gold_range"]),
            "PredRangeNorm": _fmt_norm(p["pred_range"]),
            "RangeStatus": p["range_verdict"],
            "FullMatch": "YES" if p["is_full_match"] else "NO",
            "Note": p.get("note", ""),
        })
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(rows)
    print(f"Layer-3 pairs CSV saved to: {path}")


def save_layer3_pairs_json(result: dict, path: str):
    out = []
    for i, p in enumerate(result["layer3_strict"]["all_pairs"], 1):
        out.append({
            "id": i,
            "property_type": p["predicate_type"],
            "gold_predicate": p["gold_predicate"],
            "pred_predicate": p["pred_predicate"],
            "gold_predicate_norm": _norm(p["gold_predicate"]),
            "pred_predicate_norm": _norm(p["pred_predicate"]),
            "gold_type": p.get("gold_type"),
            "pred_type": p.get("pred_type"),
            "type_verdict": p.get("type_verdict"),
            "gold_domain": p["gold_domain"],
            "pred_domain": p["pred_domain"],
            "gold_domain_norm": None if p["gold_domain"] is None else [_norm(x) for x in p["gold_domain"]],
            "pred_domain_norm": None if p["pred_domain"] is None else [_norm(x) for x in p["pred_domain"]],
            "domain_verdict": p["domain_verdict"],
            "gold_range": p["gold_range"],
            "pred_range": p["pred_range"],
            "gold_range_norm": None if p["gold_range"] is None else [_norm(x) for x in p["gold_range"]],
            "pred_range_norm": None if p["pred_range"] is None else [_norm(x) for x in p["pred_range"]],
            "range_verdict": p["range_verdict"],
            "is_full_match": p["is_full_match"],
            "note": p.get("note", ""),
        })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Layer-3 pairs JSON saved to: {path}")


def build_triple_report_md(result: dict) -> str:

    L = []
    L.append("# Property-Axiom (Triple) Evaluation Report")
    L.append("")
    L.append("_Generated by `eval_triple.py`_  ")
    cfg = result.get("config", {})
    L.append(f"_Embedding model: `{cfg.get('embedding_model', '?')}`, "
             f"semantic threshold: {cfg.get('semantic_threshold', '?')}_")
    L.append("")
    L.append("This report extends the property label-matching report by "
             "also evaluating each property's **domain** and **range** "
             "axioms. It has four layers, each with a different purpose.")
    L.append("")
    L.append("- **Layer 1, Triple Statistics:** counts only, describing "
             "what each ontology declares.")
    L.append("- **Layer 2, Semantic Overview:** for each property, build "
             "a textual representation from its axioms (e.g. "
             "`Wine madeFromGrape WineGrape`) and compare via embeddings.")
    L.append("- **Layer 3, Strict Alignment:** for property pairs the "
             "upstream alignment step matched, evaluate their domain and "
             "range under the class alignment table.")
    L.append("- **Layer 4, Global Overview:** put Layer-3 results on a "
             "complete-ontology denominator (also counting axioms of "
             "unaligned properties).")
    L.append("")

    L1 = result["layer1_statistics"]
    L.append("## Layer 1, Triple Statistics")
    L.append("")
    L.append("Counts of properties by axiom shape, per property type:")
    L.append("")
    L.append("- `full`, both rdfs:domain and rdfs:range declared")
    L.append("- `domain_only`, only rdfs:domain declared")
    L.append("- `range_only`, only rdfs:range declared")
    L.append("- `undefined`, neither declared")
    L.append("")
    for side_label, side_key, totals_key in [
        ("Gold", "gold", "gold_totals"),
        ("Pred", "pred", "pred_totals"),
    ]:
        L.append(f"**{side_label}**")
        L.append("")
        L.append("| Property type | full | domain_only | range_only | undefined | Total |")
        L.append("|---|---:|---:|---:|---:|---:|")
        for ptype in ("ObjectProperty", "DatatypeProperty"):
            b = L1[side_key][ptype]
            total = L1[totals_key][ptype]
            L.append(f"| {ptype} | {b['full']} | {b['domain_only']} | "
                     f"{b['range_only']} | {b['undefined']} | {total} |")
        grand = L1[f"{side_key}_grand_total"]
        L.append(f"| **TOTAL** | | | | | **{grand}** |")
        L.append("")

    L2 = result["layer2_semantic"]
    L.append("## Layer 2, Semantic Overview")
    L.append("")
    L.append(f"Each property's axioms are derived into a natural-"
             f"language string and embedded with the configured model. "
             f"Pairs are formed by one-to-one greedy match on cosine "
             f"similarity at threshold **{L2['threshold']}** "
             f"(model: `{L2['model_id']}`).")
    L.append("")
    L.append("- `TP` = gold property matched to a pred property")
    L.append("- `FP` = pred property with no matched gold")
    L.append("- `FN` = gold property with no matched pred")
    L.append("")
    L.append("| Scope | Precision | Recall | F1 | TP | FP | FN | Gold | Pred |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for label, key in [("Overall", "overall"),
                       ("ObjectProperty", "ObjectProperty"),
                       ("DatatypeProperty", "DatatypeProperty")]:
        m = L2[key]
        p_str = "—" if (m["tp"] + m["fp"]) == 0 else f"{m['precision']*100:.1f}%"
        r_str = "—" if (m["tp"] + m["fn"]) == 0 else f"{m['recall']*100:.1f}%"
        f_str = "—" if ((m["tp"] + m["fp"]) == 0 or (m["tp"] + m["fn"]) == 0) else f"{m['f1']*100:.1f}%"
        L.append(f"| {label} | {p_str} | {r_str} | {f_str} | "
                 f"{m['tp']} | {m['fp']} | {m['fn']} | "
                 f"{m['n_gold']} | {m['n_pred']} |")
    L.append("")

    for ptype in ("ObjectProperty", "DatatypeProperty"):
        m = L2[ptype]
        if not m.get("matches"):
            continue
        L.append(f"### {ptype}, semantic-aligned pairs (top 10)")
        L.append("")
        L.append("| Score | Gold text | Pred text |")
        L.append("|---:|---|---|")
        for pair in m["matches"][:10]:
            L.append(f"| {pair['score']:.3f} | "
                     f"`{pair['gold_text']}` | `{pair['pred_text']}` |")
        if len(m["matches"]) > 10:
            L.append("")
            L.append(f"_…and {len(m['matches']) - 10} more pairs._")
        L.append("")

    L3 = result["layer3_strict"]
    L.append("## Layer 3, Strict Alignment")
    L.append("")
    L.append(f"For the **{L3['n_aligned_total']}** property pairs that "
             f"the upstream alignment step matched (from "
             f"`property_best_matching.csv`), each pair's domain and "
             f"range are evaluated. ObjectProperty domain and range are "
             f"compared via the class alignment table "
             f"(`class_best_matching.csv`); DatatypeProperty range is "
             f"compared via normalized XSD-type equality.")
    L.append("")
    L.append("**Classification definitions** (per side, i.e. domain or range):")
    L.append("")
    L.append("- `skip`, both gold and pred declared **nothing** on this side")
    L.append("- `TP`, both declared and they agree under the alignment")
    L.append("- `FP`, pred declared something but gold did not")
    L.append("- `FN`, gold declared something but pred did not")
    L.append("- `mismatch`, both declared but they disagree (counts as **both** FP and FN)")
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

    for ptype in ("ObjectProperty", "DatatypeProperty"):
        block = L3[ptype]
        n = block["n_aligned_pairs"]
        if n == 0:
            L.append(f"### {ptype}")
            L.append("")
            L.append("_No aligned pairs._")
            L.append("")
            continue

        d = block["domain"]
        r = block["range"]
        t = block["type"]
        ov = block["overall"]
        d_fp = d["fp"] + d["mismatch"]
        d_fn = d["fn"] + d["mismatch"]
        r_fp = r["fp"] + r["mismatch"]
        r_fn = r["fn"] + r["mismatch"]
        t_fp = t["fp"] + t["mismatch"]
        t_fn = t["fn"] + t["mismatch"]
        o_fp = ov["fp"] + ov["mismatch"]
        o_fn = ov["fn"] + ov["mismatch"]

        L.append(f"### {ptype} ({n} aligned pair(s))")
        L.append("")
        L.append("Each aligned property pair is evaluated on **three "
                 "independent dimensions**: predicate `Type` (object vs "
                 "datatype), `Domain`, `Range`. A type-mismatch error is "
                 "counted only on the Type dimension; domain and range "
                 "are marked `skip` for those pairs (their semantic "
                 "spaces differ, so a fair comparison isn't possible).")
        L.append("")
        L.append("| Side | Precision | Recall | F1 | TP | FP | FN | mismatch | skip |")
        L.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")

        def _fmt_pct(value, denom_zero):
            """Show '—' when denominator is zero (no data on this
            axis), otherwise the percentage."""
            return "—" if denom_zero else f"{value*100:.1f}%"

        def _row_metrics(stat, fp_total, fn_total):
            p_zero = (stat["tp"] + fp_total) == 0
            r_zero = (stat["tp"] + fn_total) == 0
            f_zero = p_zero or r_zero
            return (_fmt_pct(stat["precision"], p_zero),
                    _fmt_pct(stat["recall"], r_zero),
                    _fmt_pct(stat["f1"], f_zero))

        t_p, t_r, t_f = _row_metrics(t, t_fp, t_fn)
        d_p, d_r, d_f = _row_metrics(d, d_fp, d_fn)
        r_p, r_r, r_f = _row_metrics(r, r_fp, r_fn)
        ov_p, ov_r, ov_f = _row_metrics(ov, o_fp, o_fn)

        L.append(f"| Type | {t_p} | {t_r} | {t_f} | "
                 f"{t['tp']} | {t_fp} | {t_fn} | "
                 f"{t['mismatch']} | {t['skip']} |")
        L.append(f"| Domain | {d_p} | {d_r} | {d_f} | "
                 f"{d['tp']} | {d_fp} | {d_fn} | "
                 f"{d['mismatch']} | {d['skip']} |")
        L.append(f"| Range | {r_p} | {r_r} | {r_f} | "
                 f"{r['tp']} | {r_fp} | {r_fn} | "
                 f"{r['mismatch']} | {r['skip']} |")
        L.append(f"| **Overall** | **{ov_p}** | **{ov_r}** | **{ov_f}** | "
                 f"**{ov['tp']}** | **{o_fp}** | **{o_fn}** | "
                 f"{ov['mismatch']} | {ov['skip']} |")
        L.append("")
        L.append("_`—` = undefined (denominator is 0)._")
        L.append("")

        pairs = [p for p in L3["all_pairs"] if p["predicate_type"] == ptype]
        if pairs:
            L.append(f"#### Per-pair detail ({ptype})")
            L.append("")
            L.append("| Gold predicate | Pred predicate | Type | "
                     "Gold domain | Pred domain | Domain | "
                     "Gold range | Pred range | Range |")
            L.append("|---|---|---|---|---|---|---|---|---|")
            for p in pairs:
                gd = ", ".join(p['gold_domain']) if p['gold_domain'] else "—"
                pd = ", ".join(p['pred_domain']) if p['pred_domain'] else "—"
                gr = ", ".join(p['gold_range']) if p['gold_range'] else "—"
                pr = ", ".join(p['pred_range']) if p['pred_range'] else "—"
                L.append(f"| `{p['gold_predicate']}` | "
                         f"`{p['pred_predicate']}` | "
                         f"**{p['type_verdict'].upper()}** | "
                         f"{gd} | {pd} | "
                         f"**{p['domain_verdict'].upper()}** | "
                         f"{gr} | {pr} | "
                         f"**{p['range_verdict'].upper()}** |")
            L.append("")

        full = block.get("fully_aligned", [])
        if full:
            L.append(f"#### Fully aligned triples ({len(full)})")
            L.append("")
            L.append("Triples where both domain AND range scored TP.")
            L.append("")
            L.append("| Side | Triple |")
            L.append("|---|---|")
            for p in full:
                gd = ", ".join(p['gold_domain']) if p['gold_domain'] else "—"
                gr = ", ".join(p['gold_range']) if p['gold_range'] else "—"
                pd = ", ".join(p['pred_domain']) if p['pred_domain'] else "—"
                pr = ", ".join(p['pred_range']) if p['pred_range'] else "—"
                L.append(f"| Gold | {gd} —[`{p['gold_predicate']}`]→ {gr} |")
                L.append(f"| Pred | {pd} —[`{p['pred_predicate']}`]→ {pr} |")
            L.append("")

    if L3.get("type_mismatches"):
        L.append(f"### Type-mismatched alignments ({len(L3['type_mismatches'])})")
        L.append("")
        L.append("_Pairs where the upstream alignment matched a gold "
                 "property to a pred property of a different type. "
                 "These are excluded from the per-type metrics above._")
        L.append("")
        L.append("| Gold predicate | Gold type | Pred predicate | Pred type |")
        L.append("|---|---|---|---|")
        for tm in L3["type_mismatches"]:
            L.append(f"| `{tm['gold_predicate']}` | {tm['gold_type']} | "
                     f"`{tm['pred_predicate']}` | {tm['pred_type']} |")
        L.append("")

    go = L3["grand_overall"]
    go_fp = go["fp"] + go["mismatch"]
    go_fn = go["fn"] + go["mismatch"]
    go_p_str = f"{go['precision']*100:.1f}%" if (go['tp'] + go_fp) else "—"
    go_r_str = f"{go['recall']*100:.1f}%" if (go['tp'] + go_fn) else "—"
    go_f_str = f"{go['f1']*100:.1f}%" if (go['tp'] + go_fp) and (go['tp'] + go_fn) else "—"
    L.append("### Layer 3 Summary (both property types, "
             "domain + range combined)")
    L.append("")
    L.append("| Precision | Recall | F1 | TP | FP | FN | mismatch |")
    L.append("|---:|---:|---:|---:|---:|---:|---:|")
    L.append(f"| {go_p_str} | {go_r_str} | {go_f_str} | "
             f"{go['tp']} | {go_fp} | {go_fn} | {go['mismatch']} |")
    L.append("")

    L4 = result["layer4_global"]
    L.append("## Layer 4, Global Overview")
    L.append("")
    L.append("Layer 3 only counts pairs already aligned by the upstream step. " \
    "Layer 4 also counts the unaligned ones: each unaligned gold axiom is a FN, " \
    "each unaligned pred axiom is a FP. TP stays the same.")
    L.append("")
    L.append("```")
    L.append("FP_global = Layer-3 FP + axioms of unaligned pred properties")
    L.append("FN_global = Layer-3 FN + axioms of unaligned gold properties")
    L.append("```")
    L.append("")

    def _fmt_pct_l4(value, denom_zero):
        return "—" if denom_zero else f"{value*100:.1f}%"

    for ptype in ("ObjectProperty", "DatatypeProperty"):
        b = L4[ptype]
        p_zero = (b["matched"] + b["extra"]) == 0
        r_zero = (b["matched"] + b["missing"]) == 0
        f_zero = p_zero or r_zero
        L.append(f"### {ptype}")
        L.append("")
        L.append("| Metric | Value | Detail |")
        L.append("|---|---:|---|")
        L.append(f"| Precision | {_fmt_pct_l4(b['precision'], p_zero)} | |")
        L.append(f"| Recall | {_fmt_pct_l4(b['recall'], r_zero)} | |")
        L.append(f"| F1 | {_fmt_pct_l4(b['f1'], f_zero)} | |")
        L.append(f"| TP | {b['matched']} | |")
        L.append(f"| FP | {b['extra']} | "
                 f"Layer-3 FP: {b['extra_layer3']} + unaligned pred "
                 f"axioms: {b['extra_unaligned']} |")
        L.append(f"| FN | {b['missing']} | "
                 f"Layer-3 FN: {b['missing_layer3']} + unaligned gold "
                 f"axioms: {b['missing_unaligned']} |")
        L.append(f"| Unaligned gold properties | "
                 f"{b['unaligned_gold_count']} | "
                 f"contributing {b['unaligned_gold_axiom_count']} axioms to FN |")
        L.append(f"| Unaligned pred properties | "
                 f"{b['unaligned_pred_count']} | "
                 f"contributing {b['unaligned_pred_axiom_count']} axioms to FP |")
        L.append("")

        if b["unaligned_gold"]:
            L.append(f"#### Unaligned gold {ptype}s (contributing to FN)")
            L.append("")
            L.append("| Predicate | Domain | Range | Axiom count |")
            L.append("|---|---|---|---:|")
            for u in b["unaligned_gold"]:
                dom = ", ".join(u['domain']) if u['domain'] else "—"
                rng = ", ".join(u['range']) if u['range'] else "—"
                L.append(f"| `{u['predicate']}` | {dom} | {rng} | "
                         f"{u['axiom_count']} |")
            L.append("")

        if b["unaligned_pred"]:
            L.append(f"#### Unaligned pred {ptype}s (contributing to FP)")
            L.append("")
            L.append("| Predicate | Domain | Range | Axiom count |")
            L.append("|---|---|---|---:|")
            for u in b["unaligned_pred"]:
                dom = ", ".join(u['domain']) if u['domain'] else "—"
                rng = ", ".join(u['range']) if u['range'] else "—"
                L.append(f"| `{u['predicate']}` | {dom} | {rng} | "
                         f"{u['axiom_count']} |")
            L.append("")

    g = L4["grand_overall"]
    g_p_zero = (g["matched"] + g["extra"]) == 0
    g_r_zero = (g["matched"] + g["missing"]) == 0
    g_f_zero = g_p_zero or g_r_zero
    L.append("### Grand Overall (Layer 4, global, all property types)")
    L.append("")
    L.append("| Metric | Value | Detail |")
    L.append("|---|---:|---|")
    L.append(f"| Precision | {_fmt_pct_l4(g['precision'], g_p_zero)} | |")
    L.append(f"| Recall | {_fmt_pct_l4(g['recall'], g_r_zero)} | |")
    L.append(f"| F1 | {_fmt_pct_l4(g['f1'], g_f_zero)} | |")
    L.append(f"| TP | {g['matched']} | |")
    L.append(f"| FP | {g['extra']} | "
             f"Layer-3 FP: {g['extra_layer3']} + unaligned pred axioms: "
             f"{g['extra_unaligned']} |")
    L.append(f"| FN | {g['missing']} | "
             f"Layer-3 FN: {g['missing_layer3']} + unaligned gold axioms: "
             f"{g['missing_unaligned']} |")
    L.append("")

    return "\n".join(L)


def append_triple_report_to_md(report_text: str, output_path: str) -> None:

    triple_marker = "# Property-Axiom (Triple) Evaluation Report"

    if not os.path.exists(output_path):
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"\n[report] Note: '{output_path}' did not exist. "
              f"Created a new file containing ONLY the property-axiom "
              f"report. To get a combined report, first run "
              f"concept_label_matching.py and eval_property.py with "
              f"--save_report_md pointing to the same file.")
        return

    with open(output_path, "r", encoding="utf-8") as f:
        existing = f.read()

    if triple_marker in existing:
        idx = existing.find(triple_marker)
        prefix = existing[:idx].rstrip()
        if prefix.endswith("---"):
            prefix = prefix[:-3].rstrip()
        new_existing = prefix + "\n\n"
        new_text = new_existing + "\n---\n\n" + report_text
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"\n[report] Triple-evaluation section already existed in "
              f"'{output_path}', replaced it with the new run.")
        return

    if not existing.endswith("\n"):
        existing += "\n"
    new_text = existing + "\n---\n\n" + report_text
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_text)
    print(f"\n[report] Triple-evaluation report appended to "
          f"'{output_path}'.")


def get_parser():
    p = argparse.ArgumentParser(
        description="Three-layer property-axiom evaluation"
    )
    p.add_argument("--pred_onto", required=True)
    p.add_argument("--gold_onto", required=True)
    p.add_argument("--model_id", default="embeddinggemma",
                   help="Ollama embedding model used for Layer 2")
    p.add_argument("--threshold", type=float, default=SEMANTIC_THRESHOLD,
                   help=f"Cosine threshold for Layer 2 (default: {SEMANTIC_THRESHOLD})")
    p.add_argument("--class_csv", default="class_best_matching.csv",
                   help="Class alignment CSV from concept_label_matching.py")
    p.add_argument("--property_csv", default="property_best_matching.csv",
                   help="Property alignment CSV from eval_property.py")
    p.add_argument("--save_result", default=None,
                   help="JSON output path; a sibling _report.txt is also written")
    p.add_argument("--save_layer3_csv", default=None,
                   help="CSV with one row per Layer-3 aligned property pair")
    p.add_argument("--save_layer3_json", default=None,
                   help="JSON with one entry per Layer-3 aligned property "
                        "pair, list-of-objects with id field")
    p.add_argument("--save_report_md", default=None,
                   help="Path to a Markdown file. If the file already "
                        "exists (e.g. from concept_label_matching.py + "
                        "eval_property.py), the triple-evaluation report "
                        "is appended after those sections. Otherwise a "
                        "new MD file is created with only this report.")
    

    #add soft version
    p.add_argument("--literal_relax",
                   choices=["yes", "no"], default="no",
                   help="If 'yes', a generic literal root in the gold "
                        "(rdfs:Literal / xsd:anySimpleType / "
                        "xsd:anyAtomicType) matches any concrete xsd:* "
                        "or rdf:* datatype in the prediction. "
                        "Default 'no' keeps strict equality.")
    return p


def main():
    args = get_parser().parse_args()
    # add soft version
    global LITERAL_RELAX
    LITERAL_RELAX = (args.literal_relax == "yes")
    print(f"[main] literal_relax = {args.literal_relax}")



    result = evaluate(
        pred_file=args.pred_onto,
        gold_file=args.gold_onto,
        class_csv=args.class_csv,
        property_csv=args.property_csv,
        model_id=args.model_id,
        threshold=args.threshold,
    )

    def _strip(o):
        if isinstance(o, dict):
            return {
                k: _strip(v) for k, v in o.items()
                if k not in ("matches", "all_pairs", "fully_aligned",
                             "unaligned_gold", "unaligned_pred")
            }
        return o

    print("\n===== SUMMARY =====")
    print(json.dumps(_strip(result), indent=2, ensure_ascii=False))

    if args.save_result:
        config = result.get("config", {})
        results_list = []
        for section_name, section_data in result.items():
            if section_name == "config":
                continue
            if isinstance(section_data, dict):
                results_list.append({"id": section_name, **section_data})
            else:
                results_list.append({"id": section_name, "value": section_data})
        out = {"config": config, "results": results_list}

        with open(args.save_result, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"\nFull result saved to: {args.save_result}")
        report_path = args.save_result.replace(".json", "_report.txt")
        generate_report(result, report_path)

    if args.save_layer3_csv:
        save_layer3_pairs_csv(result, args.save_layer3_csv)

    if args.save_layer3_json:
        save_layer3_pairs_json(result, args.save_layer3_json)

    if args.save_report_md:
        report_text = build_triple_report_md(result)
        append_triple_report_to_md(report_text, args.save_report_md)


if __name__ == "__main__":
    main()
