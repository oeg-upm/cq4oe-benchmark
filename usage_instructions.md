# How to Use CQ4OE

CQ4OE is an evaluation pipeline. It does not generate ontologies for you. You bring the output from your LLM on one of the 6 domains, and CQ4OE compares it against the CQ-aligned gold standard and produces a Markdown report.

This guide walks you through:

1. installing and choosing which task to evaluate
2. preparing your prediction files
3. running the evaluation
4. reading the report

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

Python 3.10 is tested.

External dependencies beyond `pip install`.

- **Java**. Needed by `owlready2` for HermiT reasoning in the hierarchy layer (CQ2Onto only). Check with `java -version`. Install any modern JDK if missing.
- **Ollama**. Serves the embedding model used for term alignment. Install Ollama, then pull the model once.

  ```bash
  ollama pull embeddinggemma
  ```

  Make sure `ollama serve` is running before you launch the evaluation.

`requirements.txt` covers the Python packages.

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

CQ4OE has two evaluation tasks. Pick one before going further. The directory you `cd` into, the prediction format, and the runner script are all different.

| Task | What it evaluates | Input you provide | Output |
|---|---|---|---|
| **CQ2Term** | Whether your LLM predicts the explicit classes and properties required by a CQ | one JSON file per (model, dataset) listing predicted terms per CQ | term-level P/R/F1 plus CQ-conditioned coverage |
| **CQ2Onto** | Whether your LLM produces a full OWL ontology that satisfies the CQs | one ontology file per (model, dataset) | five evaluation targets plus CQ-conditioned axiom coverage |

Supported formats for CQ2Onto. `.owl`, `.rdf`, `.xml`, `.ttl`, `.turtle` (anything `rdflib` can parse).

**Filename convention**. Prediction files must start with the dataset name (e.g. `wine_*.owl`, `awo_*.owl`). The runner uses this prefix to find the matching gold.

Quick rules of thumb.

- Use **CQ2Term** to test the ability of a model to recognize the relevant vocabulary for a CQ.
- Use **CQ2Onto** to evaluate a complete generated ontology, including property semantics, triples, hierarchy, and axioms.
- You can run both on the same model. Just go through the relevant section in turn.

---

## 3. CQ2Term

### 3.1 Folder structure

```
CQ2Term/
├── 00_gold_standard/<domain>/{cq_to_terms_<domain>.json, term_to_cqs_<domain>.json}
├── 01_predictions/<model_name>/<domain>_terms.json
├── 03_evaluation_results/
├── 04_summary/
├── competency_question/
└── scripts/{concept_label_matching.py, eval_cq_terms.py, run_all_cq2term.py}
```

The six available domains are `wine`, `awo`, `odrl`, `water`, `vgo`, `swo`.

### 3.2 Generate predictions

For a (model, domain) you want to evaluate:

1. Read the CQs from `competency_question/<domain>_cqs.json`.
2. Predict the required classes and properties per CQ with your LLM.
3. Save as JSON in the same format as `00_gold_standard/<domain>/cq_to_terms_<domain>.json`.

Place predictions one folder per model.

```
01_predictions/
└── my_model/                  ← any name, used as the label in reports
    ├── wine_terms.json
    ├── awo_terms.json
    └── ...
```

The `<model_name>` folder is required. JSON placed directly under `01_predictions/` is ignored.

### 3.3 Configure and run

Open `CQ2Term/scripts/run_all_cq2term.py` and edit the `PYTHON` path at the top.

```python
PYTHON = "/path/to/your/python"   # run `which python` inside your cq4oe env
```

Standard call.

```bash
cd CQ2Term
python -u scripts/run_all_cq2term.py
```

CLI flags.

| Flag | Effect |
|---|---|
| `--models my_model` | Only evaluate the named model folder(s). Default. All folders under `01_predictions/`. |
| `--datasets wine,awo` | Only evaluate the named datasets. Default. All six. |
| `--no_leaderboard` | Do not call `build_leaderboard.py` after the evaluation. |

Examples.

```bash
# Only my model, only wine
python -u scripts/run_all_cq2term.py --models my_model --datasets wine

# All models, all datasets, no leaderboard refresh
python -u scripts/run_all_cq2term.py --no_leaderboard
```

A successful run finishes by refreshing the leaderboard at `../leaderboard/`.

### 3.4 Outputs

```
03_evaluation_results/<model>/<dataset>/06_cq_terms/
├── eval_cq_terms_result.json
├── cqterm_class_best_matching.csv
├── cqterm_prop_best_matching.csv
├── cqterm_class_trace.csv
├── cqterm_prop_trace.csv
├── cq_coverage.csv
└── term_coverage.csv

04_summary/<model>/<dataset>_report.md   ← read first
```

Different runs do not overwrite the previous result.

### 3.5 Single (model, dataset) call

```bash
cd CQ2Term
python scripts/eval_cq_terms.py \
  --gold_cq_to_terms 00_gold_standard/wine/cq_to_terms_wine.json \
  --pred_cq_to_terms 01_predictions/my_model/wine_terms.json \
  --final_threshold 0.6 \
  --save_result_json 03_evaluation_results/my_model/wine/06_cq_terms/eval_cq_terms_result.json \
  --save_report_md   04_summary/my_model/wine_report.md
```

Optional. `--hard_threshold 1.0`, `--lexical_threshold 0.8`, `--semantic_threshold 0.6`.

---

## 4. CQ2Onto

### 4.1 Folder structure

```
CQ2Onto/
├── 00_gold_standard/<domain>/{ontology/sub_<domain>.owl, axioms/<domain>_axiom_gold.json}
├── 01_predictions/<mode>/<model_name>/ontology/<dataset>_*.owl
├── 02_atomic_axioms/
├── 03_evaluation_results/
├── 04_summary/
├── competency_question/
├── prompts/
└── scripts/{concept,property,triple,axioms,hierarchy}/...
   + scripts/run_all_evaluation_agent_datsets.py
```

The three-level path `01_predictions/<mode>/<model>/ontology/` is required. With one mode and one model, still create both layers (e.g. `01_predictions/mymodel/mymethod/ontology/`).

> **Class and Property are mandatory.** Triple, TBox Axioms, and Hierarchy Closure all read `class_best_matching.csv` and `property_best_matching.csv`. Skipping the first two layers breaks the rest.

### 4.2 Choose your scope

You decide how many (mode, model, domain) combinations to test. The runner discovers a prediction file under `01_predictions/<mode>/<model>/ontology/` and evaluates it against its matching gold standard.

- One domain. Drop one ontology file (e.g. `wine_my_model.owl`).
- Multiple domains, one model. Drop six files into the same `ontology/` folder.
- Multiple models. One `<model_name>/` subfolder per model under a `<mode>/`.
- Multiple generation strategies. Use multiple `<mode>/` top folders.

Supported formats. `.owl`, `.rdf`, `.xml`, `.ttl`, `.turtle`.

Partial benchmarks are valid (e.g. Wine plus AWO only). Just report which domains you ran.

### 4.3 Prepare predictions

For a (mode, model, domain):

1. Read CQs from `competency_question/<domain>_cqs.json`. Prompts used in the paper are in `prompts/`.
2. Generate the ontology with your LLM.
3. Save with a filename starting with the dataset (`wine_my_run.owl`).
4. Place under `01_predictions/<mode>/<model>/ontology/`.

```
01_predictions/
└── agent/                          ← generation mode
    └── my_model/                   ← any model label
        └── ontology/
            ├── wine_agent_ontology.owl
            └── awo_agent_ontology.owl
```

The `<mode>` layer must match one of the names in `MODES` at the top of the runner. Edit `MODES` to add your own.

### 4.4 Configure the runner

Edit the top of `scripts/run_all_evaluation_agent_datsets.py`.

```python
PYTHON  = "/path/to/your/python"
MODES   = ["agent", "normal", "cqbycq"]
DATASETS = ["wine", "vgo", "swo", "awo", "odrl", "water"]
```
Tunable arguments (edit inline in the `run([...])` blocks).

| Flag | Default | Effect |
|---|---|---|
| `--top_n` | `3` | Number of top non-hard methods averaged into the aggregated score s(tg, tp). `5` averages all, `1` keeps the single best. |
| `--final_threshold` | `0.6` class, `0.7` property | Cutoff for accepted candidate pairs. Higher means stricter, more precision, less recall. |
| `--hard_threshold`, `--lexical_threshold`, `--semantic_threshold` | `1.0`, `0.8`, `0.6` | Cutoffs for the standalone per-method P/R/F1 reports. |
| `--threshold` (triple) | `0.6` | Cosine cutoff for the Layer 2 embedding fallback in `eval_triple.py`. |
| `--literal_relax` | `no` | `yes` lets a generic gold literal match any concrete pred datatype. |

The shipped runner matches the paper baseline. Changing any value here puts the resulting runs in a new configuration group on the leaderboard.


### 4.5 Run the evaluation

Standard call.

```bash
cd CQ2Onto
python -u scripts/run_all_evaluation_agent_datsets.py
```

Five targets run in order. Class, Property, Triple, TBox Axioms, Hierarchy Closure. A successful run finishes by refreshing the leaderboard.

CLI flags.

| Flag | Effect |
|---|---|
| `--modes mymodel` | Only walk these mode folders. Default. All names in `MODES`. |
| `--layers concept,property` | Only run these layers. Accepted. `concept`, `property`, `triple`, `axioms`, `hierarchy`. |
| `--no_leaderboard` | Do not call `build_leaderboard.py` after the evaluation. |

Examples.

```bash
# Only my own model
python -u scripts/run_all_evaluation_agent_datsets.py --modes mymodel

# Only term-level layers (fastest, no Java needed)
python -u scripts/run_all_evaluation_agent_datsets.py --layers concept,property

# Re-run only axioms after a config change
python -u scripts/run_all_evaluation_agent_datsets.py --layers axioms --no_leaderboard
```

Downstream layers need the alignment CSVs from concept and property. The runner refuses with a clear error if the pre-alignment files are missing.

### 4.6 Evaluate a single domain

Drop only one prediction file. The other five datasets are skipped with `SKIP <dataset>: missing pred owl`. The leaderboard shows the run with Domain Coverage `1/6 ⚠`.

```bash
mkdir -p CQ2Onto/01_predictions/mymodel/my_run/ontology
cp wine_my_run.owl CQ2Onto/01_predictions/mymodel/my_run/ontology/
cd CQ2Onto
python -u scripts/run_all_evaluation_agent_datsets.py --modes mymodel
```

### 4.7 Inspect and fix alignments before running downstream layers

The Class and Property layers produce two CSVs (`class_best_matching.csv` and `property_best_matching.csv`) that downstream layers read. The automatic alignment can be wrong (LLM picked a near-synonym, two pred classes equally close, etc.) and the mistake then propagates into Triple, Axioms, and Hierarchy.

There are two ways to inspect alignments before downstream layers commit to them.

**Option A. Trace-only dry-run.** Call the layer script with only `--save_alignment_trace_*` and skip the other `--save_*` flags that write evaluation output. The script still computes a score for each candidate so you can read the trace, but it does not produce a `best_matching.csv` or metric JSON. Useful for quick parameter sweeps.

```bash
python scripts/concept/eval_concept.py \
  --generate_onto_file_path 01_predictions/mymodel/my_run/ontology/wine_my_run.owl \
  --ground_onto_file_path 00_gold_standard/wine/ontology/sub_wine.owl \
  --model_id embeddinggemma \
  --methods "hard_match,sequence_match,levenshtein,jaro_winkler,semantic" \
  --top_n 3 \
  --final_threshold 0.6 \
  --save_alignment_trace_csv  /tmp/wine_class_trace.csv \
  --save_alignment_trace_json /tmp/wine_class_trace.json
```

Open the trace, decide whether `--top_n`, `--final_threshold`, or the per-method thresholds need adjustment, then move on to the staged run.

**Option B. Staged run with hand edits.** Run the full pipeline in two phases. Edit the produced `best_matching.csv` between phases.

1. Run only the first two layers.
   ```bash
   python scripts/run_all_evaluation_agent_datsets.py --modes mymodel --layers concept,property
   ```
2. Open `03_evaluation_results/<mode>/<model>/<dataset>/01_class/class_best_matching.csv` and the property equivalent. Use the trace files next to them (`*_alignment_trace.csv` and `*_alignment_trace.json`) to see candidate pairs, all five method scores, and the selection reason.
3. Edit the `*_best_matching.csv` by hand. Replace a wrong `Pre_term`, or delete a row when no real match exists.
4. Run the rest. Downstream layers read your edited CSVs.
   ```bash
   python scripts/run_all_evaluation_agent_datsets.py --modes mymodel --layers triple,atomic,axioms,hierarchy
   ```
5. The leaderboard refresh happens automatically at the end of step 4.

### 4.8 Single-layer call (advanced)

For sweeping one argument. Example for Triple on Wine (assumes alignment CSVs exist).

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

For the exact arg list of any layer, open the matching `run([...])` block in the runner.

### 4.9 Outputs

```
03_evaluation_results/<mode>/<model>/<dataset>/
├── 01_class/{class_result.json, class_best_matching.csv, class_alignment_trace.{csv,json}}
├── 02_property/{property_result.json, property_best_matching.csv, property_alignment_trace.{csv,json}}
├── 03_triple/{triple_result.json, triple_layer3_pairs.{csv,json}}
├── 04_axiom/{eval_axioms_result.json, axiom_details.csv, strict_cq_coverage.csv}
└── 05_hierarchy/{hierarchy_result.json, hierarchy_pairs.csv}

04_summary/<mode>/<model>/<dataset>_report.md   ← read first
```

Different runs do not overwrite previous results.

---

## 5. Read the gold standards directly

- **CQ2Term.** `CQ2Term/00_gold_standard/<domain>/cq_to_terms_<domain>.json`. Required classes and properties per CQ.
- **CQ2Onto.** `CQ2Onto/00_gold_standard/<domain>/ontology/sub_<domain>.owl` is the CQ-aligned sub-ontology. The matching `axioms/<domain>_axiom_gold.json` lists TBox axioms with CQ provenance.

---

## 6. Metrics

Each layer reports **TP, FP, FN, P, R, F1**. F1 is the headline. Low P with high R means over-generation, high P with low R means too conservative.

**Layer measures.**

- **Class / Property.** Term P/R/F1 after a top-3 mean over five similarity methods.
- **AggregatedTop3.** Mean over the alignment trace of the per-pair score s(tg, tp), where s = 1 when hard match is exact and the mean of the three highest non-hard similarity scores otherwise. Reports the overall alignment landscape across all candidate pairs, not just those passing the threshold.
- **Property characteristics** (CQ2Onto). OWL flags (functional, inverse, etc.).
- **Triple** (CQ2Onto). `(subject, predicate, object)` from `rdfs:domain` and `rdfs:range`.
- **TBox axioms** (CQ2Onto). Strict axiom match after term translation.
- **Hierarchy closure** (CQ2Onto). Inferred subsumptions, not just asserted.

**Two views (CQ2Onto).** *Global* over all items. *AC* (Alignment-Conditioned) restricted to aligned items, isolating structural mistakes from vocabulary mistakes.

**CQ-conditioned coverage.** *At-least-one*, *Mean*, *Full* per CQ. For axioms reported twice (`Axioms-...` before closure, `Closure-...` after). The gap shows how much was rescued by reasoning.

---

## 7. Leaderboard

### 7.1 Files

All files live in `leaderboard/` at the repo root, side by side. No subfolder.

- `leaderboard.html`. Interface.
- `leaderboard_data.js`. Data, regenerated by `build_leaderboard.py`.
- `leaderboard.md`. Top 10 per task.
- `cqs.html` + `cqs_data.js`. CQ browser.
- `index.html`. Landing page.
- `build_leaderboard.py`. Generator script.
- `backfill_legacy_cli_args.py`. One-off migration utility (see 7.6).

### 7.2 Refresh

The runners call `build_leaderboard.py` at the end of a successful run, so the standard workflow needs no extra step.

Manual refresh.

```bash
cd leaderboard
python build_leaderboard.py \
  --cq2term_root ../CQ2Term/03_evaluation_results \
  --cq2onto_root ../CQ2Onto/03_evaluation_results \
  --html_data    leaderboard_data.js \
  --markdown_out leaderboard.md
```

### 7.3 View

```bash
cd leaderboard
python3 -m http.server 8000
# http://127.0.0.1:8000/leaderboard.html
```

For online hosting, commit the contents of `leaderboard/` and enable GitHub Pages.

### 7.4 What you see

Three nav layers.

- **Task.** CQ2Term (99 CQs) or CQ2Onto (118 CQs).
- **Target.** Term Recovery for CQ2Term. For CQ2Onto, five targets (Term Recovery, Property Characteristics, Triple, TBox Axioms, Hierarchy Closure).
- **Domain.** Overall or one of Wine, AWO, ODRL, Water, VGO, SWO.

Table controls. Click a header to sort. ▶ on F1 columns splits into P, R, F1. ⋮ on aggregated Term Recovery splits into the five methods. Hover a cell for TP, FP, FN. Partial runs show `n/6 ⚠` in the Domain Coverage column.

### 7.5 Configuration grouping

Runs are grouped by the `config.cli_args` block in each result JSON. Same CLI args means same group, regardless of model. Any change (`--threshold`, `--literal_relax`, similarity method order, etc.) puts a run in a new group.

| Change between two runs | Effect |
|---|---|
| identical CLI args | same group |
| different `--literal_relax` | new group |
| different `--threshold` | new group |
| different similarity method order | new group |

The strict rule guarantees that two runs ranked against each other are reproducible against each other.

### 7.6 Backfilling legacy runs

Runs evaluated before the eval scripts were patched do not have a `config.cli_args` block in their result JSONs. Those runs end up in an "Unknown configuration" group and cannot be ranked against fresh runs.

The one-off migration utility writes the paper-baseline `cli_args` block into legacy JSONs, so they group with patched runs that share the same parameters.

```bash
cd leaderboard

# Preview without writing files
python backfill_legacy_cli_args.py ../CQ2Onto/03_evaluation_results --dry-run

# Apply the fix
python backfill_legacy_cli_args.py ../CQ2Onto/03_evaluation_results
```

The script is idempotent. JSONs that already have a `cli_args` block are skipped. Edit the `BASELINE` dict at the top of the script if your old runs used different defaults.

After backfill, regenerate the leaderboard. The legacy and fresh runs now share one configuration group.
