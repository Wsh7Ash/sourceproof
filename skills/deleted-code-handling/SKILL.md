---
name: deleted-code-handling
description: "Close a claim whose code is gone, but check the fix first, because deletion is sometimes a revert waiting to happen. Use when the sink or a hop no longer exists in the tree"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [locate, retirement, fix]
---

# Deleted Code Handling

> Close a claim whose code is gone, but check the fix first, because deletion is sometimes a revert waiting to happen

**Use when:** the sink or a hop no longer exists in the tree

**Avoid when:** the code is behind a build flag rather than deleted

## Procedure

1. Confirm the code is absent from the current revision.
2. Find the commit that removed it and read the message.
3. Check whether a guard was added instead of the code being removed.
4. Check whether the deletion was a revert of a previous fix.
5. Mark the claim retired with the commit id and the reason.
6. Re-open if the code returns.

## Signals

- The file exists but the function is gone.
- The removal commit message says revert.
- A guard was added in the same commit as the deletion.
- The code moved to a branch that is still deployed.

## Patterns

**1. Fixed by removal**

```text
bounds check added, sink removed  -> retire as fixed
```

**2. Reverted**

```text
the fix was reverted  -> re-open the claim
```

**3. Moved to branch**

```text
still deployed from release/2.3  -> keep open
```

## Pitfalls

- Retiring a claim whose code was reverted.
- Missing a still-deployed branch that has the old code.
- Deleting the claim's evidence when it is closed.

## Done when

- The removal commit and its reason are recorded on the claim.
- The claim is retired, kept open, or marked a revert, explicitly.

## References

- [Git - revert](https://git-scm.com/docs/git-revert)
- [OWASP - vulnerability management](https://owasp.org/www-community/vulnerability_management)
