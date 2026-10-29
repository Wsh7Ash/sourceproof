# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses
[semantic versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-29

First release: 50 validated skills and the verification tool behind them.

### Added

- **Tree indexing.** Definitions for Python (indentation-bounded) and C-like
  languages (brace-bounded), call extraction per definition, and a sink catalogue
  of 9 kinds across 69 functions, each sink attributed to its enclosing function.
- **Call path search.** Breadth-first, shortest in hops, deterministic, with the
  call line recorded for every hop and a depth bound.
- **Claim grading** with blocking and advisory rules: file and line existence,
  snippet digest, sink presence and kind, sink owner, entry match, hop-by-hop edge
  verification, impact, evidence existence and drift.
- **Anchors.** A line-free, title-free identity derived from sink and path, used for
  dedupe and for matching a claim across revisions.
- **`locate`.** Re-finds a claim's quoted line anywhere in the tree by digest.
- **Ledger verification** with duplicate id and duplicate anchor detection, and
  re-grading after ledger-level findings.
- **CLI:** `validate`, `list`, `show`, `search`, `build`, `scan`, `path`, `locate`,
  `check`, `verify`, `report`, `scaffold`, `sinks`, `anchor`.
- **50 skills** across six phases: ground 8, graph 9, sink 9, locate 8, grade 8,
  ledger 8.
- CI matrix on Python 3.10, 3.12 and 3.13: corpus gate, tests, claim verification,
  and a rebuild that fails on committed-artifact drift.

### Fixed during development

- **A definition's own signature line counted as a self-call**, so every function
  appeared recursive and reachable from itself. The signature line is now skipped.
- **`path` could not reach a library sink.** The search required a definition for
  `memcpy`, so every claim about a library call failed. The goal is now a function
  whose body calls the sink.
- **Pointer-returning definitions were invisible** (`void *worker(void *arg)`), so
  any path through them was reported as an unknown hop.
- **Block comments were not stripped**, so a call or brace inside `/* ... */`
  affected call extraction and brace counting.
- **`build_claim` compared a relative evidence path to an absolute tree root** and
  crashed; both sides are resolved now, and evidence outside the tree is rejected
  with a message.
- **A duplicate claim kept its original grade** after the ledger appended a blocking
  finding, because score and grade were computed before ledger checks. `finalise`
  recomputes after every append.
- **The ledger summary printed an absolute local path**, which is unreadable and
  leaks a machine layout; it now prints the root relative to the working directory.
