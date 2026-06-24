# CQ4OE Leaderboard

Top 10 ranking per task, macro-averaged across all six domains (Wine, AWO, ODRL, SAREF4WATR, VGO, SWO). Numbers are F1 percentages unless otherwise noted. For the full interactive leaderboard with per-domain tabs, sortable columns, expanded Precision and Recall, and per-method breakdowns, open `leaderboard.html`.

**Total runs.** CQ2Term 6, CQ2Onto 6.

## Reading the tables

Each task in CQ4OE is scored with one or more of the metrics below. Tables show F1 by default. The full Precision (P), Recall (R), F1 triple is available in the interactive HTML viewer.

**Tasks.**

- **CQ2Term.** Term-level task. Does the model produce the explicit classes and properties each Competency Question (CQ) requires?
- **CQ2Onto.** Ontology-level task. Does the generated ontology capture the terms, property semantics, domain and range relations, TBox axioms (the schema-level class and property axioms), and hierarchy entailments needed to answer each CQ?

**Score columns.**

- **Class F1, Property F1.** F1 over the predicted vocabulary, aggregated by a top-3 mean over five string and embedding similarity methods (hard match, sequence match, Levenshtein, Jaro-Winkler, semantic embedding).
- **F1-AC (Alignment-Conditioned).** Restricted to items whose named terms align with gold names. Isolates structural errors from vocabulary errors.
- **F1-G (Global).** Evaluated over the full gold and predicted sets so unaligned items count as errors.
- **Cosine.** Embedding-based diagnostic that compares triples by vector similarity instead of strict structural equality.
- **CQ-Mean, Axiom-Mean, Closure-Mean.** Average per-CQ recovery rate. For each CQ, how many of its required items did the model recover, averaged across all CQs.
- **Closure-Any.** Share of CQs with at least one required item recovered after the reasoner closure rescue.

## CQ2Term

### Term Recovery

_Ranked by CQ-Mean over 99 CQs._

| Rank | Model | Class F1 | Property F1 | CQ-Mean |
|---|---:|---:|---:|---:|
| 1 | `pseudo_submission` | 70.6% | 62.8% | 56.4% |

## CQ2Onto

### Term Recovery

_Recovery of the gold vocabulary across the full predicted ontology. Ranked by Property F1._

| Rank | Mode / Model | Class F1 | Property F1 |
|---|---:|---:|---:|
| 1 | `challenge` / `pseudo_submission` | 59.8% | 28.1% |

### Property Characteristics

_Recovery of OWL property flags (functional, inverse, transitive, symmetric, reflexive). Ranked by F1-AC._

| Rank | Mode / Model | F1-AC | F1-G |
|---|---:|---:|---:|

### Triple (domain/range)

_Recovery of (subject, predicate, object) triples derived from the rdfs domain and rdfs range axioms of each property. Ranked by F1-AC._

| Rank | Mode / Model | F1-AC | F1-G | Cosine |
|---|---:|---:|---:|---:|
| 1 | `challenge` / `pseudo_submission` | 27.8% | 6.7% | 54.0% |

### TBox Axioms

_Recovery of TBox axioms by strict structural matching after alignment translation. Ranked by Axiom-Mean, the per-CQ strict axiom coverage rate._

| Rank | Mode / Model | F1-AC | F1-G | Axiom-Mean |
|---|---:|---:|---:|---:|
| 1 | `challenge` / `pseudo_submission` | 31.7% | 12.6% | 18.0% |

### Hierarchy Closure

_Recovery of inferred subClassOf and subPropertyOf entailments using the HermiT reasoner. Ranked by Closure-Mean._

| Rank | Mode / Model | F1-G | Closure-Any | Closure-Mean |
|---|---:|---:|---:|---:|
| 1 | `challenge` / `pseudo_submission` | 15.3% | 58.4% | 18.0% |

---

**Configuration groups.** Runs that differ in any CLI argument appear in separate groups and are ranked independently. The tables above merge runs from all configuration groups for brevity. Open `leaderboard.html` to see per-config rankings.

- `axiom.literal_relax=no, axiom.no_layer2=True, axiom.threshold=0.6, concept.final_threshold=0.6, concept.hard_threshold=1.0, concept.lexical_threshold=0.8, concept.methods=hard_match,sequence_match,levenshtein,jaro_winkler,semantic, concept.model_id=embeddinggemma, concept.semantic_threshold=0.6, concept.top_n=3, property.final_threshold=0.7, property.hard_threshold=1.0, property.lexical_threshold=0.8, property.methods=hard_match,sequence_match,levenshtein,jaro_winkler,semantic, property.model_id=embeddinggemma, property.semantic_threshold=0.6, property.top_n=3, triple.literal_relax=no, triple.model_id=embeddinggemma, triple.threshold=0.6`
- `cq_terms.cq_coverage_mode=cq_local, cq_terms.final_threshold=0.6, cq_terms.gold_cq_to_terms=00_gold_standard/awo/cq_to_terms_awo.json, cq_terms.hard_threshold=1.0, cq_terms.lexical_threshold=0.75, cq_terms.methods=hard_match,jaro_winkler,levenshtein,semantic,sequence_match, cq_terms.pred_cq_to_terms=01_predictions/pseudo_submission/terms/awo_cq2terms_terms.json, cq_terms.save_class_alignment_csv=03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_class_trace.csv, cq_terms.save_class_best_matching_csv=03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_class_best_matching.csv, cq_terms.save_cq_coverage_csv=03_evaluation_results/pseudo_submission/awo/06_cq_terms/cq_coverage.csv, cq_terms.save_property_alignment_csv=03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_prop_trace.csv, cq_terms.save_property_best_matching_csv=03_evaluation_results/pseudo_submission/awo/06_cq_terms/cqterm_prop_best_matching.csv, cq_terms.save_report_md=04_summary/pseudo_submission/awo_report.md, cq_terms.save_result_json=03_evaluation_results/pseudo_submission/awo/06_cq_terms/eval_cq_terms_result.json, cq_terms.save_term_coverage_csv=03_evaluation_results/pseudo_submission/awo/06_cq_terms/term_coverage.csv, cq_terms.semantic_model=embeddinggemma:latest, cq_terms.semantic_threshold=0.65, cq_terms.top_n=3`
- `cq_terms.cq_coverage_mode=cq_local, cq_terms.final_threshold=0.6, cq_terms.gold_cq_to_terms=00_gold_standard/odrl/cq_to_terms_odrl.json, cq_terms.hard_threshold=1.0, cq_terms.lexical_threshold=0.75, cq_terms.methods=hard_match,jaro_winkler,levenshtein,semantic,sequence_match, cq_terms.pred_cq_to_terms=01_predictions/pseudo_submission/terms/odrl_cq2terms_terms.json, cq_terms.save_class_alignment_csv=03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_class_trace.csv, cq_terms.save_class_best_matching_csv=03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_class_best_matching.csv, cq_terms.save_cq_coverage_csv=03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cq_coverage.csv, cq_terms.save_property_alignment_csv=03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_prop_trace.csv, cq_terms.save_property_best_matching_csv=03_evaluation_results/pseudo_submission/odrl/06_cq_terms/cqterm_prop_best_matching.csv, cq_terms.save_report_md=04_summary/pseudo_submission/odrl_report.md, cq_terms.save_result_json=03_evaluation_results/pseudo_submission/odrl/06_cq_terms/eval_cq_terms_result.json, cq_terms.save_term_coverage_csv=03_evaluation_results/pseudo_submission/odrl/06_cq_terms/term_coverage.csv, cq_terms.semantic_model=embeddinggemma:latest, cq_terms.semantic_threshold=0.65, cq_terms.top_n=3`
- `cq_terms.cq_coverage_mode=cq_local, cq_terms.final_threshold=0.6, cq_terms.gold_cq_to_terms=00_gold_standard/swo/cq_to_terms_swo.json, cq_terms.hard_threshold=1.0, cq_terms.lexical_threshold=0.75, cq_terms.methods=hard_match,jaro_winkler,levenshtein,semantic,sequence_match, cq_terms.pred_cq_to_terms=01_predictions/pseudo_submission/terms/swo_cq2terms_terms.json, cq_terms.save_class_alignment_csv=03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_class_trace.csv, cq_terms.save_class_best_matching_csv=03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_class_best_matching.csv, cq_terms.save_cq_coverage_csv=03_evaluation_results/pseudo_submission/swo/06_cq_terms/cq_coverage.csv, cq_terms.save_property_alignment_csv=03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_prop_trace.csv, cq_terms.save_property_best_matching_csv=03_evaluation_results/pseudo_submission/swo/06_cq_terms/cqterm_prop_best_matching.csv, cq_terms.save_report_md=04_summary/pseudo_submission/swo_report.md, cq_terms.save_result_json=03_evaluation_results/pseudo_submission/swo/06_cq_terms/eval_cq_terms_result.json, cq_terms.save_term_coverage_csv=03_evaluation_results/pseudo_submission/swo/06_cq_terms/term_coverage.csv, cq_terms.semantic_model=embeddinggemma:latest, cq_terms.semantic_threshold=0.65, cq_terms.top_n=3`
- `cq_terms.cq_coverage_mode=cq_local, cq_terms.final_threshold=0.6, cq_terms.gold_cq_to_terms=00_gold_standard/vgo/cq_to_terms_vgo.json, cq_terms.hard_threshold=1.0, cq_terms.lexical_threshold=0.75, cq_terms.methods=hard_match,jaro_winkler,levenshtein,semantic,sequence_match, cq_terms.pred_cq_to_terms=01_predictions/pseudo_submission/terms/vgo_cq2terms_terms.json, cq_terms.save_class_alignment_csv=03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_class_trace.csv, cq_terms.save_class_best_matching_csv=03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_class_best_matching.csv, cq_terms.save_cq_coverage_csv=03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cq_coverage.csv, cq_terms.save_property_alignment_csv=03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_prop_trace.csv, cq_terms.save_property_best_matching_csv=03_evaluation_results/pseudo_submission/vgo/06_cq_terms/cqterm_prop_best_matching.csv, cq_terms.save_report_md=04_summary/pseudo_submission/vgo_report.md, cq_terms.save_result_json=03_evaluation_results/pseudo_submission/vgo/06_cq_terms/eval_cq_terms_result.json, cq_terms.save_term_coverage_csv=03_evaluation_results/pseudo_submission/vgo/06_cq_terms/term_coverage.csv, cq_terms.semantic_model=embeddinggemma:latest, cq_terms.semantic_threshold=0.65, cq_terms.top_n=3`
- `cq_terms.cq_coverage_mode=cq_local, cq_terms.final_threshold=0.6, cq_terms.gold_cq_to_terms=00_gold_standard/water/cq_to_terms_water.json, cq_terms.hard_threshold=1.0, cq_terms.lexical_threshold=0.75, cq_terms.methods=hard_match,jaro_winkler,levenshtein,semantic,sequence_match, cq_terms.pred_cq_to_terms=01_predictions/pseudo_submission/terms/water_cq2terms_terms.json, cq_terms.save_class_alignment_csv=03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_class_trace.csv, cq_terms.save_class_best_matching_csv=03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_class_best_matching.csv, cq_terms.save_cq_coverage_csv=03_evaluation_results/pseudo_submission/water/06_cq_terms/cq_coverage.csv, cq_terms.save_property_alignment_csv=03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_prop_trace.csv, cq_terms.save_property_best_matching_csv=03_evaluation_results/pseudo_submission/water/06_cq_terms/cqterm_prop_best_matching.csv, cq_terms.save_report_md=04_summary/pseudo_submission/water_report.md, cq_terms.save_result_json=03_evaluation_results/pseudo_submission/water/06_cq_terms/eval_cq_terms_result.json, cq_terms.save_term_coverage_csv=03_evaluation_results/pseudo_submission/water/06_cq_terms/term_coverage.csv, cq_terms.semantic_model=embeddinggemma:latest, cq_terms.semantic_threshold=0.65, cq_terms.top_n=3`
- `cq_terms.cq_coverage_mode=cq_local, cq_terms.final_threshold=0.6, cq_terms.gold_cq_to_terms=00_gold_standard/wine/cq_to_terms_wine.json, cq_terms.hard_threshold=1.0, cq_terms.lexical_threshold=0.75, cq_terms.methods=hard_match,jaro_winkler,levenshtein,semantic,sequence_match, cq_terms.pred_cq_to_terms=01_predictions/pseudo_submission/terms/wine_cq2terms_terms.json, cq_terms.save_class_alignment_csv=03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_class_trace.csv, cq_terms.save_class_best_matching_csv=03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_class_best_matching.csv, cq_terms.save_cq_coverage_csv=03_evaluation_results/pseudo_submission/wine/06_cq_terms/cq_coverage.csv, cq_terms.save_property_alignment_csv=03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_prop_trace.csv, cq_terms.save_property_best_matching_csv=03_evaluation_results/pseudo_submission/wine/06_cq_terms/cqterm_prop_best_matching.csv, cq_terms.save_report_md=04_summary/pseudo_submission/wine_report.md, cq_terms.save_result_json=03_evaluation_results/pseudo_submission/wine/06_cq_terms/eval_cq_terms_result.json, cq_terms.save_term_coverage_csv=03_evaluation_results/pseudo_submission/wine/06_cq_terms/term_coverage.csv, cq_terms.semantic_model=embeddinggemma:latest, cq_terms.semantic_threshold=0.65, cq_terms.top_n=3`
