# CQ4OE Challenge submission — example-submission

A complete, valid example submission. The result files here are the
`cqbycq` / `deepseek-v4-pro` baseline from the benchmark, so this folder
doubles as a reference for the exact format and layout your own submission must
follow. The authoritative metadata is in `metadata.yml`.

## File formats

**CQ2Onto** — `CQ2Onto/<domain>/<domain>_ontology.owl`. A full OWL ontology for
that domain. Any rdflib-parseable serialization is accepted (`.owl`, `.rdf`,
`.xml`, `.ttl`, `.turtle`).

**CQ2Term** — `CQ2Term/<domain>/<domain>_cq2terms_terms.json`. A JSON list, one
object per competency question, in the benchmark's prediction format:

```json
{
  "id": "CQ1",
  "value": "Which animal eats which other animal?",
  "class": ["Animal"],
  "property": ["eats"]
}
```

Keep `id` and `value` as given by the competency-question file for the domain;
fill `class` and `property` with the terms your method predicts. Note the keys
are singular (`class`, `property`), matching what the evaluator consumes.

## Tasks and domains

This example covers both tasks across all six domains (`awo`, `odrl`, `swo`,
`vgo`, `water`, `wine`). Partial submissions are allowed — include only the
task/domain folders you ran, and declare them in `metadata.yml`.

## Method

CQbyCQ generates the ontology one competency question at a time and merges the
per-CQ fragments into a single ontology per domain; the same base model predicts
the required terms for the CQ2Term task. Replace this section with your own
method description.

## Reproducing

`code/` holds the source a verifier would use to regenerate everything under
`CQ2Onto/` and `CQ2Term/`. The exact environment setup and run command are in
the `code:` block of `metadata.yml`. The challenge CI does not execute `code/`;
it scores the committed result files and keeps `code/` for verification.
