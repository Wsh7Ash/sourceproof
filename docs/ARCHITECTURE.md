# Architecture

Three modules, one direction of dependency:

```text
sources.py  files -> definitions -> calls -> sink sites -> path search
claims.py   claim schema -> grading -> anchors -> ledger        (uses sources)
cli.py      argument parsing, output, exit codes                 (uses both)
```

`corpus/` holds the 50 skills as plain dicts, `model.py` freezes them, `validate.py`
enforces the rules, and `render.py` is the only writer of generated files.

## Why the path is the unit of proof

A finding's weakest sentence is almost always "reachable from X". Everything else
can be checked cheaply: the file exists, the line exists, the call is there. That
sentence cannot be checked at all unless it is decomposed into edges.

So a claim stores an ordered list of function names, and the tool checks each
consecutive pair against the caller's body. Three properties matter:

1. **The check is local.** Each edge is a search of one function body for
   `callee(`, which is cheap and does not depend on a whole-program analysis.
2. **The failure is informative.** A missing edge is reported with the callees the
   caller actually has, which is usually enough to find the rename or the wrapper.
3. **A broken edge is fatal.** Later hops are unproven once one fails, so the
   claim blocks rather than scoring 80/100 and looking acceptable.

The path ends at the function that *contains* the sink, not at the sink itself:
`memcpy` and `cursor.execute` are not defined in the tree, and requiring a
definition for them would make every claim about a library call unverifiable.

## Why the entry point must also be a hop

An earlier design allowed `entry` to be a free-text field. That let a claim say
"unauthenticated" while the path began somewhere else entirely. Requiring
`path[0] == entry.function` makes the exposure claim and the reachability claim
refer to the same starting point; whether that entry is authenticated is then a
separate question, answered by reading the code, and recorded as `exposure` rather
than asserted.

## The parser, and why it is heuristic

Two front ends, both regex-based:

| Language | Definition rule | Body rule |
|---|---|---|
| Python | `def` / `async def` at line start | indentation greater than the `def` |
| C-like (C, C++, Java, Go, Rust, JS/TS, PHP, Ruby) | signature line ending in `{` or followed by one | brace counting |

Before either runs, every line is passed through `strip_noise`, which removes block
comments, `//` and `#` comments, and string literals. Without that, `printf("}")`
closes the function early and every definition after it is wrong.

The signature line is deliberately excluded from a definition's own call list: it
contains `name(`, and counting it made every function look recursive and let it
appear reachable from itself.

Pointer return types needed a dedicated rule (`void *worker(void *arg)`): a naive
"type then name" pattern cannot cross the `*`, so those definitions were missing
from the index entirely and any path through them was reported as unknown.

### What it cannot see

- calls through function pointers with no visible assignment
- virtual dispatch to more than one implementation
- macro-generated calls
- callbacks registered outside the tree
- calls in dead branches (counted as edges)
- any file whose suffix is not in the table

The first four make the index *miss* edges, which is safe: a claim fails rather
than passes. The fifth makes it *add* an edge that may never run, which can pass a
claim that would not execute; the `guard-verification` and `call-edge-verification`
skills tell the reviewer to check the condition. The sixth is reported per claim as
`unsupported-language`.

## Anchors

`anchor_of` hashes `file|function|kind|path`. It deliberately excludes the line
number and the title:

- a line number changes on every reformat, and an identity that changes on a
  reformat is not an identity;
- a title is prose, and two people describe one bug differently, which is how a
  ledger ends up with the same finding filed twice under two names.

The line number is still carried, because it is how a human finds the code. The
snippet digest is what makes the line portable: `locate` searches for a line whose
normalised text hashes to the recorded value, so a claim that moved by ten lines is
found rather than lost, and a claim whose quoted text changed is treated as a claim
about different code.

## Grading is blocking by construction

`grade` returns a score *and* findings tagged `blocking`, `major` or `minor`. Any
blocking finding forces grade D regardless of the score, because a 97/100 claim
that lacks a line number is not 97% verified; it is unverified with two minor
problems.

`finalise` recomputes score and grade from the findings list. It is called twice:
once at the end of `grade`, and again after `verify_ledger` appends duplicate
findings. Without the second call a duplicated claim kept its original grade A,
which is exactly the kind of display bug that makes a gate untrustworthy.

## Bundles and drift

Evidence is referenced by path with a SHA-256. Two rules keep that honest:

- a reference that does not resolve blocks, because a claim cannot be checked
  against a file that is not there;
- a digest mismatch blocks, because the artefact is not the one that was reviewed.

The digest is computed over the bytes, so a text-mode transfer that rewrites line
endings shows up as drift — correctly, since the claim is about the bytes.

## Determinism

`build_pack` is the only writer of `skills/`, `pack.json` and `results/`. Rendering
is a pure function of the skill dict, the test suite compares every committed file
against a fresh render, and CI rebuilds and fails on any diff. A corpus edit without
a rebuild cannot ship.
