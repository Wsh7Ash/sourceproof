# Usage

The workflow this tool supports, in the order a source review actually happens.

## 1. Pin the tree

```bash
git rev-parse HEAD
git status --short        # if this prints anything, the tree is dirty
sourceproof scan . --sinks
```

Record the commit with the review. A verified claim with no revision is a claim
about whatever was on disk that afternoon.

## 2. Find something worth claiming

```bash
sourceproof scan /path/to/tree --sinks --kind unbounded-copy
```

This prints catalogue sinks with their enclosing function. From a sink, work
backwards by searching for callers, or forwards from an entry point:

```bash
sourceproof path handle_request memcpy --root /path/to/tree
```

If the path does not exist, that is the finding before the finding: either the sink
is unreachable from that entry, or the path you had in mind was wrong.

## 3. Write the claim

```bash
sourceproof scaffold "Unbounded memcpy in copy_field" --id SP-001 --out claim.json
```

Fill in:

- `sink.file`, `sink.line` — the line with the call
- `sink.snippet_sha256` — from `sourceproof anchor <file> <line>`
- `path` — entry first, the sink's enclosing function last
- `entry.function` — must equal `path[0]`
- `entry.exposure` — `pre-auth`, `authenticated`, `local` or `unknown`
- `impact`, `severity`
- `evidence` — files with digests

Never hand-type the digest. `sourceproof anchor` prints it from the file:

```console
$ sourceproof anchor examples/workspace/src/parse.c 10
line     memcpy(dst, src, (size_t)len);
digest   b6a1...
```

## 4. Grade it

```bash
sourceproof check claim.json --root /path/to/tree --verbose
```

Blocking findings mean: not verified. Fix the claim, not the rule. The common ones
and what they mean:

| Finding | Usually means |
|---|---|
| `broken-hop` | a rename, or a wrapper between the two functions |
| `unknown-hop` | the function is a macro, a library call, or in an unparsed file |
| `sink-owner` | the path ends one function too early |
| `snippet-mismatch` | the line moved (a hint gives the new one) or the code changed |
| `sink-kind-mismatch` | the declared sink class does not match the catalogue |

## 5. Attach evidence

```bash
sourceproof path handle_request memcpy --root . > evidence/path.txt
sourceproof anchor src/parse.c 10 > evidence/snippet.txt
```

Then add each file to `evidence` with its SHA-256, and re-run `check`. An evidence
reference that does not resolve, or whose digest changed, blocks.

## 6. Keep the ledger

```bash
sourceproof verify ledger.jsonl --root /path/to/tree
```

One claim per line, or `{"claims": [...]}`. Duplicate ids and duplicate anchors are
detected; a repeat claim re-grades to D. The exit code is 0 only when every claim
verifies.

## 7. Re-verify after the code moves

```bash
git pull
sourceproof verify ledger.jsonl --root .
```

For a claim that fails only on `snippet-mismatch`:

```bash
sourceproof locate claim.json --root .
```

- one hit → the line moved; update `sink.line` and re-check
- several hits → narrow by file and enclosing function before choosing
- no hits → the code changed; re-review rather than re-pointing the claim

## Exit codes

| Code | Meaning |
|---|---|
| `0` | verified, or a path was found |
| `1` | a gate failed: not verified, no path, line not found |
| `2` | usage error: missing file, unknown slug, bad JSON, sink not in the catalogue |

## Working in an agent loop

Each skill is `skills/<slug>/SKILL.md` with front matter naming the pack and phase.
`sourceproof search "<term>"` and `sourceproof show <slug>` fetch one procedure, so
an agent can load the rule it needs instead of the whole pack. The claim schema is
plain JSON, so a loop can write a claim, run `check`, read `--json` findings, and
iterate without parsing prose.
