# Security policy

## Reporting a vulnerability

Open a private security advisory on this repository, or email the maintainer in the
commit history. Do not open a public issue for a vulnerability in this tool.

Include the command, the input file and the traceback. If the input is a claim
about someone else's code, redact anything under NDA; a minimal reproduction of the
tool bug is enough.

Expect an acknowledgement within a week. Single-maintainer project, no bounty.

## What this tool does with your data

- It **reads** files under the root you pass. Nothing outside that root is opened,
  except the claim or ledger path you name explicitly.
- It **writes** only where told: `build` under the repository root, `report --out`,
  `scaffold --out`.
- It **has no network code**. No sockets, no HTTP client, no telemetry.
- It **does not execute** anything it reads. The C fixture in `examples/` is only
  ever parsed; the reproduction command from a claim is never run.

## Data handling

A source review touches confidential code. Two practical rules:

1. **Keep claims in the repository, not in chat.** A claim names a file, a line and
   a path; that triple is often enough to hand an outsider a map of the codebase.
2. **Redact before attaching evidence.** A captured `path` output is safe; a
   captured stack or log may contain tokens or user data. Redact first, then hash,
   because hashing first means either shipping the secret or breaking the digest.

The `evidence-bundle` and `redaction` guidance in the `grade` phase skills covers
the workflow.

## False confidence is the real risk

The parser is heuristic. A verified path means the tree contains that call chain,
not that the program can only behave that way. It cannot see function pointers,
virtual dispatch, macros, generated code or callbacks registered elsewhere, and it
counts calls in dead branches.

Treat a `verified` grade as "the reviewer can check this in four reads", never as
"this is definitely exploitable". The `dynamic-dispatch-limits` and
`unsupported-language-honesty` skills exist because of this failure mode.

## Authorisation

The tool reads code you already have. Reviewing it is still your responsibility:
check the program's scope, and quote the scope reference in the report that the
claim supports.
