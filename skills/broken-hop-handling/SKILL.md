---
name: broken-hop-handling
description: "When a hop fails, report the caller's real callees instead of deleting the hop, because the failed edge is often the most useful thing you learned. Use when a claimed call edge does not exist in the tree"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [graph, path, triage]
---

# Broken Hop Handling

> When a hop fails, report the caller's real callees instead of deleting the hop, because the failed edge is often the most useful thing you learned

**Use when:** a claimed call edge does not exist in the tree

**Avoid when:** the hop resolves only through a macro or function pointer, where absence proves nothing

## Procedure

1. Confirm the failure is real: the caller's body has no call to the callee.
2. List the callees the caller does have, from the tree.
3. Look for a rename, a wrapper or a moved function among them.
4. Check whether the sink is still reachable by another path.
5. Record the failed edge and the candidate replacement.
6. Decide: fix the claim, or downgrade it to a latent defect.

## Signals

- The caller calls a function one letter away from the claimed name.
- The caller calls a wrapper that calls the claimed function.
- The claimed callee moved to another module and was renamed.
- The sink is reachable from a different entry entirely.

## Patterns

**1. Real callees**

```text
dispatch_route calls parse_headers, strncmp  -> candidates
```

**2. Renamed function**

```text
safe_copy is now copy_field  -> one hop rewrite
```

**3. Still reachable**

```text
another entry reaches the sink  -> path rewrite, not a rejection
```

## Pitfalls

- Deleting the broken hop so the remaining path verifies.
- Rejecting the finding when only the entry point was wrong.
- Assuming the tree is stale instead of reading the caller's body.

## Done when

- The failed edge and the caller's actual callees are both recorded.
- The claim is either corrected with a verified path or downgraded explicitly.

## References

- [CWE-1059 - insufficient examination](https://cwe.mitre.org/data/definitions/1059.html)
- [Git - rename detection](https://git-scm.com/docs/git-log)
