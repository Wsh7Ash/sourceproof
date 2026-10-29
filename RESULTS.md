# Results

Reproducible evidence for every claim in [README.md](README.md). Commands run from
the repository root with `PYTHONPATH=src`.

## Environment

- Windows 11 (MSYS2 shell), Python 3.14.0
- Runtime: standard library only; `pytest>=8` as the only dev dependency
- Network: none required

## 1. Corpus gate

```console
$ sourceproof validate
sourceproof: 50/50 skills valid
  ok  steps>=6 signals>=4 patterns>=3 pitfalls>=3 words>=180 refs canonical https
```

Phase distribution: `ground` 8, `graph` 9, `sink` 9, `locate` 8, `grade` 8,
`ledger` 8 — 50 unique slugs, titles and summaries.

## 2. Indexing a real tree

```console
$ sourceproof scan examples --sinks
sql-exec         workspace/app/api.py:12    execute                  in store_file
unbounded-copy   workspace/src/parse.c:10    memcpy                   in copy_field
# 2 sink(s) in 5 file(s)
```

Five source files, eight definitions, two catalogue sinks. Each sink is attributed
to the function that contains it, not to the file.

`sourceproof scan examples` also prints every definition: `handle_request`
`server.c:26-34` calls `dispatch_route` and `read_message`; `parse_headers`
`parse.c:14-27` calls `copy_field`. The header `parse.h` contributes no
definitions, because a prototype ending in `;` is not a body.

## 3. Call path, verified hop by hop

```console
$ sourceproof path handle_request memcpy --root examples
   handle_request  workspace/src/server.c:26 (calls on line 33)
-> dispatch_route  workspace/src/server.c:18 (calls on line 21)
-> parse_headers  workspace/src/parse.c:14 (calls on line 26)
-> copy_field  workspace/src/parse.c:8 (calls on line 10)
# 4 hop(s), verified against the tree
```

```console
$ sourceproof path route_upload execute --root examples
   route_upload  workspace/app/api.py:4 (calls on line 6)
-> store_file  workspace/app/api.py:9 (calls on line 12)
# 2 hop(s), verified against the tree
```

The second path ends at `store_file`, which is where the SQL sink lives. Neither
path is asserted anywhere: each arrow is a call found in the caller's body, at the
line printed.

A path that does not exist exits 1 and says so:

```console
$ sourceproof path route_upload memcpy --root examples
no call path from route_upload to memcpy
exit=1
```

## 4. Grading a claim

```console
$ sourceproof check examples/claim.json --root examples
SP-001: grade A (100/100) verified
  anchor b691b72bf431c683
exit=0
```

Tampering produces blocking findings with the evidence needed to fix the claim:

```console
$ sourceproof check broken-hop.json --root examples --verbose
SP-001: grade D (25/100) NOT verified
  blocking broken-hop: 'handle_request' does not call 'parse_headers'
           -> Callees found in the tree: dispatch_route, read_message
  blocking broken-hop: 'parse_headers' does not call 'dispatch_route'
           -> Callees found in the tree: copy_field
  blocking broken-hop: 'dispatch_route' does not call 'copy_field'
           -> Callees found in the tree: parse_headers
exit=1
```

```console
$ sourceproof check moved.json --root examples --verbose
SP-001: grade D (50/100) NOT verified
  blocking snippet-mismatch: the line at workspace/src/parse.c:12 is not the line the claim quoted
           -> The quoted line is now at workspace/src/parse.c:10; run locate to re-anchor.
  blocking sink-absent: workspace/src/parse.c:12 does not call memcpy
           -> The sink moved, or the finding points at a comment or a wrapper.
exit=1
```

A claim whose sink is in the wrong function, with every edge intact, is caught
separately:

```console
$ sourceproof check wrong-owner.json --root examples
  blocking sink-owner: workspace/src/parse.c:10 is inside 'copy_field', not 'parse_headers'
exit=1
```

## 5. Re-anchoring

```console
$ sourceproof locate moved.json --root examples
workspace/src/parse.c:10
# 1 match(es) for the quoted line
exit=0
```

The claim's line number was edited to 12; the digest still finds the code at 10.
With an unknown digest the search exits 1, which is the signal to re-review rather
than to guess.

## 6. The ledger

```console
$ sourceproof verify examples/ledger.jsonl --root examples
ok   SP-001       A 100  Unbounded memcpy in copy_field reached from the upload request handler
ok   SP-002       A 100  SQL injection in store_file via the upload name parameter
# 2/2 claim(s) verified against examples
exit=0
```

Duplicates are caught at ledger level, and the repeated claim re-grades to D:

```console
$ python -m pytest tests/test_tree.py -k duplicate
test_verify_ledger_flags_a_duplicate_id PASSED
test_verify_ledger_flags_a_duplicate_claim_with_a_new_id PASSED
```

## 7. Test suite

```console
$ python -m pytest
93 passed in 7.59s

tests/test_corpus.py: 39
tests/test_tree.py: 54
```

`tests/test_tree.py` covers parsing (C definitions, prototypes, pointer returns,
static functions, braces inside strings, comment stripping, Python indentation),
sink catalogue matching, path search (edges, depth, determinism, unreachable
entries), every blocking grade rule, anchors, locate, ledger duplicates, claim
rendering and the claim builder.

`tests/test_corpus.py` covers the 50/50 gate, uniqueness, floors, phase coverage,
references, deterministic rendering, committed-artifact sync, and every CLI
subcommand with its exit code and JSON shape.

## 8. Determinism of generated files

```console
$ sourceproof build && git diff --exit-code -- skills pack.json results
(no output, exit 0)
```

## What was not run

- **No real codebase was reviewed.** `examples/workspace` is a five-file C and
  Python fixture written to exercise the parser and the path search, not a live
  project. Its claims are true of that fixture and nothing else.
- **The indexer was not compared against a real compiler front end** (clang,
  tree-sitter, jedi). Calls through function pointers, virtual dispatch, macros
  and generated code are out of reach by design and reported as such.
- **No network, no scanner, no target.** The tool only reads files under the root
  you pass it; nothing here contacted an endpoint or ran a payload.
- **Branch divergence was not exercised against a real multi-branch repository.**
  The rule is documented in the `locate` skills and the tool accepts any checkout
  you point it at, one at a time.
