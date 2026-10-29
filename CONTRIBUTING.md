# Contributing

## Setup

```bash
python -m pip install -e ".[dev]"
pytest
sourceproof validate
```

No runtime dependency, and that should not change: this tool has to run on a
review host that may have nothing installed.

## The gates

```bash
sourceproof validate                # 50/50 skills valid
pytest                              # 93 passing
sourceproof build
git diff --exit-code -- skills pack.json results
```

`build` is the only writer of generated files. Never edit a `SKILL.md` by hand.

## Changing the parser

`scan`, `path` and every hop check depend on `sources.py`. A parser change needs a
test that fails before it and passes after, and the test should use a real code
shape, not a synthetic one-liner. If the change narrows or widens what counts as an
edge, say so in the pull request — it changes which claims verify.

Two invariants to keep:

- a definition must never list its own name as a call;
- a brace or a parenthesis inside a comment or a string must not affect parsing.

## Changing a grading rule

A rule is blocking only when the claim is unfalsifiable without it. If a rule
becomes more permissive, the pull request must say why; "it rejected a finding I
liked" is not a reason.

If you add a blocking rule, add a test that a claim failing it is not submittable,
and one that the same claim with the field filled in is.

## Adding a skill

Skills live in `src/sourceproof/corpus/part{1,2,3}.py` as dicts. Enforced rules:
6+ steps, 4+ signals, 3+ patterns, 3+ pitfalls, 2+ done-when items, 180+ rendered
words, 2+ kebab-case tags, at least one `[label](https://...)` reference, no
placeholders, no machine-local paths, unique slug and title.

Beyond the mechanics: a skill earns its place only if it changes a decision. State
when *not* to use it, because a skill that always applies teaches nothing.

## Style

- Python 3.10+, standard library only
- `from __future__ import annotations` in every module
- Type hints on public functions
- CLI output ASCII only, and paths relative to the working directory where possible
- No printing from library modules; `cli.py` owns stdout and exit codes

## Reporting a problem

Open an issue with the command, the tree shape (not the tree itself), the output you
got and the output you expected. If a path did not verify, say whether the hop is a
macro, a function pointer or a rename — those are the three usual causes.
