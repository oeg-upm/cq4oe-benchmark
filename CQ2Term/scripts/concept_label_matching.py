#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import csv
import json
import argparse
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

from rdflib import Graph, RDF, OWL, RDFS, Literal
from rdflib.term import BNode

from sentence_transformers import util
from langchain_ollama import OllamaEmbeddings

import difflib
import Levenshtein
import textdistance

import nltk
from nltk.corpus import wordnet as wn



SEMANTIC_THRESHOLD = 0.6
LEXICAL_THRESHOLD = 0.8
HARD_THRESHOLD = 1.0



# add the thresholds for 5 simi methods
def override_thresholds(semantic=None, lexical=None, hard=None):
    """Override the per-method similarity thresholds at runtime.

    Each argument is optional. Pass ``None`` (the default) to keep the
    current value. Pass a float to override it. Called by ``eval_cq_terms``
    when the user supplies the matching CLI flags.
    """
    global SEMANTIC_THRESHOLD, LEXICAL_THRESHOLD, HARD_THRESHOLD
    if semantic is not None:
        SEMANTIC_THRESHOLD = float(semantic)
    if lexical is not None:
        LEXICAL_THRESHOLD = float(lexical)
    if hard is not None:
        HARD_THRESHOLD = float(hard)



def ensure_nltk_resource():
    try:
        wn.synsets("dog")
    except LookupError:
        nltk.download("wordnet")
        nltk.download("omw-1.4")



def get_class_name(uri, graph=None):

    if graph is not None:
        labels = list(graph.objects(uri, RDFS.label))

        for l in labels:
            if isinstance(l, Literal) and getattr(l, "language", None) == "en":
                return str(l).strip()

        for l in labels:
            if isinstance(l, Literal) and getattr(l, "language", None) in (None, ""):
                return str(l).strip()

        for l in labels:
            if isinstance(l, Literal):
                return str(l).strip()

    uri_str = str(uri)
    if "#" in uri_str:
        local = uri_str.split("#")[-1]
    else:
        local = uri_str.rstrip("/").split("/")[-1]
    if local:
        return local
    return uri_str


def _norm(text):

    if text is None:
        return ""
    return str(text).strip().lower()


def _iri_local_name(iri: str) -> str:
    if "#" in iri:
        return iri.split("#")[-1]

    return iri.rstrip("/").split("/")[-1]

def _rdflib_extract_explicit_classes(file_path: str, fmt: str):
    g = Graph()
    g.parse(file_path, format=fmt)

    owl_class_uris = set()
    rdfs_class_uris = set()

    for cls in g.subjects(RDF.type, OWL.Class):
        if isinstance(cls, BNode):
            continue

        if str(cls) in {str(OWL.Thing), str(OWL.Nothing)}:
            continue

        owl_class_uris.add(cls)

    for cls in g.subjects(RDF.type, RDFS.Class):
        if isinstance(cls, BNode):
            continue

        if str(cls) in {str(OWL.Thing), str(OWL.Nothing)}:
            continue

        rdfs_class_uris.add(cls)

    all_uris = owl_class_uris | rdfs_class_uris
    names = sorted(set(get_class_name(uri, g) for uri in all_uris))

    return names


def extract_classes_from_rdfxml_etree(file_path):
    OWL_NS = "http://www.w3.org/2002/07/owl#"
    RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    RDFS_NS = "http://www.w3.org/2000/01/rdf-schema#"
    XML_NS = "http://www.w3.org/XML/1998/namespace"

    tree = ET.parse(file_path)
    root = tree.getroot()

    owl_class_uris = set()
    rdfs_class_uris = set()
    name_map = {}

    def best_label_from_elem(elem):
        en_label = None
        plain_label = None
        any_label = None

        for lbl in elem.findall(f"{{{RDFS_NS}}}label"):
            text = (lbl.text or "").strip()

            if not text:
                continue

            lang = lbl.get(f"{{{XML_NS}}}lang")

            if lang == "en":
                en_label = text
                break
            elif lang in (None, "") and plain_label is None:
                plain_label = text
            elif any_label is None:
                any_label = text

        return en_label or plain_label or any_label

    builtin_iris = {
        "http://www.w3.org/2002/07/owl#Thing",
        "http://www.w3.org/2002/07/owl#Nothing",
    }

    for elem in root.iter(f"{{{OWL_NS}}}Class"):
        iri = elem.get(f"{{{RDF_NS}}}about") or elem.get(f"{{{RDF_NS}}}ID")

        if not iri:
            continue

        if iri in builtin_iris:
            continue

        owl_class_uris.add(iri)
        name_map[iri] = _iri_local_name(iri) or best_label_from_elem(elem)

    for elem in root.iter(f"{{{RDFS_NS}}}Class"):
        iri = elem.get(f"{{{RDF_NS}}}about") or elem.get(f"{{{RDF_NS}}}ID")

        if not iri:
            continue

        if iri in builtin_iris:
            continue

        rdfs_class_uris.add(iri)
        name_map[iri] = _iri_local_name(iri) or best_label_from_elem(elem)

    for elem in root.iter(f"{{{RDF_NS}}}Description"):
        iri = elem.get(f"{{{RDF_NS}}}about") or elem.get(f"{{{RDF_NS}}}ID")

        if not iri:
            continue

        if iri in builtin_iris:
            continue

        declared_as_owl = False
        declared_as_rdfs = False

        for type_elem in elem.findall(f"{{{RDF_NS}}}type"):
            type_res = type_elem.get(f"{{{RDF_NS}}}resource")

            if type_res == "http://www.w3.org/2002/07/owl#Class":
                declared_as_owl = True
            elif type_res == "http://www.w3.org/2000/01/rdf-schema#Class":
                declared_as_rdfs = True

        if not declared_as_owl and not declared_as_rdfs:
            continue

        if declared_as_owl:
            owl_class_uris.add(iri)

        if declared_as_rdfs:
            rdfs_class_uris.add(iri)

        name_map[iri] = _iri_local_name(iri) or best_label_from_elem(elem)

    all_uris = owl_class_uris | rdfs_class_uris
    names = sorted(set(name_map[uri] for uri in all_uris))

    return names


def extract_classes_from_functional_owlxml(file_path):
    OWL_NS = "http://www.w3.org/2002/07/owl#"
    XML_NS = "http://www.w3.org/XML/1998/namespace"

    tree = ET.parse(file_path)
    root = tree.getroot()

    class_ids = {}

    builtin_iris = {
        "http://www.w3.org/2002/07/owl#Thing",
        "http://www.w3.org/2002/07/owl#Nothing",
    }

    builtin_abbrs = {
        "owl:Thing",
        "owl:Nothing",
    }

    for decl in root.iter(f"{{{OWL_NS}}}Declaration"):
        cls_elem = decl.find(f"{{{OWL_NS}}}Class")

        if cls_elem is None:
            continue

        iri = cls_elem.get("IRI")
        abbr = cls_elem.get("abbreviatedIRI")

        if iri:
            if iri in builtin_iris:
                continue

            class_ids[iri] = _iri_local_name(iri)

        elif abbr:
            if abbr in builtin_abbrs:
                continue

            local = abbr.split(":")[-1] if ":" in abbr else abbr
            class_ids[abbr] = local

    if not class_ids:
        return []

    label_map = {}

    for ann in root.iter(f"{{{OWL_NS}}}AnnotationAssertion"):
        prop = ann.find(f"{{{OWL_NS}}}AnnotationProperty")

        if prop is None:
            continue

        prop_abbr = prop.get("abbreviatedIRI", "")
        prop_iri = prop.get("IRI", "")

        is_label = (
            prop_abbr == "rdfs:label"
            or prop_iri == "http://www.w3.org/2000/01/rdf-schema#label"
        )

        if not is_label:
            continue

        subj_iri = ann.find(f"{{{OWL_NS}}}IRI")
        subj_abbr = ann.find(f"{{{OWL_NS}}}AbbreviatedIRI")

        subj = (
            subj_iri.text if subj_iri is not None else
            subj_abbr.text if subj_abbr is not None else
            None
        )

        if not subj:
            continue

        lit = ann.find(f"{{{OWL_NS}}}Literal")

        if lit is None:
            continue

        text = (lit.text or "").strip()

        if not text:
            continue

        lang = lit.get(f"{{{XML_NS}}}lang")

        if subj not in label_map:
            label_map[subj] = {}

        if lang == "en" and "en" not in label_map[subj]:
            label_map[subj]["en"] = text
        elif lang in (None, "") and "plain" not in label_map[subj]:
            label_map[subj]["plain"] = text
        elif "any" not in label_map[subj]:
            label_map[subj]["any"] = text

    names = []

    for id_str, local_fallback in class_ids.items():
        labels = label_map.get(id_str, {})
        name = local_fallback or labels.get("en") or labels.get("plain") or labels.get("any")

        if name:
            names.append(name)

    return sorted(set(names))


def extract_classes_from_jsonld(file_path):
    OWL_CLASS_URIS = {
        "owl:Class",
        "http://www.w3.org/2002/07/owl#Class",
    }

    RDFS_CLASS_URIS = {
        "rdfs:Class",
        "http://www.w3.org/2000/01/rdf-schema#Class",
    }

    builtin_iris = {
        "owl:Thing",
        "owl:Nothing",
        "http://www.w3.org/2002/07/owl#Thing",
        "http://www.w3.org/2002/07/owl#Nothing",
    }

    def _get_label(node):
        for key in (
            "rdfs:label",
            "http://www.w3.org/2000/01/rdf-schema#label",
            "label",
        ):
            val = node.get(key)

            if val is None:
                continue

            if isinstance(val, str):
                return val

            if isinstance(val, dict):
                return val.get("@value", "")

            if isinstance(val, list):
                for v in val:
                    if isinstance(v, dict) and v.get("@language") == "en":
                        return v.get("@value", "")

                for v in val:
                    if isinstance(v, dict) and v.get("@language") in (None, ""):
                        return v.get("@value", "")

                first = val[0]

                if isinstance(first, dict):
                    return first.get("@value", "")

                return str(first)

        return None

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    graph_data = data if isinstance(data, list) else data.get("@graph", [data])

    names = []

    for node in graph_data:
        if not isinstance(node, dict):
            continue

        types = node.get("@type", [])

        if isinstance(types, str):
            types = [types]

        if not any(t in OWL_CLASS_URIS or t in RDFS_CLASS_URIS for t in types):
            continue

        iri = node.get("@id", "")

        if iri in builtin_iris:
            continue

        label = _iri_local_name(iri) if iri else None

        if not label:
            label = _get_label(node)

        if label:
            names.append(label)

    return sorted(set(names))


_RDFLIB_FORMATS = [
    ("xml", {".owl", ".rdf", ".xml"}),
    ("turtle", {".ttl", ".turtle"}),
    ("nt", {".nt"}),
    ("nquads", {".nq"}),
    ("json-ld", {".jsonld", ".json"}),
    ("trig", {".trig"}),
    ("trix", {".trix"}),
]


def extract_classes(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    ordered_formats = sorted(
        _RDFLIB_FORMATS,
        key=lambda x: 0 if ext in x[1] else 1
    )

    last_error = None

    for fmt, _ in ordered_formats:
        try:
            names = _rdflib_extract_explicit_classes(file_path, fmt)

            if names:
                print(f"[extract_classes] Parsed '{file_path}' with rdflib format='{fmt}'")
                return sorted(set(names))

        except Exception as e:
            last_error = e

    print(f"[extract_classes] rdflib failed or found no explicit classes. Last error: {last_error}")

    if ext in {".owl", ".rdf", ".xml", ""}:
        try:
            names = extract_classes_from_rdfxml_etree(file_path)

            if names:
                print("[extract_classes] Recovered classes via RDF/XML etree fallback.")
                return sorted(set(names))

        except Exception as e:
            print(f"[extract_classes] RDF/XML etree fallback failed: {e}")

        try:
            names = extract_classes_from_functional_owlxml(file_path)

            if names:
                print("[extract_classes] Recovered classes via OWL/XML functional fallback.")
                return sorted(set(names))

        except Exception as e:
            print(f"[extract_classes] OWL/XML functional fallback failed: {e}")

    if ext in {".jsonld", ".json"}:
        try:
            names = extract_classes_from_jsonld(file_path)

            if names:
                print("[extract_classes] Recovered classes via JSON-LD fallback.")
                return sorted(set(names))

        except Exception as e:
            print(f"[extract_classes] JSON-LD fallback failed: {e}")

    print(f"[extract_classes] WARNING: no explicit classes extracted from '{file_path}'")

    return []

def split_camel_case(text):
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    text = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", text)
    return text


def normalize_key(concept):

    text = str(concept or "").strip()
    text = split_camel_case(text)
    text = text.lower()
    text = text.replace("_", " ").replace("-", " ")
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", "", text)
    return text


def normalize_text(concept):

    text = str(concept or "").strip()
    text = split_camel_case(text)
    text = text.replace("_", " ").replace("-", " ")
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()


def check_normalized_duplicates(raw_terms, name, mode):

    if mode == "key":
        normalized = [normalize_key(x) for x in raw_terms]
    elif mode == "text":
        normalized = [normalize_text(x) for x in raw_terms]
    else:
        raise ValueError("mode must be 'key' or 'text'")

    counts = Counter(normalized)
    duplicated = {k: v for k, v in counts.items() if v > 1}

    if duplicated:
        print(f"\n[WARNING] duplicated normalized {name} by normalize_{mode}:")
        for k, v in duplicated.items():
            print(f"  {k}: {v}")


def build_records(raw_terms):

    records = []

    for idx, raw in enumerate(raw_terms):
        records.append({
            "id": idx,
            "raw": raw,
            "key": normalize_key(raw),
            "text": normalize_text(raw),
        })

    return records


def make_gold_entry(gold_term):
    return {
        "gold_term": gold_term,
        "matched_preds": []
    }


def make_pred_entry(pred_term):
    return {
        "pred_term": pred_term,
        "matched_golds": []
    }


def match_one_to_one_greedy(gold_records, pred_records, sim_func, threshold):

    candidates = []

    for g in gold_records:
        for p in pred_records:
            score = sim_func(g, p)

            if score >= threshold:
                candidates.append((score, g["id"], p["id"]))

    candidates.sort(key=lambda x: x[0], reverse=True)

    used_gold = set()
    used_pred = set()

    gold_match = {}
    pred_match = {}

    for score, gold_id, pred_id in candidates:
        if gold_id in used_gold:
            continue

        if pred_id in used_pred:
            continue

        gold_match[gold_id] = (pred_id, score)
        pred_match[pred_id] = (gold_id, score)

        used_gold.add(gold_id)
        used_pred.add(pred_id)

    return gold_match, pred_match


def compute_full_score_matrix(gold_records, pred_records, sim_func):

    out = []
    for g in gold_records:
        for p in pred_records:
            score = sim_func(g, p)
            out.append((score, g["id"], p["id"]))
    return out


def compute_lexical_sim_from_normalized(a_norm, b_norm, info_type):


    if info_type == "hard_match":
        return 1.0 if a_norm == b_norm else 0.0

    elif info_type == "sequence_match":
        return difflib.SequenceMatcher(None, a_norm, b_norm).ratio()

    elif info_type == "levenshtein":
        dist = Levenshtein.distance(a_norm, b_norm)
        return 1 - dist / max(len(a_norm), len(b_norm), 1)

    elif info_type == "jaro_winkler":
        return textdistance.jaro_winkler.normalized_similarity(a_norm, b_norm)

    else:
        print(f"[WARNING] Metric type '{info_type}' is not properly defined.")
        return 0.0


def get_threshold(info_type):
    if info_type == "hard_match":
        return HARD_THRESHOLD

    if info_type == "semantic":
        return SEMANTIC_THRESHOLD

    return LEXICAL_THRESHOLD


def compute_full_score_table(gen_class, ground_class, info_type,
                             model_id=None):

    gold_records = build_records(ground_class)
    pred_records = build_records(gen_class)

    if not gold_records or not pred_records:
        return []

    if info_type in {"hard_match", "sequence_match",
                     "levenshtein", "jaro_winkler"}:
        def sim_func(g_record, p_record):
            return compute_lexical_sim_from_normalized(
                g_record["key"], p_record["key"], info_type)
    elif info_type == "semantic":
        if not model_id:
            raise ValueError("semantic matching requires --model_id")
        encoder = OllamaEmbeddings(model=model_id)
        gold_texts = [r["text"] for r in gold_records]
        pred_texts = [r["text"] for r in pred_records]
        all_texts = gold_texts + pred_texts
        print(f"\n[semantic] (no-threshold mode) model = {model_id}")
        embeddings = encoder.embed_documents(all_texts)
        gold_embed = embeddings[:len(gold_records)]
        pred_embed = embeddings[len(gold_records):]
        sim_matrix = [
            [float(util.cos_sim(gold_embed[i], pred_embed[j]).item())
             for j in range(len(pred_records))]
            for i in range(len(gold_records))
        ]
        def sim_func(g_record, p_record):
            return sim_matrix[g_record["id"]][p_record["id"]]
    else:
        raise ValueError(
            f"Unsupported info_type='{info_type}'. "
            f"Supported: hard_match, sequence_match, levenshtein, "
            f"jaro_winkler, semantic")

    out = []
    for g in gold_records:
        for p in pred_records:
            score = sim_func(g, p)
            out.append({
                "gold_term": g["raw"],
                "pred_term": p["raw"],
                "method": info_type,
                "score": float(score),
            })
    return out


def pre_process(gen_class, ground_class, info_type, model_id=None):

    threshold = get_threshold(info_type)

    gold_records = build_records(ground_class)
    pred_records = build_records(gen_class)

    gold_id_to_record = {r["id"]: r for r in gold_records}
    pred_id_to_record = {r["id"]: r for r in pred_records}

    if len(gold_records) == 0 or len(pred_records) == 0:
        gold_map = {g: make_gold_entry(g) for g in ground_class}
        pred_map = {p: make_pred_entry(p) for p in gen_class}

        scores_gold2pred = [(g, None, 0.0) for g in ground_class]
        scores_pred2gold = [(p, None, 0.0) for p in gen_class]

        return gold_map, pred_map, scores_gold2pred, scores_pred2gold, threshold

    if info_type in {"hard_match", "sequence_match", "levenshtein", "jaro_winkler"}:

        def sim_func(g_record, p_record):
            return compute_lexical_sim_from_normalized(
                g_record["key"],
                p_record["key"],
                info_type
            )

    elif info_type == "semantic":
        if not model_id:
            raise ValueError("semantic matching requires --model_id")

        try:
            encoder = OllamaEmbeddings(model=model_id)

            gold_texts = [r["text"] for r in gold_records]
            pred_texts = [r["text"] for r in pred_records]

            all_texts = gold_texts + pred_texts

            print(f"\n[semantic] model = {model_id}")
            print("[semantic] examples of normalized texts sent to embedding:")
            print("  Gold:", gold_texts[:10])
            print("  Pred:", pred_texts[:10])

            embeddings = encoder.embed_documents(all_texts)

            gold_embed = embeddings[:len(gold_records)]
            pred_embed = embeddings[len(gold_records):]

            sim_matrix = [
                [
                    float(util.cos_sim(gold_embed[i], pred_embed[j]).item())
                    for j in range(len(pred_records))
                ]
                for i in range(len(gold_records))
            ]

            def sim_func(g_record, p_record):
                i = g_record["id"]
                j = p_record["id"]
                return sim_matrix[i][j]

        except Exception as e:
            print(f"[semantic] ERROR: embedding failed with model='{model_id}'.")
            print(f"[semantic] Details: {e}")

            gold_map = {g: make_gold_entry(g) for g in ground_class}
            pred_map = {p: make_pred_entry(p) for p in gen_class}

            scores_gold2pred = [(g, None, 0.0) for g in ground_class]
            scores_pred2gold = [(p, None, 0.0) for p in gen_class]

            return gold_map, pred_map, scores_gold2pred, scores_pred2gold, threshold

    else:
        raise ValueError(
            f"Unsupported info_type='{info_type}'. "
            f"Supported methods: hard_match, sequence_match, levenshtein, jaro_winkler, semantic"
        )

    gold_match, pred_match = match_one_to_one_greedy(
        gold_records,
        pred_records,
        sim_func,
        threshold
    )

    scores_gold2pred = []

    for g_record in gold_records:
        gold_id = g_record["id"]
        gold_raw = g_record["raw"]

        if gold_id in gold_match:
            pred_id, score = gold_match[gold_id]
            pred_raw = pred_id_to_record[pred_id]["raw"]
            scores_gold2pred.append((gold_raw, pred_raw, score))
        else:
            scores_gold2pred.append((gold_raw, None, 0.0))

    scores_pred2gold = []

    for p_record in pred_records:
        pred_id = p_record["id"]
        pred_raw = p_record["raw"]

        if pred_id in pred_match:
            gold_id, score = pred_match[pred_id]
            gold_raw = gold_id_to_record[gold_id]["raw"]
            scores_pred2gold.append((pred_raw, gold_raw, score))
        else:
            scores_pred2gold.append((pred_raw, None, 0.0))

    gold_map = {g: make_gold_entry(g) for g in ground_class}
    pred_map = {p: make_pred_entry(p) for p in gen_class}

    for gold_id, (pred_id, score) in gold_match.items():
        gold_raw = gold_id_to_record[gold_id]["raw"]
        pred_raw = pred_id_to_record[pred_id]["raw"]

        gold_map[gold_raw]["matched_preds"].append({
            "pred_term": pred_raw,
            "method": info_type,
            "score": round(score, 4),
            "threshold": threshold,
            "is_correct": score >= threshold
        })

    for pred_id, (gold_id, score) in pred_match.items():
        pred_raw = pred_id_to_record[pred_id]["raw"]
        gold_raw = gold_id_to_record[gold_id]["raw"]

        pred_map[pred_raw]["matched_golds"].append({
            "gold_term": gold_raw,
            "method": info_type,
            "score": round(score, 4),
            "threshold": threshold,
            "is_correct": score >= threshold
        })

    return gold_map, pred_map, scores_gold2pred, scores_pred2gold, threshold


def cal_metrics(gen_class, ground_class, info_type, model_id=None):
    gold_map, pred_map, scores_gold2pred, scores_pred2gold, threshold = pre_process(
        gen_class,
        ground_class,
        info_type,
        model_id
    )

    TP_g = sum(1 for _, _, s in scores_gold2pred if s >= threshold)
    TP_p = sum(1 for _, _, s in scores_pred2gold if s >= threshold)

    precision = TP_p / len(gen_class) if gen_class else 0.0
    recall = TP_g / len(ground_class) if ground_class else 0.0
    coverage = recall

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    print(f"[{info_type}] threshold={threshold}  TP_g={TP_g}/{len(ground_class)}  TP_p={TP_p}/{len(gen_class)}")
    print(f"  Precision={precision:.4f}  Recall={recall:.4f}  Coverage={coverage:.4f}  F1={f1:.4f}")

    return coverage, precision, recall, f1, gold_map, pred_map


def wordnet_noun_synonyms_from_normalized_text(term_text: str) -> set:

    base = term_text.replace(" ", "_")

    syns = set()
    variants = {term_text, base}

    for v in variants:
        for s in wn.synsets(v, pos=wn.NOUN):
            for lemma in s.lemmas():
                norm = normalize_text(lemma.name())

                if norm and norm != term_text:
                    syns.add(norm)

    return syns


def cal_synonym(gen_class, ground_class):
    ensure_nltk_resource()

    threshold = 1.0

    gold_records = build_records(ground_class)
    pred_records = build_records(gen_class)

    gold_id_to_record = {r["id"]: r for r in gold_records}
    pred_id_to_record = {r["id"]: r for r in pred_records}

    synonyms_map = {
        g["id"]: wordnet_noun_synonyms_from_normalized_text(g["text"])
        for g in gold_records
    }

    def sim_func(g_record, p_record):
        gold_text = g_record["text"]
        pred_text = p_record["text"]

        if gold_text == pred_text:
            return 1.0

        if pred_text in synonyms_map[g_record["id"]]:
            return 1.0

        return 0.0

    gold_match, pred_match = match_one_to_one_greedy(
        gold_records,
        pred_records,
        sim_func,
        threshold
    )

    TP_g = len(gold_match)
    TP_p = len(pred_match)

    precision = TP_p / len(gen_class) if gen_class else 0.0
    recall = TP_g / len(ground_class) if ground_class else 0.0
    coverage = recall

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    gold_map = {g: make_gold_entry(g) for g in ground_class}
    pred_map = {p: make_pred_entry(p) for p in gen_class}

    for gold_id, (pred_id, score) in gold_match.items():
        gold_raw = gold_id_to_record[gold_id]["raw"]
        pred_raw = pred_id_to_record[pred_id]["raw"]

        gold_map[gold_raw]["matched_preds"].append({
            "pred_term": pred_raw,
            "method": "synonym",
            "score": 1.0,
            "threshold": threshold,
            "is_correct": True
        })

    for pred_id, (gold_id, score) in pred_match.items():
        pred_raw = pred_id_to_record[pred_id]["raw"]
        gold_raw = gold_id_to_record[gold_id]["raw"]

        pred_map[pred_raw]["matched_golds"].append({
            "gold_term": gold_raw,
            "method": "synonym",
            "score": 1.0,
            "threshold": threshold,
            "is_correct": True
        })

    print(f"[synonym] threshold={threshold}  TP_g={TP_g}/{len(ground_class)}  TP_p={TP_p}/{len(gen_class)}")
    print(f"  Precision={precision:.4f}  Recall={recall:.4f}  Coverage={coverage:.4f}  F1={f1:.4f}")

    return coverage, precision, recall, f1, gold_map, pred_map

def _dict_to_list_of_objects(data):

    if isinstance(data, list):

        out = []
        for i, item in enumerate(data, 1):
            if isinstance(item, dict) and "id" not in item:
                out.append({"id": i, **item})
            else:
                out.append(item)
        return out
    if not isinstance(data, dict):
        return data
    out = []
    for key, value in data.items():
        if isinstance(value, dict):
            out.append({"id": key, **value})
        else:
            out.append({"id": key, "value": value})
    return out


def save_json(data, save_path):
    if not save_path:
        return

    serializable = _dict_to_list_of_objects(data)

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=4)


def save_all_pairings_to_json(all_pairings, save_path):
    if not save_path:
        return

    serializable = _dict_to_list_of_objects(all_pairings)

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=4)


def build_merged_tp_gold_to_pred(all_gold_maps):

    out = {}

    for matching_way, gold_map in all_gold_maps.items():
        for gold_term, entry in gold_map.items():
            for m in entry.get("matched_preds", []):
                if m.get("is_correct", False) and m.get("pred_term") is not None:
                    if gold_term not in out:
                        out[gold_term] = {
                            "gold_term": gold_term,
                            "matched_preds": []
                        }

                    out[gold_term]["matched_preds"].append({
                        "pred_term": m["pred_term"],
                        "matching_way": matching_way,
                        "score": m["score"]
                    })

    return out


def build_merged_tp_pred_to_gold(all_pred_maps):

    out = {}

    for matching_way, pred_map in all_pred_maps.items():
        for pred_term, entry in pred_map.items():
            for m in entry.get("matched_golds", []):
                if m.get("is_correct", False) and m.get("gold_term") is not None:
                    if pred_term not in out:
                        out[pred_term] = {
                            "pred_term": pred_term,
                            "matched_golds": []
                        }

                    out[pred_term]["matched_golds"].append({
                        "gold_term": m["gold_term"],
                        "matching_way": matching_way,
                        "score": m["score"]
                    })

    return out


def build_best_class_map_top_n(all_score_tables, top_n=3,
                               final_threshold=0.0,
                               return_trace=False):

    pair_scores = defaultdict(dict)   # (gold, pred) → {method: score}
    hard_match_pairs = set()          # pairs that hit hard_match (score=1.0)

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
            "gold": g,
            "pred": p,
            "agg_score": agg,
            "matching_way": label,
            "scores_by_method": dict(scores),
            "top_methods": top_methods,
            "n_methods_total": len(scores),
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
                "reason": (f"pred already taken by '{stealer}' "
                           f"(higher averaged score)"),
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
                "agg_score": round(c["agg_score"], 4),
                "is_hard_match": c["is_hard_match"],
                "selected": log["selected"],
                "reason": log["reason"],
            })

        trace.sort(key=lambda t: (not t["selected"], -t["agg_score"]))

    n_dropped_threshold = sum(1 for v in selection_log.values()
                              if not v["selected"]
                              and "final_threshold" in v["reason"])
    n_dropped_one_to_one = sum(1 for v in selection_log.values()
                               if not v["selected"]
                               and "final_threshold" not in v["reason"])

    print(f"\n[build_best_class_map_top_{top_n}_avg]")
    print(f"  Candidate pairs collected: {len(pair_scores)}")
    print(f"  Aggregated (after per-pair top-{top_n} average): {len(aggregated)}")
    if final_threshold > 0:
        print(f"  Dropped by threshold {final_threshold}: {n_dropped_threshold}")
    print(f"  Dropped by 1-to-1 enforcement: {n_dropped_one_to_one}")
    print(f"  Final selected: {len(final_map)}")
    if final_threshold == 0:
        print(f"  Note: NO threshold applied (final_threshold=0); every gold "
              f"has a best-match candidate.")

    if return_trace:
        return final_map, trace
    return final_map


def build_best_class_map(all_gold_maps, agreement_threshold=0.6,
                         return_trace=False):

    pair_scores = {}

    for matching_way, gold_map in all_gold_maps.items():
        for gold_term, entry in gold_map.items():
            for m in entry.get("matched_preds", []):
                if not m.get("is_correct", False):
                    continue
                pred = m.get("pred_term")
                if pred is None:
                    continue
                key = (gold_term, pred)
                if key not in pair_scores:
                    pair_scores[key] = {
                        "scores_by_method": {},
                        "hard_match_hit": False,
                    }
                pair_scores[key]["scores_by_method"][matching_way] = m["score"]
                if matching_way == "hard_match":
                    pair_scores[key]["hard_match_hit"] = True


    aggregated = []
    for (gold, pred), info in pair_scores.items():
        scores = info["scores_by_method"]
        non_hard = {k: v for k, v in scores.items() if k != "hard_match"}

        if info["hard_match_hit"]:
            agg_score = 1.0
            label = "hard_match"
            methods_used = sorted(scores.keys())
        else:
            if not non_hard:
                continue
            agg_score = sum(non_hard.values()) / len(non_hard)
            methods_used = sorted(non_hard.keys())
            label = f"average({'+'.join(methods_used)})"

        aggregated.append({
            "gold": gold,
            "pred": pred,
            "agg_score": agg_score,
            "matching_way": label,
            "methods_used": methods_used,
            "score": agg_score,
            "scores_by_method": dict(scores),
            "hard_match_hit": info["hard_match_hit"],
        })

    above_threshold = [c for c in aggregated
                       if (c["matching_way"] == "hard_match" or
                           c["agg_score"] >= agreement_threshold)]
    n_dropped_threshold = len(aggregated) - len(above_threshold)
    below_threshold_set = {(c["gold"], c["pred"]) for c in aggregated} - \
                          {(c["gold"], c["pred"]) for c in above_threshold}

    def _vote_count(c):
        if c["matching_way"] == "hard_match":
            return 999
        return len(c["methods_used"])

    above_threshold.sort(key=lambda c: (_vote_count(c), c["agg_score"]),
                         reverse=True)
    final_map = {}
    used_preds = set()
    selection_log = {}     # (gold, pred) → {selected: bool, reason: str}

    for c in above_threshold:
        key = (c["gold"], c["pred"])
        if c["gold"] in final_map:
            selection_log[key] = {
                "selected": False,
                "reason": f"gold already mapped to '{final_map[c['gold']]['pred_term']}'",
            }
            continue
        if c["pred"] in used_preds:
            stealer = None
            for g, info in final_map.items():
                if info["pred_term"] == c["pred"]:
                    stealer = g
                    break
            selection_log[key] = {
                "selected": False,
                "reason": f"pred already taken by '{stealer}' (more votes or higher score)",
            }
            continue
        final_map[c["gold"]] = {
            "gold_term": c["gold"],
            "pred_term": c["pred"],
            "matching_way": c["matching_way"],
            "score": c["agg_score"],
            "n_votes": _vote_count(c) if _vote_count(c) < 999 else "hard_match",
        }
        used_preds.add(c["pred"])
        selection_log[key] = {"selected": True, "reason": "selected"}

    n_dropped_one_to_one = sum(1 for v in selection_log.values()
                               if not v["selected"])

    if return_trace:
        trace = []
        for c in aggregated:
            key = (c["gold"], c["pred"])
            if (c["gold"], c["pred"]) in below_threshold_set:
                selected = False
                reason = (f"below global threshold "
                          f"{agreement_threshold} (agg_score="
                          f"{c['agg_score']:.4f})")
            else:
                log = selection_log.get(key, {"selected": False,
                                              "reason": "(not seen)"})
                selected = log["selected"]
                reason = log["reason"]
            trace.append({
                "gold_term": c["gold"],
                "pred_term": c["pred"],
                "n_methods_voted": len(c["methods_used"]),
                "methods_voted": "+".join(c["methods_used"]),
                "scores_by_method": "; ".join(f"{k}={v:.4f}"
                                              for k, v in
                                              sorted(c["scores_by_method"].items())),
                "hard_match_hit": c["hard_match_hit"],
                "agg_score": round(c["agg_score"], 4),
                "above_global_threshold": (c["agg_score"]
                                           >= agreement_threshold or
                                           c["hard_match_hit"]),
                "selected": selected,
                "reason": reason,
            })
        # Sort trace: selected first, then by agg_score desc
        trace.sort(key=lambda t: (not t["selected"], -t["agg_score"]))


    print(f"[build_best_class_map] {len(pair_scores)} candidate pairs "
          f"collected across all methods")
    print(f"  → {len(aggregated)} after per-pair aggregation "
          f"(hard_match: 1.0; otherwise mean of non-hard methods)")
    print(f"  → {len(above_threshold)} above threshold "
          f"{agreement_threshold} (dropped {n_dropped_threshold})")
    print(f"  → {len(final_map)} after 1-to-1 enforcement "
          f"(dropped {n_dropped_one_to_one})")

    if return_trace:
        return final_map, trace
    return final_map


def save_alignment_trace_csv(trace, output_path):

    fields = [
        "gold_term", "pred_term",
        "top_methods_used",
        "scores_by_method",
        "is_hard_match",
        "agg_score",
        "selected",
        "reason",
    ]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in trace:
            writer.writerow(row)
    print(f"\nAlignment trace (per-pair scoring details) saved to: "
          f"{output_path}")


def save_alignment_trace_json(trace, output_path):

    out = []
    for i, row in enumerate(trace, 1):

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
    print(f"\nAlignment trace (per-pair scoring details, JSON) saved to: "
          f"{output_path}")


def save_matching_csv(gold_terms, all_gold_maps, output_path):

    if not output_path:
        return

    method_names = list(all_gold_maps.keys())
    gold_terms_sorted = sorted(set(gold_terms))

    headers = ["gold"]

    for m in method_names:
        headers.append(f"{m}_pred")
        headers.append(f"{m}_score")

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for gold in gold_terms_sorted:
            row = [gold]

            for m in method_names:
                gold_map = all_gold_maps[m]
                entry = gold_map.get(gold, {})
                preds = entry.get("matched_preds", [])

                if preds:
                    best = preds[0]
                    pred_term = best.get("pred_term", "")
                    score = best.get("score", 0.0)
                else:
                    pred_term = ""
                    score = 0.0

                row.append(pred_term)
                row.append(score)

            writer.writerow(row)

    print(f"Matching details CSV saved to: {output_path}")


def save_best_matching_csv(best_class_map, output_path):
    
    if not output_path:
        return

    headers = ["Gold_term", "Pre_term", "Method", "Score"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for gold_term, item in sorted(best_class_map.items()):
            writer.writerow([
                item.get("gold_term", gold_term),
                item.get("pred_term", ""),
                item.get("matching_way", ""),
                item.get("score", 0.0)
            ])

    print(f"Best matching CSV saved to: {output_path}")

def build_class_report_md(ground_class, gen_class, result, best_class_map,
                          top_n, final_threshold, model_id):

    lines = []

    lines.append("# Class-Level Label Matching Report")
    lines.append("")
    lines.append(f"_Generated by `eval_concept.py`_  ")
    lines.append(f"_Methods compared: hard_match, jaro_winkler, "
                 f"levenshtein, sequence_match, semantic (model: "
                 f"`{model_id}`)_")
    lines.append("")

    lines.append("## Layer 1 — Class Statistics")
    lines.append("")
    gold_count = len(ground_class)
    pred_count = len(gen_class)
    gold_set = {normalize_key(c) for c in ground_class}
    pred_set = {normalize_key(c) for c in gen_class}
    intersection = gold_set & pred_set
    only_gold = gold_set - pred_set
    only_pred = pred_set - gold_set

    lines.append("| | Count |")
    lines.append("|---|---:|")
    lines.append(f"| Gold ontology classes | {gold_count} |")
    lines.append(f"| Pred ontology classes | {pred_count} |")
    lines.append(f"|  Exact overlap (after normalization) | {len(intersection)} |")
    lines.append(f"| Only in gold | {len(only_gold)} |")
    lines.append(f"| Only in pred | {len(only_pred)} |")
    lines.append("")

  
    lines.append("### Class lists")
    lines.append("")
    lines.append(f"**Gold ({gold_count}):** "
                 f"{', '.join(f'`{c}`' for c in sorted(ground_class))}")
    lines.append("")
    lines.append(f"**Pred ({pred_count}):** "
                 f"{', '.join(f'`{c}`' for c in sorted(gen_class))}")
    lines.append("")

    lines.append("## Layer 2 — Per-Method Matching Results")
    lines.append("")
    lines.append("This layer reports each method's **standalone** "
                 "matching quality. Each method runs an independent "
                 "one-to-one greedy matching at its own conventional "
                 "threshold (hard_match 1.0; lexical methods such as "
                 "jaro_winkler, levenshtein, and sequence_match at 0.8; "
                 "semantic at 0.6) and reports its own Precision, "
                 "Recall, and F1. These numbers are diagnostic only. ")
    lines.append("")
    lines.append("| Method | TP_gold | Coverage | Precision | Recall | F1 |")
    lines.append("|---|---:|---:|---:|---:|---:|")

    skip_keys = {"class_counts", "matching_rule", "thresholds", "synonym"}
    method_keys = [k for k in result if k not in skip_keys]

    for method in method_keys:
        r = result[method]
        if not isinstance(r, dict):
            continue
        cov = r.get("coverage", 0.0)
        p = r.get("precision", 0.0)
        rec = r.get("recall", 0.0)
        f1 = r.get("f1", 0.0)
        tp_gold = int(round(rec * gold_count))
        cov_str = "—" if gold_count == 0 else f"{cov*100:.1f}%"
        p_str = "—" if pred_count == 0 else f"{p*100:.1f}%"
        rec_str = "—" if gold_count == 0 else f"{rec*100:.1f}%"
        f1_str = "—" if (gold_count == 0 or pred_count == 0) else f"{f1*100:.1f}%"
        lines.append(f"| `{method}` | {tp_gold}/{gold_count} | "
                     f"{cov_str} | {p_str} | {rec_str} | "
                     f"{f1_str} |")
    lines.append("")

    lines.append("## Layer 3 — Best Matching Alignment Table")
    lines.append("")
    lines.append(f"Final aligned (gold ↔ pred) pairs after combining all "
                 f"methods via **top-{top_n} averaging** of per-method "
                 f"scores, then 1-to-1 greedy selection.")
    if final_threshold > 0:
        lines.append(f"")
        lines.append(f"Threshold applied: **`final_threshold = "
                     f"{final_threshold}`** — pairs with averaged score "
                     f"below this are dropped (hard-match hits always "
                     f"pass).")
    else:
        lines.append("")
        lines.append("No threshold applied — every gold gets its best "
                     "candidate (subject to 1-to-1 conflict).")
    lines.append("")

    if not best_class_map:
        lines.append("_No alignments produced._")
    else:
        lines.append("| Gold class | Pred class | Method(s) | Score |")
        lines.append("|---|---|---|---:|")
        sorted_items = sorted(
            best_class_map.items(),
            key=lambda kv: -kv[1].get("score", 0.0),
        )
        for gold, info in sorted_items:
            pred = info.get("pred_term", "")
            method = info.get("matching_way", "")
            score = info.get("score", 0.0)
            lines.append(f"| `{gold}` | `{pred}` | {method} | "
                         f"{score:.4f} |")
    lines.append("")

    if best_class_map:
        n_aligned = len(best_class_map)
        used_preds = {info["pred_term"] for info in best_class_map.values()}
        tp = n_aligned
        fn = gold_count - n_aligned
        fp = pred_count - len(used_preds)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)
              if (precision + recall) else 0.0)

        lines.append("### Overall (Layer 3 — macro-level) Precision / Recall / F1")
        lines.append("")
        lines.append("All gold and pred classes are included in the calculation: "
             "unmatched gold classes count as FN, and unmatched pred "
             "classes count as FP.")
        lines.append("")
        lines.append("| Metric | Count | Definition |")
        lines.append("|---|---:|---|")
        lines.append(f"| TP | {tp} | Gold classes aligned to a pred class |")
        lines.append(f"| FN | {fn} | Gold classes with no pred match "
                     f"(no candidate met the threshold or all "
                     f"candidates were taken by stronger pairings) |")
        lines.append(f"| FP | {fp} | Pred classes with no gold match "
                     f"(no candidate met the threshold or pred was "
                     f"taken by a higher-scoring gold) |")
        lines.append("")
        p_str = f"**{precision*100:.1f}%** ({tp}/{tp+fp})" if (tp + fp) else "**—** (0/0)"
        r_str = f"**{recall*100:.1f}%** ({tp}/{tp+fn})" if (tp + fn) else "**—** (0/0)"
        f_str = f"**{f1*100:.1f}%**" if (tp + fp) and (tp + fn) else "**—**"
        lines.append("| Metric | Value |")
        lines.append("|---|---:|")
        lines.append(f"| Precision = TP / (TP + FP) | {p_str} |")
        lines.append(f"| Recall = TP / (TP + FN) | {r_str} |")
        lines.append(f"| F1 | {f_str} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("# Property-Level Label Matching Report")
    lines.append("")
    lines.append("_To be appended in a subsequent run for ObjectProperty "
                 "and DatatypeProperty matching._")
    lines.append("")

    return "\n".join(lines)


def save_class_report_md(report_text, output_path):

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\nClass-level matching report (Markdown) saved to: "
          f"{output_path}")


def get_parser():
    parser = argparse.ArgumentParser(
        description="Evaluation of generated ontology explicit classes with normalized one-to-one matching"
    )

    parser.add_argument(
        "--model_id",
        default="embeddinggemma",
        help="Ollama embedding model id; comma-separated for multiple",
        type=str
    )

    parser.add_argument(
        "--methods",
        default="hard_match,sequence_match,levenshtein,jaro_winkler,semantic,synonym",
        help=(
            "Comma-separated matching methods. "
            "Available: hard_match, sequence_match, levenshtein, jaro_winkler, semantic, synonym"
        ),
        type=str
    )

    parser.add_argument(
        "--generate_onto_file_path",
        help="path of generated ontology file",
        type=str,
        required=True
    )

    parser.add_argument(
        "--ground_onto_file_path",
        help="path of ground truth ontology file",
        type=str,
        required=True
    )

    parser.add_argument(
        "--save_file_path",
        help="path to save final metric result json",
        type=str
    )

    parser.add_argument(
        "--save_pairings_path",
        help="path to save matching results",
        type=str
    )

    parser.add_argument(
        "--save_tp_gold_to_pred_path",
        help="path to save merged TP-only gold->pred mapping json",
        type=str
    )

    parser.add_argument(
        "--save_tp_pred_to_gold_path",
        help="path to save merged TP-only pred->gold mapping json",
        type=str
    )

    parser.add_argument(
        "--save_best_class_map",
        help="path to save best class mapping gold -> best pred class as JSON",
        type=str
    )

    parser.add_argument(
        "--save_matching_csv",
        help="path to save CSV file with per-gold per-method matching results",
        type=str
    )

    parser.add_argument(
        "--save_best_matching_csv",
        help="path to save final best gold-pred matching as CSV",
        type=str
    )

    parser.add_argument(
        "--top_n",
        help="For each (gold, pred) candidate pair, average the top-N "
             "method scores and use that as the pair's combined score. "
             "Default: 3.",
        type=int,
        default=3
    )

    parser.add_argument(
        "--final_threshold",
        help="Minimum top-N averaged score for a pair to be retained. "
             "Applied AFTER aggregation, BEFORE 1-to-1 enforcement. "
             "Use 0.0 (default) to disable filtering — every gold gets a "
             "best-match candidate. Recommended values: 0.7 for strict "
             "matching (drops ~10 spurious matches on wine data, keeps "
             "all real ones), 0.6 for moderate, 0.5 for loose. "
             "Hard-match hits always pass (their score is 1.0).",
        type=float,
        default=0.0
    )

    parser.add_argument(
        "--save_alignment_trace_csv",
        help="path to save a detailed per-pair selection trace as CSV. "
             "Each row gives one candidate (gold, pred) pair with all "
             "method scores, top-N score average, whether it was "
             "selected, and (if not) why it was dropped.",
        type=str
    )

    parser.add_argument(
        "--save_alignment_trace_json",
        help="path to save the same per-pair selection trace as JSON "
             "(list-of-objects with id field). Same content as "
             "--save_alignment_trace_csv but easier to consume "
             "programmatically.",
        type=str
    )

    parser.add_argument(
        "--save_report_md",
        help="path to save a human-readable Markdown report covering "
             "Layer 1 (class statistics), Layer 2 (per-method P/R/F1), "
             "and Layer 3 (final best-matching alignment table). "
             "Includes a placeholder section for property-level results "
             "to be appended later.",
        type=str
    )

    return parser

def main():
    para_parser = get_parser()
    args = para_parser.parse_args()
    args_dict = vars(args)

    model_id = args_dict["model_id"]

    requested_methods = [
        m.strip()
        for m in args_dict["methods"].split(",")
        if m.strip()
    ]

    valid_methods = {
        "hard_match",
        "sequence_match",
        "levenshtein",
        "jaro_winkler",
        "semantic",
        "synonym"
    }

    for m in requested_methods:
        if m not in valid_methods:
            raise ValueError(
                f"Unsupported method '{m}'. "
                f"Available methods: {sorted(valid_methods)}"
            )

    print("===== EXTRACTING EXPLICIT CLASSES =====")

    gen_class = extract_classes(args_dict["generate_onto_file_path"])
    ground_class = extract_classes(args_dict["ground_onto_file_path"])

    print("\n===== CLASS COUNTS =====")
    print(f"Gold class count: {len(ground_class)}")
    print(f"Pred class count: {len(gen_class)}")

    print("\n===== EXTRACTED CLASSES RAW =====")
    print("Gold classes:")
    print(ground_class)

    print("\nPred classes:")
    print(gen_class)

    print("\n===== NORMALIZATION DUPLICATE CHECK =====")
    check_normalized_duplicates(ground_class, "gold classes", mode="key")
    check_normalized_duplicates(gen_class, "pred classes", mode="key")
    check_normalized_duplicates(ground_class, "gold classes", mode="text")
    check_normalized_duplicates(gen_class, "pred classes", mode="text")

    result = {
        "class_counts": {
            "gold_class_count": len(ground_class),
            "pred_class_count": len(gen_class)
        },
        "matching_rule": {
            "type": "normalized one-to-one global greedy matching",
            "description": (
                "All matching methods use normalized terms internally. "
                "Hard and lexical methods use normalize_key, where spaces are removed. "
                "Semantic and synonym methods use normalize_text, where word spaces are preserved. "
                "Each gold can match at most one pred. "
                "Each pred can match at most one gold. "
                "Pred terms are removed from the pool once matched. "
                "Only pairs above the method-specific threshold are considered."
            )
        },
        "thresholds": {
            "hard_match": HARD_THRESHOLD,
            "lexical": LEXICAL_THRESHOLD,
            "semantic": SEMANTIC_THRESHOLD,
            "synonym": 1.0
        }
    }

    all_gold_maps = {}
    all_pred_maps = {}

    print("\n===== RUNNING MATCHING METHODS =====")

    for info_type in requested_methods:
        if info_type == "synonym":
            coverage, precision, recall, f1, gold_map, pred_map = cal_synonym(
                gen_class,
                ground_class
            )

            result["synonym"] = {
                "coverage": coverage,
                "precision": precision,
                "recall": recall,
                "f1": f1
            }

            all_gold_maps["synonym"] = gold_map
            all_pred_maps["synonym"] = pred_map

        elif info_type == "semantic":
            for _model_id in model_id.split(","):
                _model_id = _model_id.strip()

                if not _model_id:
                    continue

                coverage, precision, recall, f1, gold_map, pred_map = cal_metrics(
                    gen_class,
                    ground_class,
                    info_type,
                    _model_id
                )

                info_id = f"{info_type}_{_model_id}"

                result[info_id] = {
                    "coverage": coverage,
                    "precision": precision,
                    "recall": recall,
                    "f1": f1
                }

                all_gold_maps[info_id] = gold_map
                all_pred_maps[info_id] = pred_map

        else:
            coverage, precision, recall, f1, gold_map, pred_map = cal_metrics(
                gen_class,
                ground_class,
                info_type
            )

            result[info_type] = {
                "coverage": coverage,
                "precision": precision,
                "recall": recall,
                "f1": f1
            }

            all_gold_maps[info_type] = gold_map
            all_pred_maps[info_type] = pred_map

    print("\n===== FINAL RESULTS =====")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args_dict.get("save_file_path"):

        config_keys = {"class_counts", "matching_rule", "thresholds"}
        result_for_save = {
            "config": {k: v for k, v in result.items() if k in config_keys},
            "results": _dict_to_list_of_objects(
                {k: v for k, v in result.items() if k not in config_keys}
            ),
        }
        with open(args_dict["save_file_path"], "w", encoding="utf-8") as f:
            json.dump(result_for_save, f, ensure_ascii=False, indent=4)
        print(f"\nMetric result saved to: {args_dict['save_file_path']}")

    if args_dict.get("save_pairings_path"):
        pairings_output = {}

        for info_type in result:
            if info_type in {"class_counts", "matching_rule", "thresholds"}:
                continue

            if info_type not in all_gold_maps:
                continue

            pairings_output[info_type] = {
                "gold_to_pred": list(all_gold_maps[info_type].values()),
                "pred_to_gold": list(all_pred_maps[info_type].values()),
            }

        save_all_pairings_to_json(pairings_output, args_dict["save_pairings_path"])
        print(f"\nBidirectional pairings saved to: {args_dict['save_pairings_path']}")

    if args_dict.get("save_tp_gold_to_pred_path"):
        tp_gold_to_pred_output = build_merged_tp_gold_to_pred(all_gold_maps)
        save_json(tp_gold_to_pred_output, args_dict["save_tp_gold_to_pred_path"])
        print(f"\nMerged TP Gold->Pred mapping saved to: {args_dict['save_tp_gold_to_pred_path']}")

    if args_dict.get("save_tp_pred_to_gold_path"):
        tp_pred_to_gold_output = build_merged_tp_pred_to_gold(all_pred_maps)
        save_json(tp_pred_to_gold_output, args_dict["save_tp_pred_to_gold_path"])
        print(f"\nMerged TP Pred->Gold mapping saved to: {args_dict['save_tp_pred_to_gold_path']}")

    best_class_map = None
    alignment_trace = None

    top_n = int(args_dict.get("top_n", 3))
    final_threshold = float(args_dict.get("final_threshold", 0.0))
    want_trace = bool(args_dict.get("save_alignment_trace_csv")) or \
                 bool(args_dict.get("save_alignment_trace_json"))

    if args_dict.get("save_best_class_map") or want_trace \
            or args_dict.get("save_best_matching_csv"):
        topn_eligible = [m for m in requested_methods if m != "synonym"]
        thr_str = (f", final_threshold={final_threshold}"
                   if final_threshold > 0 else ", no threshold")
        print(f"\n[main] Building best class map via top-{top_n} average"
              f"{thr_str} over methods: {topn_eligible}")
        all_score_tables = {}
        for info_type in topn_eligible:
            try:
                table = compute_full_score_table(
                    gen_class, ground_class, info_type,
                    model_id=model_id if info_type == "semantic" else None,
                )
                all_score_tables[info_type] = table
                print(f"  [{info_type}] full score table: "
                      f"{len(table)} entries")
            except Exception as e:
                print(f"  [{info_type}] skipped (failed to compute "
                      f"full table: {e})")

        topn_result = build_best_class_map_top_n(
            all_score_tables,
            top_n=top_n,
            final_threshold=final_threshold,
            return_trace=want_trace,
        )
        if want_trace:
            best_class_map, alignment_trace = topn_result
        else:
            best_class_map = topn_result

        if args_dict.get("save_best_class_map"):
            save_json(best_class_map, args_dict["save_best_class_map"])
            print(f"\nBest class mapping gold->pred saved to: "
                  f"{args_dict['save_best_class_map']}")

    if args_dict.get("save_best_matching_csv"):
        save_best_matching_csv(
            best_class_map,
            args_dict["save_best_matching_csv"]
        )

    if alignment_trace is not None:
        if args_dict.get("save_alignment_trace_csv"):
            save_alignment_trace_csv(alignment_trace,
                                     args_dict["save_alignment_trace_csv"])
        if args_dict.get("save_alignment_trace_json"):
            save_alignment_trace_json(alignment_trace,
                                      args_dict["save_alignment_trace_json"])

    if args_dict.get("save_matching_csv"):
        save_matching_csv(
            ground_class,
            all_gold_maps,
            args_dict["save_matching_csv"]
        )

    if args_dict.get("save_report_md"):
        if best_class_map is None:
            topn_eligible = [m for m in requested_methods if m != "synonym"]
            print(f"\n[main] (for report) Building best class map via "
                  f"top-{top_n} average...")
            all_score_tables = {}
            for info_type in topn_eligible:
                try:
                    all_score_tables[info_type] = compute_full_score_table(
                        gen_class, ground_class, info_type,
                        model_id=model_id if info_type == "semantic" else None,
                    )
                except Exception as e:
                    print(f"  [{info_type}] skipped: {e}")
            best_class_map = build_best_class_map_top_n(
                all_score_tables, top_n=top_n,
                final_threshold=final_threshold,
            )
        report_text = build_class_report_md(
            ground_class=ground_class,
            gen_class=gen_class,
            result=result,
            best_class_map=best_class_map,
            top_n=top_n,
            final_threshold=final_threshold,
            model_id=model_id,
        )
        save_class_report_md(report_text, args_dict["save_report_md"])


if __name__ == "__main__":
    main()
