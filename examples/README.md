# Examples

A five-file workspace with two real bugs, two claims that verify against it, and a
ledger that keeps them honest. Everything is synthetic: the code is written to be
read and parsed, not to run in production.

## The workspace

```text
workspace/
  src/server.c    handle_request -> read_message, dispatch_route
  src/parse.c     dispatch_route -> parse_headers -> copy_field -> memcpy
  src/parse.h     prototypes only, so it contributes no definitions
  app/api.py      route_upload -> store_file -> cursor.execute
  app/routes.py   register(app) wires the route table
```

Two catalogue sinks:

- `memcpy` in `copy_field`, at `src/parse.c:10`, reached from the upload handler in
  four hops across two files
- `cursor.execute` in `store_file`, at `app/api.py:12`, reached in two hops

## Verify the paths

```console
$ sourceproof path handle_request memcpy --root examples
   handle_request  workspace/src/server.c:26 (calls on line 33)
-> dispatch_route  workspace/src/server.c:18 (calls on line 21)
-> parse_headers  workspace/src/parse.c:14 (calls on line 26)
-> copy_field  workspace/src/parse.c:8 (calls on line 10)
# 4 hop(s), verified against the tree
```

Each arrow is a call the indexer found inside the caller's body, at the printed
line. Nothing here is asserted: if the call were absent, the hop would fail.

## The claims

| File | Sink | Path | Grade |
|---|---|---|---|
| `claim.json` | `memcpy` (unbounded-copy) | `handle_request → dispatch_route → parse_headers → copy_field` | A |
| `claim-python.json` | `execute` (sql-exec) | `route_upload → store_file` | A |

```console
$ sourceproof check examples/claim.json --root examples
SP-001: grade A (100/100) verified
  anchor b691b72bf431c683
```

The `snippet_sha256` in each claim was taken from the file with
`sourceproof anchor`, not typed by hand — a hand-typed digest is precisely the
failure this tool is for.

## Evidence

`evidence/` holds four files: the two path captures and the two quoted sink lines.
Each is referenced from its claim with a SHA-256. Editing any of them makes `check`
report `evidence-drift` and block.

## The ledger

`ledger.jsonl` contains both claims, one per line.

```console
$ sourceproof verify examples/ledger.jsonl --root examples
ok   SP-001       A 100  Unbounded memcpy in copy_field reached from the upload request handler
ok   SP-002       A 100  SQL injection in store_file via the upload name parameter
# 2/2 claim(s) verified against examples
```

## Try to break it

```bash
# a hop that does not exist: the caller's real callees are reported
python - <<'PY'
import json, pathlib
c = json.loads(pathlib.Path("examples/claim.json").read_text())
c["path"] = ["handle_request", "parse_headers", "copy_field"]
pathlib.Path("broken.json").write_text(json.dumps(c, indent=2))
PY
sourceproof check broken.json --root examples

# a line that moved: the digest finds it
sourceproof locate examples/claim.json --root examples

# a sink in the wrong function, with every edge intact
python - <<'PY'
import json, pathlib
c = json.loads(pathlib.Path("examples/claim.json").read_text())
c["path"] = ["handle_request", "dispatch_route", "parse_headers"]
pathlib.Path("wrong-owner.json").write_text(json.dumps(c, indent=2))
PY
sourceproof check wrong-owner.json --root examples
```

Each one blocks with a finding that names the thing to fix, which is the point:
a rejected claim should teach you where your reading of the code was wrong.
