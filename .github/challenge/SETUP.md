# CQ4OE submission evaluation Action — setup (fork-compatible)

Two workflows work together so evaluation runs and reports correctly on BOTH
fork PRs and same-repo PRs.

## evaluate-submission.yml  (trigger: pull_request on submissions/**)
1. Detects which submission changed.
2. Validates it against the submission guideline (metadata, files, formats).
3. Runs the evaluation over the submitted results.
4. Produces `submissions/<name>/result/` (+ `summary.md`), uploads it as the
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
  `result/` folder is available as the `cq4oe-results` artifact. To get the
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
    ├── make_result_data.py
    └── runners.patch
```

## Environment (handled by the workflow)
Ollama serving `embeddinggemma` (cached), Java 17 (HermiT), Python 3.10 +
requirements.txt. First run is slow due to the model pull.

## Output structure (what the Action writes)

Everything the Action produces for a submission lives in ONE folder,
`submissions/<name>/result/`. For each task declared in the submission's
`metadata.yml` it writes a `result/` (numeric) and a `report/` (markdown)
subfolder; the aggregate files sit at the top:

```
submissions/<name>/
└── result/
    ├── CQ2Onto/
    │   ├── result/             # numeric files, mirroring 03_evaluation_results
    │   │   └── <domain>/{01_class,02_property,03_triple,04_axiom,05_hierarchy}/*.json,*.csv
    │   └── report/             # markdown, one *_report.md per ontology (all layers)
    │       └── <domain>_report.md
    ├── CQ2Term/
    │   ├── result/
    │   │   └── <domain>/06_cq_terms/*.json,*.csv
    │   └── report/
    │       └── <domain>_report.md
    ├── result_data.js          # build_leaderboard.py output, scoped to THIS submission
    ├── leaderboard.md          # aggregate markdown leaderboard
    └── summary.md              # headline F1s + links (used for the PR comment)
```

`result_data.js` is produced by running `leaderboard/build_leaderboard.py` over a
temporary view of this submission's `03_evaluation_results` (the builder needs the
`<mode>/<model>/<dataset>` depth, which the flattened `result/` subfolder omits). It
has the same `LEADERBOARD_DATA` format as the global `leaderboard_data.js`; the
aggregate `leaderboard.md` is written alongside it.

Within each task, `report/` is the human-readable markdown and `result/` is the raw
numeric tree (identical layout to `CQ2Onto/03_evaluation_results/<mode>/<model>/`). A
task subfolder appears only if that task is declared in `metadata.yml`.
