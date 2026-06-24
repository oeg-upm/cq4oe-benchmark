# CQ4OE submission evaluation Action — setup (fork-compatible)

Two workflows work together so evaluation runs and reports correctly on BOTH
fork PRs and same-repo PRs.

## evaluate-submission.yml  (trigger: pull_request on submissions/**)
1. Detects which submission changed.
2. Validates it against the submission guideline (metadata, files, formats).
3. Runs the evaluation over the submitted results.
4. Produces `submissions/<name>/result/` (+ `SUMMARY.md`), uploads it as the
   `cq4oe-results` artifact (with the PR number), and — for same-repo PRs only —
   commits it back onto the PR branch.

A fork PR's token is read-only, so on a fork it does NOT commit back and CANNOT
comment. It just uploads the artifact.

## post-results.yml  (trigger: workflow_run, after the above completes)
Runs with write access but never checks out PR code. It downloads the
`cq4oe-results` artifact and posts the SUMMARY as a PR comment (updating its own
previous comment on re-runs). This is what gives fork PRs visible results on the
PR itself.

## Why two workflows
GitHub gives fork-PR runs a read-only token (security: untrusted code must not be
able to write to your repo or read secrets). So the fork-triggered run can only
*produce* results; a separate `workflow_run` run, which executes from your default
branch with write access, *publishes* them. This is the standard secure pattern.

## What you get, by PR type
- **Same-repo PR** (branch in OEG-Clark/cq4oe-benchmark): evaluation folder is
  committed into the PR AND a summary comment is posted.
- **Fork PR** (e.g. ClarkWang0519:main): a summary comment is posted and the full
  `evaluation/` folder is available as the `cq4oe-results` artifact. To get the
  folder committed for a fork submission, add it at merge time (a push-to-main
  workflow running the same steps and committing into main).

## One-time repo setup
1. Apply the runner patch: `git apply .github/challenge/runners.patch`
2. Commit `.github/` and the patched runners to the default branch (`main`).
3. Settings -> Actions -> General:
   - Workflow permissions: **Read and write** (needed for same-repo commit-back).
   - Fork pull request workflows: allow runs (first-time fork PRs need a one-time
     "Approve and run" click on the PR).

## Files
```
.github/
├── workflows/
│   ├── evaluate-submission.yml   # produce results
│   └── post-results.yml          # publish results to the PR
└── challenge/
    ├── validate_submission.py
    ├── stage_submission.py
    ├── collect_into_submission.py
    └── runners.patch
```

## Environment (handled by the workflow)
Ollama serving `embeddinggemma` (cached), Java 17 (HermiT), Python 3.10 +
requirements.txt. First run is slow due to the model pull.

## Output structure (what the Action writes)

For each task listed in the submission's `metadata.yml`, the Action creates a
task subfolder under `result/` and saves one markdown report per ontology:

```
submissions/<name>/result/
├── CQ2Onto/                 # only if cq2onto is in metadata tasks
│   ├── awo_report.md
│   ├── odrl_report.md
│   └── ...                  # one *_report.md per evaluated ontology
├── CQ2Term/                 # only if cq2term is in metadata tasks
│   ├── awo_report.md
│   └── ...
└── SUMMARY.md               # headline F1s, links to each report (used for the PR comment)
```

Each CQ2Onto `*_report.md` is the consolidated report covering all layers
(class, property, triple, axiom, hierarchy) for that ontology.
