# CQ4OE Leaderboard

Top 10 ranking per task, macro-averaged across all six domains (Wine, AWO, ODRL, SAREF4WATR, VGO, SWO). Numbers are F1 percentages unless otherwise noted. For the full interactive leaderboard with per-domain tabs, sortable columns, expanded Precision and Recall, and per-method breakdowns, open `leaderboard.html`.

**Total runs.** CQ2Term 54, CQ2Onto 163.

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
| 1 | `deepseek-v4-flash` | 70.8% | 51.3% | 57.1% |
| 2 | `deepseek-v4-pro` | 70.6% | 62.8% | 56.4% |
| 3 | `qwen_qwen3.6-plus` | 68.0% | 52.8% | 56.2% |
| 4 | `qwen_qwen3.6-35b-a3b` | 64.4% | 56.6% | 54.6% |
| 5 | `qwen_qwen3.6-27b` | 66.2% | 50.3% | 54.4% |
| 6 | `google_gemma-4-31b-it` | 67.8% | 64.2% | 54.2% |
| 7 | `google_gemma-4-26b-a4b-it` | 69.2% | 51.5% | 54.0% |
| 8 | `deepseek_deepseek-v3.2` | 64.0% | 52.6% | 53.9% |
| 9 | `qwen_qwen3.6-flash` | 62.7% | 54.4% | 52.5% |

## CQ2Onto

### Term Recovery

_Recovery of the gold vocabulary across the full predicted ontology. Ranked by Property F1._

| Rank | Mode / Model | Class F1 | Property F1 |
|---|---:|---:|---:|
| 1 | `normal` / `deepseek-v4-pro` | 68.5% | 41.7% |
| 2 | `normal` / `qwen_qwen3.6-35b-a3b` | 66.0% | 39.6% |
| 3 | `normal` / `deepseek-v4-flash` | 66.8% | 39.5% |
| 4 | `normal` / `qwen_qwen3.6-flash` | 61.9% | 39.3% |
| 5 | `agent` / `qwen_qwen3.6-flash` | 61.7% | 38.2% |
| 6 | `normal` / `qwen_qwen3.6-27b` | 64.3% | 37.6% |
| 7 | `agent` / `qwen_qwen3.6-plus` | 62.6% | 36.9% |
| 8 | `agent` / `deepseek-v4-pro` | 51.1% | 35.1% |
| 9 | `normal` / `deepseek_deepseek-v3.2` | 62.1% | 34.8% |
| 10 | `mymodel` / `mymethod` | 69.0% | 34.8% |

### Property Characteristics

_Recovery of OWL property flags (functional, inverse, transitive, symmetric, reflexive). Ranked by F1-AC._

| Rank | Mode / Model | F1-AC | F1-G |
|---|---:|---:|---:|
| 1 | `cqbycq` / `qwen_qwen3.6-plus` | 100.0% | 28.6% |

### Triple (domain/range)

_Recovery of (subject, predicate, object) triples derived from the rdfs domain and rdfs range axioms of each property. Ranked by F1-AC._

| Rank | Mode / Model | F1-AC | F1-G | Cosine |
|---|---:|---:|---:|---:|
| 1 | `mymodel` / `mymethod` | 80.0% | 27.9% | 60.9% |
| 2 | `agent` / `deepseek-v4-flash` | 41.4% | 12.1% | 47.0% |
| 3 | `normal` / `qwen_qwen3.6-plus` | 38.7% | 12.0% | 46.1% |
| 4 | `agent` / `deepseek_deepseek-v3.2` | 38.6% | 12.9% | 48.5% |
| 5 | `normal` / `deepseek-v4-pro` | 38.6% | 19.0% | 50.3% |
| 6 | `agent` / `qwen_qwen3.6-27b` | 37.8% | 11.9% | 45.6% |
| 7 | `agent` / `google_gemma-4-31b-it` | 36.1% | 10.4% | 56.1% |
| 8 | `normal` / `deepseek-v4-flash` | 35.9% | 16.7% | 55.3% |
| 9 | `agent` / `qwen_qwen3.6-plus` | 34.1% | 11.0% | 53.1% |
| 10 | `normal` / `qwen_qwen3.6-35b-a3b` | 33.6% | 14.1% | 54.1% |

### TBox Axioms

_Recovery of TBox axioms by strict structural matching after alignment translation. Ranked by Axiom-Mean, the per-CQ strict axiom coverage rate._

| Rank | Mode / Model | F1-AC | F1-G | Axiom-Mean |
|---|---:|---:|---:|---:|
| 1 | `agent` / `qwen_qwen3.6-plus` | 35.3% | 16.0% | 30.7% |
| 2 | `agent` / `deepseek_deepseek-v3.2` | 40.6% | 17.6% | 29.5% |
| 3 | `agent` / `deepseek-v4-flash` | 33.6% | 14.9% | 27.9% |
| 4 | `mymodel` / `mymethod` | 56.0% | 28.4% | 25.4% |
| 5 | `agent` / `qwen_qwen3.6-flash` | 39.5% | 14.6% | 25.1% |
| 6 | `normal` / `deepseek-v4-flash` | 42.5% | 21.0% | 24.2% |
| 7 | `agent` / `deepseek-v4-pro` | 30.4% | 12.4% | 24.0% |
| 8 | `normal` / `qwen_qwen3.6-flash` | 39.6% | 18.6% | 22.2% |
| 9 | `agent` / `google_gemma-4-31b-it` | 37.6% | 16.6% | 21.9% |
| 10 | `cqbycq` / `qwen_qwen3.6-27b` | 37.2% | 14.8% | 21.5% |

### Hierarchy Closure

_Recovery of inferred subClassOf and subPropertyOf entailments using the HermiT reasoner. Ranked by Closure-Mean._

| Rank | Mode / Model | F1-G | Closure-Any | Closure-Mean |
|---|---:|---:|---:|---:|
| 1 | `agent` / `qwen_qwen3.6-plus` | 18.2% | 78.2% | 32.8% |
| 2 | `agent` / `deepseek_deepseek-v3.2` | 22.3% | 74.8% | 29.5% |
| 3 | `agent` / `deepseek-v4-flash` | 10.7% | 70.2% | 28.4% |
| 4 | `agent` / `qwen_qwen3.6-flash` | 12.4% | 66.5% | 27.6% |
| 5 | `mymodel` / `mymethod` | 14.3% | 100.0% | 26.0% |
| 6 | `normal` / `deepseek-v4-flash` | 21.8% | 66.9% | 24.6% |
| 7 | `agent` / `google_gemma-4-31b-it` | 23.5% | 63.6% | 24.5% |
| 8 | `agent` / `deepseek-v4-pro` | 11.5% | 57.9% | 24.0% |
| 9 | `agent` / `qwen_qwen3.6-35b-a3b` | 10.5% | 56.3% | 22.7% |
| 10 | `cqbycq` / `deepseek_deepseek-v3.2` | 18.6% | 64.9% | 22.4% |

---

**Configuration groups.** Runs that differ in any CLI argument appear in separate groups and are ranked independently. The tables above merge runs from all configuration groups for brevity. Open `leaderboard.html` to see per-config rankings.

- `axiom.literal_relax=no, axiom.no_layer2=True, axiom.threshold=0.6, concept.final_threshold=0.6, concept.hard_threshold=1.0, concept.lexical_threshold=0.8, concept.methods=hard_match,sequence_match,levenshtein,jaro_winkler,semantic, concept.model_id=embeddinggemma, concept.semantic_threshold=0.6, concept.top_n=3, property.final_threshold=0.7, property.hard_threshold=1.0, property.lexical_threshold=0.8, property.methods=hard_match,sequence_match,levenshtein,jaro_winkler,semantic, property.model_id=embeddinggemma, property.semantic_threshold=0.6, property.top_n=3, triple.literal_relax=no, triple.model_id=embeddinggemma, triple.threshold=0.6`
- `cq_terms.final_threshold=0.6, cq_terms.methods=[hard_match,jaro_winkler,levenshtein,semantic,sequence_match], cq_terms.semantic_model=embeddinggemma:latest, cq_terms.top_n=3`
