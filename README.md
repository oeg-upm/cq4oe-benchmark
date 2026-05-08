# CQ4OE: A benchmark for assessing the LLM-assisted ontology generation from competency questions

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20080309.svg)](https://doi.org/10.5281/zenodo.20080309)

This repository contains a benchmark for assessing the performance of different LLM-based ontology generation methods from competency questions. The benchmark is built on six domain experts annotated ontologies that are exact mirroring the corresponding competency questions. 

The gold standards for both tasks and entire annotation process are also published as a dataset on HuggingFace: [oeg/CQ4OE](https://huggingface.co/datasets/oeg/CQ2Onto);

**Task 1: [CQ2Term](https://w3id.org/cq4oe/task/CQ2Term)** Given a competency question, the LLM-based method aims to extract the classes and properties required to answer it.
 
**Task 2: [CQ2Onto](https://w3id.org/cq4oe/task/CQ2Onto)** Given a set of competency questions in any domain, processing by LLM-based ontology generation method, producing a full OWL ontology.




**Annotated Ontologies**:
- [Wine](https://github.com/UCDavisLibrary/wine-ontology): Wine Ontology
- [VGO](https://vocab.linkeddata.es/vgo/): VideoGame Ontolgy
- [SWO](https://obofoundry.org/ontology/swo.html): Software Ontology
- [AWO](https://people.cs.uct.ac.za/~mkeet/OEbook/ontologies/AfricanWildlifeOntology1.owl): African wildlife Ontology
- [ODRL](https://www.w3.org/ns/odrl/2/): Open Digital Rights Language Ontology
- [Water](https://saref.etsi.org/saref4watr/v1.1.1/#clause-4-2-7): SAREF4WATR Ontolgy


## Annotation

The annotated ontologies in this benchmark are not just snapshots of existing ontologies. Every class, property and axiom is explicitly tied back to the competency questions. This section documents how that link was built so anyone adding a new domain can do the same thing.

### Annotation Guideline

For each source ontology, the annotation runs in three stages.

**1. Identify the core terms**: Before processing the competency question, domain experts extracts the conceptual backbone (key concepts and properties) from the source ontology by calculating the degree for each node as the relevance of the concept or property in the ontology. This can kept the backbone of the source ontology with maximum coverage.


**2. Annotated the CQs**: We annotated each CQ with two different terms. Exclude all CQs with external or out-of-the-scope concepts from the domain of the ontology. The two categories of the terms are:
- **Explicit:** terms that appear lexically in the CQ
- **Implicit:** terms expressed through synonymous phrasing
- **Missing Element**: terms are indicates in the CQ however do not mentioned in the ontology



**3. CQ Creation:** 
[Jiayi]
Due to the selection of the CQs after step 2, if there is any missing core concepts, domain experts create brand new CQs based on the missing core concepts.

**4. Axiom:**
[JiaYi]

**5. Annotating Ontology:**
[Jiayi]


Example of the annotation process
```
CQ: Which animals are the predators of [these animals]?
- Explicit Class: animal
- Explicit Property: eaten-by
- Implicit Class: Carnivore
- Implicit Property: None
- Missing Element: Predators is not in the ontology, however, carnivore indicates predators
```


### Dataset Description

We have selected six ontologies in three diferent scales:
| Ontology | Tier | Source CQs | Retained | New ⋆ | CQ2Onto set | CQ2Term set |
|----------|------|-----------:|---------:|------:|------------:|------------:|
| Wine     | small  | 7   | 4   | 1 | 5  | 5  |
| AWO      | small  | 14  | 7   | 0 | 7  | 7  |
| ODRL     | medium | 35  | 13  | 6 | 19 | 19 |
| Water    | medium | 43  | 21  | 0 | 21 | 20 |
| VGO      | large  | 68  | 30  | 1 | 31 | 22 |
| SWO      | large  | 88  | 35  | 0 | 35 | 26 |

## LLM Usage:

This repository evaluates LLM-based methods for two tasks: CQ2Onto (full-ontology generation) and CQ2Term (term-level generation), with the selection of baseline LLMs.

### Baseline LLMs Selection

- **Qwen-3.6 Series**: 
  - **Qwen-3.6-27B**: Open-source dense 27B parameter model
  - **Qwen-3.6-35B**: Open-source Mixture-of-Experts model, 35B total parameters with only 3B active per token
  - **Qwen-3.6-flash**: Closed-weights API-only low-latency model
  - **Qwen-3.6-plus**: Closed-weight API-only flagship model with 1M context window
- **Gemma-4 Series**:
  - **Gemma-4-26B**: Open-source Mixture-of-Experts model with 4B active per token
  - **Gemma-4-31B**: Open-source dense 31B parameter model 
- **Deepseek Series**:
  - **Deepseek-V3.2-671B**: The previous-generation flagship, Mixture-of-Experts  model from Deepseek.
  - **Deepseek-V4-flash-284B**: Efficient Mixture-of-Experts model with 13B activate parameter
  - **Deepseek-V4-1.6T**: Flagship Mixture-of-Experts model with 49B activate parameter, 1M context window.

### CQ2Onto
 
This repository evaluates three different LLM-assiat ontology generation methods.:
 
- **normal**: Give the model all the CQs and ask for the OWL ontology in one shot.
- [Cq-by-Cq Generation](https://github.com/LiUSemWeb/LLMs4OntologyDev-ESWC2024): generate a partial ontology per CQ and merge them. Slower but the model has to think about each question individually.
- [MASEO](https://github.com/oeg-upm/maseo): Multi-Agent System for Explainable Ontology Generation.


### CQ2Term
 
One LLM-based method for term-level prediction:
 
- **zero-shot term prediction**: Given a competency question, the model directly outputs the classes and properties required to answer it.

### Prompts

The prompts that drive every model for each method is under `CQ2Onto/prompts/` and `CQ2Term/prompts/`. They are kept in plain JSON, one file per generation method. Every prompt file is a JSON array of *agent* objects. Each object has three fields:

```json
[
  {
    "agent": "the name of the LLM-based agent",
    "instruction": "the system message of the given agent",
    "prompt": "the user message designed for the task corresponding to the agent"
  }
]
```

## Evaluation

The benchmark is organized as **tasks** → **dimensions** → **metrics**. A task is an evaluation track (CQ2Onto, CQ2Term); a dimension is one aspect evaluated within a task; a metric is a single measurement applied to a dimension. Definitions, formulas, and persistent identifiers for every dimension and metric are in the catalogue.
 
To submit a new model: place its outputs under the corresponding `predictions/` folder and run the script. The pipeline locates the gold standard, runs every dimension, and writes per-dataset and per-model results to `03_evaluation_results/` and `04_summary/`.

```bash
# CQ2Term
cd CQ2Term && python scripts/run_all_cq2term.py
 
# CQ2Onto, all three generation strategies
cd CQ2Onto && python scripts/run_all_evaluation_agent_4datsets.py
```

### CQ2Onto
 
Given a set of competency questions, the LLM produces a full OWL ontology. The output is evaluated against a CQ-aligned gold OWL ontology along the dimensions below. The first dimension yields a one-to-one term alignment that the others reuse to translate predicted vocabulary into gold vocabulary.
 
1. [`ClassProperty`](https://w3id.org/cq4oe/dimension/ClassProperty)
   1. Target: Do the generated classes and properties match the gold ones?
   2. Metrics: [`HardMatch`](https://w3id.org/cq4oe/metric/HardMatch), [`SequenceMatch`](https://w3id.org/cq4oe/metric/SequenceMatch), [`LevenshteinDistance`](https://w3id.org/cq4oe/metric/LevenshteinDistance), [`JaroWinklerDistance`](https://w3id.org/cq4oe/metric/JaroWinklerDistance), [`SemanticCosineSimilarity`](https://w3id.org/cq4oe/metric/SemanticCosineSimilarity), [`AggregatedTop3`](https://w3id.org/cq4oe/metric/AggregatedTop3); [`Precision`](https://w3id.org/cq4oe/metric/Precision), [`Recall`](https://w3id.org/cq4oe/metric/Recall), [`F1`](https://w3id.org/cq4oe/metric/F1).
2. [`PropertyCharacteristics`](https://w3id.org/cq4oe/dimension/PropertyCharacteristics)
   1. Target: Are the OWL property characteristics (functional, transitive, etc.) on each aligned property correct?
   2. Metrics: [`Precision`](https://w3id.org/cq4oe/metric/Precision), [`Recall`](https://w3id.org/cq4oe/metric/Recall), [`F1`](https://w3id.org/cq4oe/metric/F1).
3. [`Triple`](https://w3id.org/cq4oe/dimension/Triple)
   1. Target: Do the generated domain/range triples match the gold ones?
   2. Metrics: [`Precision`](https://w3id.org/cq4oe/metric/Precision), [`Recall`](https://w3id.org/cq4oe/metric/Recall), [`F1`](https://w3id.org/cq4oe/metric/F1); [`EmbeddingDiagnostic`](https://w3id.org/cq4oe/metric/EmbeddingDiagnostic).
4. [`Axiom`](https://w3id.org/cq4oe/dimension/Axiom)
   1. Target: Do the generated TBox axioms match the gold ones at the atomic level?
   2. Metrics: [`Precision`](https://w3id.org/cq4oe/metric/Precision), [`Recall`](https://w3id.org/cq4oe/metric/Recall), [`F1`](https://w3id.org/cq4oe/metric/F1); [`EmbeddingDiagnostic`](https://w3id.org/cq4oe/metric/EmbeddingDiagnostic); [`AtLeastOneCoverage`](https://w3id.org/cq4oe/metric/AtLeastOneCoverage), [`MeanCoverage`](https://w3id.org/cq4oe/metric/MeanCoverage), [`FullCoverage`](https://w3id.org/cq4oe/metric/FullCoverage).
5. [`HierarchyClosure`](https://w3id.org/cq4oe/dimension/HierarchyClosure)
   1. Target: Does the generated ontology entail the same class and property subsumptions as the gold one? Closure is computed with the HermiT reasoner.
   2. Metrics: [`Precision`](https://w3id.org/cq4oe/metric/Precision), [`Recall`](https://w3id.org/cq4oe/metric/Recall), [`F1`](https://w3id.org/cq4oe/metric/F1); [`ClosureRescueCoverage`](https://w3id.org/cq4oe/metric/ClosureRescueCoverage).
6. [`CQCoverage`](https://w3id.org/cq4oe/dimension/CQCoverage)
   1. Target: For each CQ, how many of its required TBox axioms appear in the generated ontology?
   2. Metrics: [`AtLeastOneCoverage`](https://w3id.org/cq4oe/metric/AtLeastOneCoverage), [`MeanCoverage`](https://w3id.org/cq4oe/metric/MeanCoverage), [`FullCoverage`](https://w3id.org/cq4oe/metric/FullCoverage); [`ClosureRescueCoverage`](https://w3id.org/cq4oe/metric/ClosureRescueCoverage) credits hierarchy axioms reachable through reasoner closure.

   
### CQ2Term
 
Given a single competency question, the LLM outputs the classes and properties needed to answer it. The output is evaluated against the explicit term set annotated for that CQ.
 
1. [`ClassProperty`](https://w3id.org/cq4oe/dimension/ClassProperty)
   1. Target: Do the generated classes and properties match the gold ones for the CQ?
   2. Metrics: [`HardMatch`](https://w3id.org/cq4oe/metric/HardMatch), [`SequenceMatch`](https://w3id.org/cq4oe/metric/SequenceMatch), [`LevenshteinDistance`](https://w3id.org/cq4oe/metric/LevenshteinDistance), [`JaroWinklerDistance`](https://w3id.org/cq4oe/metric/JaroWinklerDistance), [`SemanticCosineSimilarity`](https://w3id.org/cq4oe/metric/SemanticCosineSimilarity), [`AggregatedTop3`](https://w3id.org/cq4oe/metric/AggregatedTop3); global [`Precision`](https://w3id.org/cq4oe/metric/Precision), [`Recall`](https://w3id.org/cq4oe/metric/Recall), [`F1`](https://w3id.org/cq4oe/metric/F1).
2. [`CQCoverage`](https://w3id.org/cq4oe/dimension/CQCoverage)
   1. Target: Are the required terms generated under the CQ that requires them?
   2. Metrics: [`AtLeastOneCoverage`](https://w3id.org/cq4oe/metric/AtLeastOneCoverage), [`MeanCoverage`](https://w3id.org/cq4oe/metric/MeanCoverage), [`FullCoverage`](https://w3id.org/cq4oe/metric/FullCoverage).


## Ackownledgement

This work was supported by the grant [SOEL: Supporting Ontology Engineering with Large Language Models](https://w3id.org/soel) PID2023-152703NA-I00 funded by MCIN/AEI/10.13039/501100011033 and by ERDF/UE. The authors would also like to thank the EDINT (Espacios de Datos para las Infraestructuras Urbanas Inteligentes) ontology development team for sharing the project resources for evaluation purposes.