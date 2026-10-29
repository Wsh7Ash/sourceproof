---
name: call-edge-verification
description: "Check each consecutive pair in the path against the caller's body, because a path is only as strong as its weakest unverified hop. Use when the claim records a multi-hop call path from an entry to a sink"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [graph, path, verification]
---

# Call Edge Verification

> Check each consecutive pair in the path against the caller's body, because a path is only as strong as its weakest unverified hop

**Use when:** the claim records a multi-hop call path from an entry to a sink

**Avoid when:** the finding is a single function with no inter-function path

## Procedure

1. Take the path as an ordered list of function names.
2. For each pair, open the caller and search its body for a call to the callee.
3. Record the line of that call as the hop's evidence.
4. Confirm the callee is the definition you mean when names collide.
5. Mark the first broken hop, since later hops are unproven once one fails.
6. Do not shorten the path to make it verify.

## Signals

- The caller has a call to a same-named function in another module.
- The hop exists but only behind a condition that cannot be true.
- The call appears in a dead branch that the compiler removes.
- The pair verifies only when the name is matched loosely.

## Patterns

**1. Direct call**

```text
parse_headers calls copy_field on line 26  -> edge proven
```

**2. Conditional**

```text
call sits behind if (upload_enabled)  -> record the guard
```

**3. Dead branch**

```text
call after return  -> edge exists in text, never runs
```

## Pitfalls

- Accepting a hop because both functions exist, without checking the call.
- Matching by substring so a similarly named function verifies the hop.
- Skipping the broken hop and verifying the rest of the path.

## Done when

- Every pair has a recorded call site inside the caller's body.
- The first broken hop, if any, is reported with the caller's real callees.

## References

- [CWE-1125 - excessive attack surface](https://cwe.mitre.org/data/definitions/1125.html)
- [OWASP - attack surface analysis](https://owasp.org/www-community/Attack_Surface_Analysis_Cheat_Sheet)
