# How to Use CQ4OE

CQ4OE is an evaluation pipeline. It does not generate ontologies for you. You bring the output from your LLM on one of our 6 domains, and CQ4OE compares it against the CQ-aligned gold standard and produces a Markdown report.

This guide walks you through:

1. installing and choosing which task to evaluate,
2. preparing your prediction files,
3. running the evaluation,
4. reading the report.

---

## 1. Install

Clone the repository and create a fresh Python environment.

```bash
git clone https://github.com/oeg-upm/cq4oe-benchmark.git
cd cq4oe-benchmark

conda create -n cq4oe python=3.10 -y
conda activate cq4oe
pip install -r requirements.txt
```

**Python version.** Tested on **Python 3.10**.

**External dependencies beyond `pip install`:**

- **Java**: needed by `owlready2` for HermiT reasoning in the hierarchy layer (CQ2Onto only). Check with `java -version`. If missing, install any modern JDK.
- **Ollama**: serves the embedding model used for term alignment. Install Ollama, then pull the model once:

  ```bash
  ollama pull embeddinggemma
  ```

  Make sure `ollama serve` is running before you launch the evaluation.

`requirements.txt` covers the Python packages:

```text
rdflib                  # OWL / RDF parsing
owlready2               # HermiT reasoner (CQ2Onto hierarchy)
python-Levenshtein      # edit distance
textdistance            # Jaro-Winkler etc.
sentence-transformers   # embedding similarity
langchain-ollama        # Ollama client
openpyxl                # XLSX export
```

---

## 2. Pick your task

CQ4OE has two evaluation tasks. **Pick one before going further.** The directory you `cd` into, the prediction format, and the runner script are all different.

| Task | What it evaluates | Input you provide | Output |
|---|---|---|---|
| **CQ2Term** | Whether your LLM predicts the **explicit classes and properties** required by each CQ | one JSON file per (model, dataset) listing predicted terms per CQ | term-level P/R/F1 + CQ-conditioned coverage |
| **CQ2Onto** | Whether your LLM produces a **full OWL ontology** that satisfies the CQs | one ontology file per (model, dataset) | five evaluation tasks + CQ-conditioned axiom coverage |

Supported formats for CQ2Onto: `.owl`, `.rdf`, `.xml`, `.ttl`, `.turtle` (anything `rdflib` can parse).

**Filename convention (important).** For CQ2Term and CQ2Onto , each prediction file must start with the dataset name (e.g. wine_*.owl, awo_*.owl). The runner uses this prefix to find the matching gold.**

Quick rules of thumb:

- Use **CQ2Term** if you only want to test the ability of model to recognize/recover the relevant vocabulary for each CQ.
- Use **CQ2Onto** if you want to evaluate a complete generated ontology, including property semantics, triples, hierarchy, and axioms.
- You can run **both** on the same model. Just go through each section in turn.

## 3. CQ2Term: term-level evaluation

### 3.1 Folder structure

```
CQ2Term/
├── 00_gold_standard/          ← read-only; per-domain CQ-to-term provenance
│   └── <domain>/
│       ├── cq_to_terms_<domain>.json
│       └── term_to_cqs_<domain>.json
├── 01_predictions/
│   └── <model_name>/          ← any label (e.g. Claude, baseline, default)
│       └── <domain>_terms.json
├── 03_evaluation_results/
├── 04_summary/
├── competency_question/        ← raw CQs per domain
└── scripts/
    ├── concept_label_matching.py
    ├── eval_cq_terms.py
    └── run_all_cq2term.py
```

The six available domains are: `wine`, `awo`, `odrl`, `water`, `vgo`, `swo`.

### 3.2 Generate predictions

For each model and each domain you want to evaluate:

1. Read the CQs from `competency_question/<domain>_cqs.json`.
2. For each CQ, predict the required classes and properties with your LLM.
3. Save as JSON in the same format as `00_gold_standard/<domain>/cq_to_terms_<domain>.json`.

Place predictions one folder per model:

```
01_predictions/
└── my_model/                  ← any name; used as the label in reports
    ├── wine_terms.json
    ├── awo_terms.json
    ├── odrl_terms.json
    ├── water_terms.json
    ├── vgo_terms.json
    └── swo_terms.json
```

The `<model_name>` folder works as a label. Use any name like `Claude`, `baseline`, or `default`. This name becomes the directory under `03_evaluation_results/` and `04_summary/`. The folder layer is required. JSON files placed directly under `01_predictions/` will not be picked up.

### 3.3 Configure and run

Open `CQ2Term/scripts/run_all_cq2term.py` and edit one constant at the top:

```python
PYTHON = "/path/to/your/python"   # run `which python` inside your cq4oe env
```

Then run from the `CQ2Term/` directory:

```bash
cd CQ2Term
python -u scripts/run_all_cq2term.py
```

The runner scans each folder under `01_predictions/` and pairs it with each domain in `DATASETS = ["wine", "vgo", "swo", "awo", "odrl", "water"]`. It runs `eval_cq_terms.py` when both files exist, and prints SKIP otherwise. No per-run edits needed. Drop your model folder into `01_predictions/` and the runner picks it up.

### 3.4 Inspect the outputs

After a run, each (model, dataset) pair produces:

```
03_evaluation_results/<model>/<dataset>/06_cq_terms/
├── eval_cq_terms_result.json          ← P/R/F1 summary
├── cqterm_class_best_matching.csv     ← accepted class alignment
├── cqterm_prop_best_matching.csv      ← accepted property alignment
├── cqterm_class_trace.csv             ← per-method similarity scores (classes)
├── cqterm_prop_trace.csv              ← per-method similarity scores (properties)
├── cq_coverage.csv                    ← per-CQ coverage (At-least-one / Mean / Full)
└── term_coverage.csv                  ← per-term coverage

**Read the Markdown report first.** The JSON and CSV files under `03_evaluation_results/` hold the raw numbers if you want to do your own analysis. Different runs do not overwrite each other.
```

### 3.5 Run a single (model, dataset) pair

Call `eval_cq_terms.py` directly when you want to rerun one pair without invoking the full runner. Useful for debugging or for adjusting parameters like the similarity threshold.

The dataset name (`wine` in the example below) lives in the file paths. To switch to a different dataset, replace `wine` with `awo`, `odrl`, `water`, `vgo`, or `swo`.

```bash
cd CQ2Term
python scripts/eval_cq_terms.py \
  --gold_cq_to_terms 00_gold_standard/wine/cq_to_terms_wine.json \
  --pred_cq_to_terms 01_predictions/my_model/wine_terms.json \
  --final_threshold 0.6 \
  --save_result_json 03_evaluation_results/my_model/wine/06_cq_terms/eval_cq_terms_result.json \
  --save_report_md   04_summary/my_model/wine_report.md
```
Optionally override the per-method similarity thresholds with `--hard_threshold` (default `1.0`), `--lexical_threshold` (default `0.8`), and `--semantic_threshold` (default `0.6`).
---

## 4. CQ2Onto: full-ontology evaluation

### 4.1 Folder structure

```
CQ2Onto/
├── 00_gold_standard/           ← read-only
│   └── <domain>/
│       ├── ontology/sub_<domain>.owl         ← CQ-aligned gold ontology
│       └── axioms/<domain>_axiom_gold.json   ← TBox axioms with CQ provenance
├── 01_predictions/             ← drop your generated ontology files here
│   └── <mode>/                 ← agent / normal / cqbycq (your generation strategy)
│       └── <model_name>/       ← any label (e.g. deepseek-v4-pro, gpt4)
│           └── ontology/
│               ├── wine_*.owl          ← filename must start with the dataset
│               ├── awo_*.owl
│               ├── odrl_*.owl
│               ├── water_*.owl
│               ├── vgo_*.owl
│               └── swo_*.owl
├── 02_atomic_axioms/           ← intermediate axiom decomposition
├── 03_evaluation_results/      ← per-layer raw scores (CSV / JSON)
├── 04_summary/                 ← Markdown reports
├── competency_question/        ← raw CQs per domain
├── prompts/                    ← prompts used in the paper (cqbycq, MASEO)
└── scripts/
    ├── concept/eval_concept.py
    ├── property/eval_property.py
    ├── triple/eval_triple.py
    ├── axioms/Axioms_atomic.py
    ├── axioms/eval_axioms.py
    ├── hierarchy/eval_hierarchy.py
    └── run_all_evaluation_agent_datasets.py
```

The runner expects the three-level layout `01_predictions/<mode>/<model_name>/ontology/<dataset>_*.owl`. If you only have one mode and one model, still create those two layers (`01_predictions/single/my_model/ontology/wine_*.owl`).

### 4.2 Choose your scope

You decide how many (mode, model, domain) combinations to test. The runner **automatically discovers** each prediction file under `01_predictions/<mode>/<model>/ontology/` and evaluates it against its matching gold standard.

- One domain: drop one ontology file (e.g. `wine_my_model.owl`) into `01_predictions/single/my_model/ontology/`. One report comes out.
- Multiple domains, one model: drop six files (`wine_*.owl`, `awo_*.owl`, …) into the same `ontology/` folder. The runner evaluates each one.
- Multiple models, multiple domains: create one `<model_name>/` subfolder per model. The runner walks all of them.
- Multiple generation strategies: use the top-level `<mode>/` layer (`agent` vs `cqbycq` vs `normal`). The runner walks all modes that exist.

Supported formats: `.owl`, `.rdf`, `.xml`, `.ttl`, `.turtle` (anything `rdflib` can parse).

Partial benchmarks are valid (e.g. Wine + AWO only). Just report which domains you ran. To match the numbers in the CQ4OE paper, run all six.

Common situations:

- Testing a prompt change on one domain: one file in one model folder, one run.
- Comparing two models on Wine: two model folders each with `wine_*.owl`, one run.
- Comparing agent vs cqbycq strategies: two mode folders, one run.
- Full benchmark on a new LLM: one model folder with all six `<dataset>_*.owl` files, one run.

### 4.3 Generate predictions

For each (mode, model, domain) combination you want to evaluate:

1. Read the CQs from `CQ2Onto/competency_question/<domain>_cqs.json` (some domains use `<domain>_cq2onto_cqs.json`).
2. Feed them to your LLM under any generation strategy (one-shot, CQ-by-CQ, multi-agent, …). Prompts used in the paper are under `CQ2Onto/prompts/` if you want to reproduce them.
3. Save the result as one ontology file per domain (`.owl`, `.rdf`, `.xml`, `.ttl`, or `.turtle`).
4. **Name the file so it starts with the dataset**: `wine_my_run.owl`, `awo_v2.owl`, `vgo_cq2onto_output.owl`. The dataset prefix is how the runner identifies which gold to compare against.

Place the file under `01_predictions/<mode>/<model_name>/ontology/`:

```
01_predictions/
└── agent/                          ← generation mode (must match MODES in runner)
    └── my_model/                   ← any model label (used verbatim in outputs)
        └── ontology/
            ├── wine_agent_ontology.owl
            ├── awo_agent_ontology.owl
            └── vgo_cq2onto_agent_ontology.owl
```

The `<mode>` layer must match one of the names in `MODES` at the top of the runner (default: `agent`, `normal`, `cqbycq`). To use a different name, edit `MODES`. The `<model_name>` layer can be anything (e.g. `gpt4`, `deepseek-v3`); it is auto-discovered and used verbatim as the folder name in `03_evaluation_results/` and `04_summary/`.

### 4.4 Configure the runner

Open `scripts/run_all_evaluation_agent_datsets.py`. Edit only what you need:

```python
PYTHON  = "/path/to/your/python"        # required: which Python to use
MODES   = ["agent", "normal", "cqbycq"]  # which mode folders to scan
DATASETS = ["wine", "vgo", "swo", "awo", "odrl", "water"]  # whitelist
```

| Constant | What to put | Notes |
|---|---|---|
| `PYTHON` | absolute path to the Python in your `cq4oe` env | run `which python` inside the env |
| `MODES` | list of mode subfolders to scan under `01_predictions/` | remove items you don't have, e.g. `["normal"]` if you only have one mode |
| `DATASETS` | the six benchmark domains | shouldn't need to change unless adding a new domain |

The runner **does not** need you to specify which file to evaluate. It walks `01_predictions/<mode>/<model>/ontology/`, picks each `.owl` file, infers the dataset from the filename prefix, and runs the full pipeline. Missing modes are skipped with a SKIP message.

**Optional arguements inside the runner.** Two kinds of parameters are passed to the underlying scripts and can be edited inline in the relevant `run([...])` blocks:

- **Per-method thresholds** (passed to `eval_concept.py` and `eval_property.py`):
  - `--hard_threshold` (default `1.0`)
  - `--lexical_threshold` (default `0.8`)
  - `--semantic_threshold` (default `0.6`)

- **Layer-2 cosine threshold** (passed to `eval_triple.py`; `eval_axioms.py` has it too but its Layer 2 is disabled by `--no_layer2`):
  - `--threshold` (default `0.6`). Controls the cosine-similarity cutoff used by the embedding-based Layer 2 in the triple evaluation. Raise to be stricter, lower to be looser.

- **Datatype relaxation** (passed to `eval_triple.py` and `eval_axioms.py`):
  - `--literal_relax yes` or `no` (default in the shipped runner: `no`)

When `--literal_relax yes`, a generic literal root in the gold (`rdfs:Literal`, `xsd:anySimpleType`, `xsd:anyAtomicType`) matches any concrete `xsd:*` or `rdf:*` datatype in the prediction, treating a concrete prediction as a sound specialization of a generic gold. Set to `no` to keep strict equality (matches the numbers in the paper's strict configuration).

### 4.5 Run the evaluation

From the `CQ2Onto/` directory.

```bash
cd CQ2Onto
python -u scripts/run_all_evaluation_agent_datasets.py
```

The script runs five evaluation layers in order.

1. **Concept** (`scripts/concept/eval_concept.py`). Class alignment and recovery.
2. **Property** (`scripts/property/eval_property.py`). Property alignment and recovery.
3. **Triple** (`scripts/triple/eval_triple.py`). Domain / range triple match.
4. **Axioms** (`scripts/axioms/Axioms_atomic.py`, then `scripts/axioms/eval_axioms.py`). The first decomposes your prediction into atomic TBox axioms. The second compares them to the gold axioms with CQ provenance.
5. **Hierarchy** (`scripts/hierarchy/eval_hierarchy.py`). Reasoner-based closure recovery (needs Java).

If any layer fails the script stops. A successful run means all five layers completed.

### 4.6 Run individual layers

The five layers are independent scripts and can be run on their own. Useful for debugging or for re-running one part without redoing the whole pipeline.

**Hard dependency.** The last three layers (`triple`, `axioms`, `hierarchy`) require the alignment CSVs produced by `concept` and `property`. Required order:

1. `concept` (produces `class_best_matching.csv`)
2. `property` (produces `property_best_matching.csv`)
3. `triple`, `axioms`, `hierarchy` (all three read the two CSVs above)

After `concept` and `property` finish you have:

```
03_evaluation_results/<mode>/<model>/<dataset>/01_class/class_best_matching.csv
03_evaluation_results/<mode>/<model>/<dataset>/02_property/property_best_matching.csv
```

These two CSVs are read by the later layers through `--class_csv` and `--property_csv`.

**Example: run only the triple layer on Wine.** This example assumes you already ran concept and property for the `agent / my_model` configuration. Replace `my_model` with your actual model folder name:

```bash
python scripts/triple/eval_triple.py \
  --pred_onto 01_predictions/agent/my_model/ontology/wine_agent_ontology.owl \
  --gold_onto 00_gold_standard/wine/ontology/sub_wine.owl \
  --class_csv    03_evaluation_results/agent/my_model/wine/01_class/class_best_matching.csv \
  --property_csv 03_evaluation_results/agent/my_model/wine/02_property/property_best_matching.csv \
  --save_result      03_evaluation_results/agent/my_model/wine/03_triple/triple_result.json \
  --save_layer3_csv  03_evaluation_results/agent/my_model/wine/03_triple/triple_layer3_pairs.csv \
  --save_layer3_json 03_evaluation_results/agent/my_model/wine/03_triple/triple_layer3_pairs.json \
  --save_report_md   04_summary/agent/my_model/wine_report.md \
  --literal_relax    no
```

To run a different layer, open `run_all_evaluation_agent_datasets.py` and copy the relevant `run([...])` block; that block lists exactly the arguments that layer's script accepts.

**Skipping concept or property is not allowed.** Running any of `triple` / `axioms` / `hierarchy` without those two CSVs will fail.

### 4.7 Inspect the outputs

After a successful run, the outputs follow the same `<mode>/<model>/<dataset>/` layout as the predictions:

```
02_atomic_axioms/<mode>/<model>/<dataset>/
└── <pred_stem>_atomic_tbox.json        ← your prediction in atomic-TBox form
03_evaluation_results/<mode>/<model>/<dataset>/
├── 01_class/
│   ├── class_result.json               ← per-method P/R/F1 (raw)
│   ├── class_best_matching.csv         ← final gold↔pred alignment (used by later layers)
│   ├── class_alignment_trace.csv       ← per-pair scoring trace
│   └── class_alignment_trace.json      ← same trace, JSON form
├── 02_property/
│   ├── property_result.json            ← per-method + characteristics raw results
│   ├── property_best_matching.csv      ← final gold↔pred alignment (used by later layers)
│   ├── property_alignment_trace.csv
│   └── property_alignment_trace.json
├── 03_triple/
│   ├── triple_result.json              ← layer 1-4 raw results
│   ├── triple_layer3_pairs.csv         ← per-aligned-pair domain/range verdicts
│   └── triple_layer3_pairs.json
├── 04_axiom/
│   ├── eval_axioms_result.json         ← strict TBox matching raw results
│   ├── axiom_details.csv               ← per-axiom verdict (TP/FP/FN/mismatch)
│   └── strict_cq_coverage.csv          ← per-CQ axiom recovery
└── 05_hierarchy/
├── hierarchy_result.json           ← closure-based P/R/F1
└── hierarchy_pairs.csv             ← per-pair subsumption verdicts
04_summary/<mode>/<model>/<dataset>_report.md   ← read this first
```

For example, evaluating `01_predictions/agent/my_model/ontology/wine_agent_ontology.owl` produces `04_summary/agent/my_model/wine_report.md`.

**Read the Markdown report first.** It aggregates all five layers in one place, with per-CQ traces of what was matched, what was missed, and what was rescued through reasoning. The JSON and CSV files under `03_evaluation_results/` hold the raw numbers if you want to do your own analysis. Different runs do not overwrite each other, so you can compare models or strategies side by side.

---

## 5. Read the gold standards directly (no evaluation)

If you only want to inspect the requirements, skip the runner and go straight to the gold files.

**CQ2Term.** `CQ2Term/00_gold_standard/<domain>/cq_to_terms_<domain>.json` records the CQ-to-term provenance. For each CQ you get the explicit classes and properties required to answer it.

**CQ2Onto.** `CQ2Onto/00_gold_standard/<domain>/` contains:

- `ontology/sub_<domain>.owl`: the CQ-aligned sub-ontology produced by Phase 4 of the annotation pipeline.
- `axioms/<domain>_axiom_gold.json`: TBox axioms with CQ-to-axiom provenance.

These are exactly what the evaluation pipeline compares against. Anything you read here is what your model is graded on.

---

## 6. Interpret the metrics

Each layer reports **TP, FP, FN, Precision, Recall, F1**. F1 is the headline; Precision and Recall tell you the failure mode (low P + high R = over-generates; high P + low R = too conservative).

**What each layer measures:**

- **Class / Property**: P/R/F1 between gold and predicted terms after one-to-one alignment over five similarity methods (top-3 mean).
- **Property characteristics** *(CQ2Onto)*: P/R/F1 over OWL flags (functional, inverse, transitive, …).
- **Domain / range triples** *(CQ2Onto)*: P/R/F1 over `(subject, predicate, object)` triples from `rdfs:domain` / `rdfs:range`.
- **TBox axioms** *(CQ2Onto)*: P/R/F1 over strict axiom matches after term translation.
- **Hierarchy closure** *(CQ2Onto)*: P/R/F1 over inferred subsumptions (entailed, not just asserted).

**Two views (CQ2Onto):**

- *Global*: over all gold and predicted items.
- *AC (Alignment-Conditioned)*: restricted to items whose terms aligned, isolating structural mistakes from vocabulary mistakes.

**CQ-conditioned coverage.** Per CQ-level target: *At-least-one*, *Mean*, *Full*. For axioms, reported twice (`Axioms-…` before closure rescue, `Closure-…` after); comparing the two shows how much was rescued by reasoning.

**Datatype literal relaxation** *(triple and axiom layers)*. With `--literal_relax yes`, a generic literal root in the gold (`rdfs:Literal`, `xsd:anySimpleType`, `xsd:anyAtomicType`) matches any concrete `xsd:*` or `rdf:*` datatype in the prediction. With `no` (default), strict equality only. Reverse direction (pred broader than gold) is never relaxed.

---
