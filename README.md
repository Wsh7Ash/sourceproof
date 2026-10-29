# sourceproof

Verify a source-level finding against the tree it came from — the file, the line,
the sink, and a call path whose every hop exists — plus **50 validated skills** for
reviewing source instead of trusting prose.

A finding written from memory reads the same as one that is true. The difference
is whether the tree supports it, and the tree can be asked:

- does the file exist, and does that line still contain the quoted code?
- is a catalogued sink actually called there, with the claimed kind?
- is the sink inside the function the path claims?
- does each consecutive pair in the path correspond to a real call?

This tool answers those four questions, and refuses to call a claim verified when
any of them fails. Zero runtime dependencies. Python 3.10+. Offline.

## The failure it exists to catch

Prose reachability. A report says "attacker-controlled input reaches `memcpy`
through `handle_request`", and the only artefact is the sentence. When the
reviewer opens the tree, one hop does not exist, or the sink sits in a different
function, or the quoted line moved three releases ago — and the report is dead.

`sourceproof` makes that check mechanical: the claim carries its own call path,
and the path is either in the tree or it is not.

```text
$ sourceproof path handle_request memcpy --root examples
   handle_request  workspace/src/server.c:26 (calls on line 33)
-> dispatch_route  workspace/src/server.c:18 (calls on line 21)
-> parse_headers  workspace/src/parse.c:14 (calls on line 26)
-> copy_field  workspace/src/parse.c:8 (calls on line 10)
# 4 hop(s), verified against the tree
```

Every arrow is a call the indexer found in the caller's body, at the line shown.

## Install and run

```bash
python -m pip install -e ".[dev]"
sourceproof validate          # the 50/50 gate
```

Or from a checkout: `PYTHONPATH=src python -m sourceproof ...`.

## The commands

### `scan` — index a tree

```text
$ sourceproof scan examples --sinks
sql-exec         workspace/app/api.py:12    execute                  in store_file
unbounded-copy   workspace/src/parse.c:10    memcpy                   in copy_field
# 2 sink(s) in 5 file(s)
```

Finds definitions (Python by indentation, C-like by brace matching), the calls
inside each, and catalogue sinks with their enclosing function. Also reports call
names that no definition matches, so a library call is visibly a library call.

### `path` — prove reachability

```text
$ sourceproof path route_upload execute --root examples
   route_upload  workspace/app/api.py:4 (calls on line 6)
-> store_file  workspace/app/api.py:9 (calls on line 12)
# 2 hop(s), verified against the tree
```

Breadth-first, so the path is the shortest in hops. The sink does not need a
definition of its own — `memcpy` and `cursor.execute` never have one.

### `check` — grade one claim

```text
$ sourceproof check examples/claim.json --root examples
SP-001: grade A (100/100) verified
  anchor b691b72bf431c683
```

A claim that breaks a hop fails with the caller's real callees named:

```text
$ sourceproof check broken-hop.json --root examples --verbose
SP-001: grade D (25/100) NOT verified
  blocking broken-hop: 'handle_request' does not call 'parse_headers'
           -> Callees found in the tree: dispatch_route, read_message
```

### `locate` — re-anchor a moved line

```text
$ sourceproof locate moved.json --root examples
workspace/src/parse.c:10
```

The digest of the quoted line is what identifies it, so a line that shifted is
found rather than lost. A claim whose line moved gets the new location as a hint:

```text
  blocking snippet-mismatch: the line at workspace/src/parse.c:12 is not the line the claim quoted
           -> The quoted line is now at workspace/src/parse.c:10; run locate to re-anchor.
```

### `verify` — the whole ledger

```text
$ sourceproof verify examples/ledger.jsonl --root examples
ok   SP-001       A 100  Unbounded memcpy in copy_field reached from the upload request handler
ok   SP-002       A 100  SQL injection in store_file via the upload name parameter
# 2/2 claim(s) verified against examples
```

Duplicate ids and duplicate anchors are flagged, and a duplicate claim re-grades
to D rather than keeping the score it earned before the ledger check.

## Blocking rules

A claim is not verified when any of these fail. They are chosen so that each one
makes the claim unfalsifiable, not merely weaker:

| Rule | Why it blocks |
|---|---|
| `sink-file-missing`, `sink-line-range` | there is no location to check |
| `snippet-mismatch` | the quoted bytes are not there, so the claim describes other code |
| `sink-absent` | the line does not call the named function |
| `sink-kind-mismatch` | `memcpy` declared as command execution is a different finding |
| `unknown-hop`, `broken-hop` | the path is the claim; an edge the tree lacks is an invented edge |
| `sink-owner` | the sink is not inside the function the path ends at |
| `entry-mismatch` | the path does not start where the claim says it does |
| `impact`, `evidence` | no stated effect, or nothing attached to verify |
| `evidence-drift`, `evidence-missing` | the artefact changed after it was hashed |
| `ledger-duplicate-id`, `ledger-duplicate-claim` | one finding filed twice inflates the ledger |

Severity penalties (`major`, `minor`) lower the score without blocking: an unknown
exposure, a missing `reported_at`, an unparsed file type.

## The 50 skills

| Phase | Skills | What it covers |
|---|---|---|
| `ground` | 8 | File/line anchoring, snippet hashing, symbol and boundary resolution, sink confirmation, entry points, build variants, parser limits |
| `graph` | 9 | Call-edge verification, broken hops, dynamic dispatch, callbacks, recursion, wrappers, path minimality, cross-file resolution, reachability vs exposure |
| `sink` | 9 | Catalogue scoping, copies, command exec, SQL, path traversal, deserialisation, format strings, dynamic code, what a sanitiser actually guarantees |
| `locate` | 8 | Drift, re-anchoring, duplicate snippets, renames, moves, deletions, line ranges, branch divergence |
| `grade` | 8 | Blocking vs advisory, impact, severity from evidence, false-positive review, guards, dedupe by anchor, evidence bundles, verification records |
| `ledger` | 8 | Format, identity, duplicate detection, cadence, branch pinning, retirement, disclosure mapping, handoff |

Every skill passes the same rules `sourceproof validate` enforces: 6+ steps, 4+
signals, 3+ patterns, 3+ pitfalls, 180+ rendered words, canonical https
references, no placeholders, no machine-local paths, unique slug and title.

```bash
sourceproof list --phase graph
sourceproof show broken-hop-handling
sourceproof search "guard"
```

## Honest limits

The indexer is a heuristic, not a compiler. It cannot see calls through function
pointers without an assignment it can find, virtual dispatch to more than one
implementation, macro expansions, callback registration outside the tree, or any
file whose language it does not parse. It counts calls in dead branches.

Those limits are reported rather than hidden: `scan` prints how many call names
resolve to nothing, and a claim whose sink lives in an unparsed file gets an
`unsupported-language` finding instead of a silent pass. A verified path means
*the tree supports this path*, not *this path is the only runtime behaviour*.

## Layout

```text
src/sourceproof/
  sources.py   definitions, call edges, sink catalogue, path search
  claims.py    claim schema, grading, anchors, ledger, rendering
  cli.py       the command surface
  corpus/      the 50 skills as plain dicts, in three parts
  validate.py  the corpus rules
  render.py    deterministic SKILL.md rendering
skills/        generated SKILL.md files
pack.json      generated manifest with a SHA-256 per skill
results/       generated catalog and demo transcript
examples/      a small real tree, two claims, a ledger, evidence
```

## Verification

- `sourceproof validate` → **50/50 skills valid**
- `pytest` → **93 passing**
- `check` on the example claim → grade A; a broken hop → grade D with the caller's
  real callees; a moved line → `locate` finds it
- Committed skills are compared against a fresh render, and CI rebuilds and fails
  on any diff

Exact commands and output: [RESULTS.md](RESULTS.md). Why a path is verified hop by
hop: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Scope

This tool reads source you already have and checks claims you already wrote. It
does not scan networks, fuzz binaries or exploit anything. Run it on code you are
authorised to review.

## License

MIT.
