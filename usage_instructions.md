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
   + scripts/run_all_evaluation_agent_datasets.py
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

Edit the top of `scripts/run_all_evaluation_agent_datasets.py`.

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
| `--threshold` (triple, axiom) | `0.6` | Cosine cutoff for the Layer 2 embedding step. Both the triple and axiom evaluations have a Layer 2 (semantic embedding match); this sets its threshold in each. |
| `--literal_relax` | `no` | `yes` lets a generic gold literal match any concrete pred datatype. |
| `--no_layer2`| off by default, so Layer 2 is evaluated | Both the triple and axiom layers evaluate their Layer 2 (the embedding match) by default. This optional flag exists only for the triple and axiom layer and skips its Layer 2 when passed. |

The shipped runner matches the paper baseline. Changing any value here puts the resulting runs in a new configuration group on the leaderboard.


### 4.5 Run the evaluation

Standard call.

```bash
cd CQ2Onto
python -u scripts/run_all_evaluation_agent_datasets.py
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
python -u scripts/run_all_evaluation_agent_datasets.py --modes mymodel

# Only term-level layers (fastest, no Java needed)
python -u scripts/run_all_evaluation_agent_datasets.py --layers concept,property

# Re-run only axioms after a config change
python -u scripts/run_all_evaluation_agent_datasets.py --layers axioms --no_leaderboard
```

Downstream layers need the alignment CSVs from concept and property. The runner refuses with a clear error if the pre-alignment files are missing.

### 4.6 Evaluate a single domain

Drop only one prediction file. The other five datasets are skipped with `SKIP <dataset>: missing pred owl`. The leaderboard shows the run with Domain Coverage `1/6 ⚠`.

```bash
mkdir -p CQ2Onto/01_predictions/mymodel/my_run/ontology
cp wine_my_run.owl CQ2Onto/01_predictions/mymodel/my_run/ontology/
cd CQ2Onto
python -u scripts/run_all_evaluation_agent_datasets.py --modes mymodel
```

### 4.7 Inspect and fix alignments before running downstream layers

The Class and Property layers produce two CSVs (`class_best_matching.csv` and `property_best_matching.csv`) that downstream layers read. The automatic alignment can be wrong (LLM picked a near-synonym, two pred classes equally close, etc.), and the mistake then propagates into Triple, Axioms, and Hierarchy.

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

**Option B. Staged run with human verified edits.** Run the full pipeline in two phases. Edit the produced `best_matching.csv` between phases.

1. Run only the first two layers.
   ```bash
   python scripts/run_all_evaluation_agent_datasets.py --modes mymodel --layers concept,property
   ```
2. Open `03_evaluation_results/<mode>/<model>/<dataset>/01_class/class_best_matching.csv` and the property equivalent. Use the trace files next to them (`*_alignment_trace.csv` and `*_alignment_trace.json`) to see candidate pairs, all five method scores, and the selection reason.
3. Edit the `*_best_matching.csv` by hand. Replace a wrong `Pre_term`, or delete a row when no real match exists.
4. Run the rest. Downstream layers read your edited CSVs
   ```bash
   python scripts/run_all_evaluation_agent_datasets.py --modes mymodel --layers triple, atomic axioms, hierarchy
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

- **CQ2Term.** Under `CQ2Term/00_gold_standard/<domain>/`:
  - `cq_to_terms_<domain>.json`. The classes and properties each CQ requires (the gold used for scoring).
  - `term_to_cqs_<domain>.json`. The reverse mapping: for each term, the CQs that require it.
- **CQ2Onto.** Under `CQ2Onto/00_gold_standard/<domain>/`:
  - `ontology/sub_<domain>.owl`. The CQ-aligned sub-ontology (the gold ontology).
  - `axioms/<domain>_axiom_gold.json`. The gold TBox axioms used for scoring, each tagged with the CQ it comes from.
  - `axioms/<domain>_axiom_gold.xlsx`. A human-readable Excel view of the same gold axioms, with two sheets: one listing each axiom and the CQs it maps to, and one listing each CQ and the axioms it triggers. For reading only; scoring uses the JSON.
  - `axioms/sub_<domain>_atomic_tbox.{json,txt,xlsx}`. The full set of atomic TBox axioms extracted from the sub-ontology, in machine-readable (json), plain-text (txt), and spreadsheet (xlsx) form. Reference material; not read by the evaluation.

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

All files live in `leaderboard/` at the repo root. The two you interact with are:

- `build_leaderboard.py`. Generator script. Reads the result JSONs and `provenance.yaml`, writes `leaderboard_data.js`.
- `provenance.yaml`. Hand-maintained record of which runs have been reproduced and verified (see 7.5). The only file here you edit by hand.

The rest (`leaderboard.html`, `leaderboard_data.js`, `index.html`, `cqs.html`, `leaderboard.md`) are generated or static pages that are not normally touched.

### 7.2 Refresh

The runners call `build_leaderboard.py` at the end of a successful run, so the standard workflow needs no extra step. The scores come from the result JSONs under `03_evaluation_results/`. The Reproduced and Verified badges come from `provenance.yaml`. The script merges the two and writes `leaderboard_data.js`.

Manual refresh.

```bash
cd leaderboard
python build_leaderboard.py \
  --cq2term_root ../CQ2Term/03_evaluation_results \
  --cq2onto_root ../CQ2Onto/03_evaluation_results \
  --html_data    leaderboard_data.js \
  --markdown_out leaderboard.md \
  --provenance   provenance.yaml
```

`--provenance` defaults to `provenance.yaml` in the current directory, so it can be omitted when you run from inside `leaderboard/`. If the file is not found the leaderboard is still built, but with **no badges and nothing ranked**. Pass the path explicitly in any script that runs from another directory.

### 7.3 View

The leaderboard is published online via GitHub Pages (link in the README).

### 7.4 Configuration grouping

Two runs are ranked against each other only when they share the same settings, so that comparisons stay fair. The settings that matter are the alignment thresholds, `top_n`, `--threshold`, `--literal_relax`, `no_layer2`, `model_id`, and `methods`. Changing any of them puts a run in a new group. Paths and the reasoner (always HermiT) are ignored, and equivalent values (`1` vs `1.0`, `no` vs `false`, or a reordered `methods` list) count as the same.

One exception: a run marked **Verified** (see 7.5) had its alignment corrected by hand, so its class/property alignment threshold is no longer treated as a grouping setting. This lets verified runs be compared together even if a maintainer tuned that threshold differently for each.


### 7.5 Provenance badges (Reproduced / Verified)

The leaderboard shows two badges in the **Status** column. They record human review and are loaded entirely from the hand-maintained file `leaderboard/provenance.yaml`, independent of the evaluation scores.

- **Reproduced.** A maintainer invoked the model and obtained a prediction equivalent to what was submitted. Confirms the result is a real model output.
- **Verified.** A maintainer inspected the alignment (`class_best_matching.csv` / `property_best_matching.csv`), corrected it where the automatic matching was wrong, and re-ran the downstream layers. Confirms the metrics rest on a sound alignment.

**Ranking.** Only runs with both badges are ranked. All others remain visible below the divider without a rank. A run with no entry in `provenance.yaml` is treated as an unreviewed community submission (no badge, not ranked).

**The scores are never edited here.** `provenance.yaml` contains no metrics, only who reviewed what, and when. Scores always come from the result JSONs and are averaged by the script. This keeps evaluation results machine-generated while human review is recorded separately in one auditable file.

#### How to add a badge

After reproducing or verifying a run, add an entry to `leaderboard/provenance.yaml`. CQ2Onto is keyed by `mode` plus `model`, while CQ2Term is keyed by `model` alone.

```yaml
cq2onto:
  - mode: agent
    model: my_model            # must match the folder name under 01_predictions/<mode>/
    reproduced:
      by: "Name from Maintenance"
      date: "2026-06-08"
    verified:
      by: "Name from Maintenance"
      date: "2026-06-08"
      datasets: [wine, awo]    # only the domains you actually verified

cq2term:
  - model: my_model
    reproduced: { by: "Name from Maintenance", date: "2026-06-08" }
    verified:   { by: "Name from Maintenance", date: "2026-06-08", datasets: [wine, awo] }
```

How this works.

- **Writing a block turns a badge on.** A `reproduced:` block gives a model the R badge, and a `verified:` block gives it the V badge. `by`, `date`, and `notes` are optional hover metadata and do not affect the badge.
- **`datasets:` controls the Overall badge.** Inside `verified:`, list the domains you verified by hand. The Overall row gets a V badge only when all evaluated domains are listed. If only some are listed, those per-domain rows get V, but the Overall row does not.
- **`config:` is optional.** It ties a badge to a specific configuration group. If omitted (the normal case), the badge applies to the model regardless of settings. Use it only when the same model has multiple configurations that should be badged separately.

Save the file and refresh the leaderboard (7.2) to display the badges.
