---
name: moved-function-tracking
description: "Update file paths when a function moves between modules, because the code is unchanged but the claim's path no longer resolves. Use when the definition still exists but in a different file or package"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [locate, move, source]
---

# Moved Function Tracking

> Update file paths when a function moves between modules, because the code is unchanged but the claim's path no longer resolves

**Use when:** the definition still exists but in a different file or package

**Avoid when:** the function was deleted and reimplemented differently

## Procedure

1. Confirm the function name still resolves somewhere.
2. Confirm the body is materially the same as the reviewed one.
3. Update the sink file and the hop's file.
4. Re-check the callers, which may now import from a new path.
5. Record the move in the claim history.
6. Re-verify the path, since callers may not have been updated.

## Signals

- The name resolves in a new module with identical code.
- The old file now contains only a re-export.
- The move split the function into two.
- The callers import from the new location but one still uses the old one.

## Patterns

**1. Re-export**

```text
old path imports from new path  -> update the claim
```

**2. Function split**

```text
the copy moved into a helper  -> path gained a hop
```

**3. Stale caller**

```text
one caller still imports the shim  -> note it
```

## Pitfalls

- Treating a move as a fix when the code itself is unchanged.
- Updating the sink path but not the hop paths.
- Missing that a move split the function and changed the sink's owner.

## Done when

- Every path in the claim points at the moved code, and the move is recorded.
- The path re-verifies with the new module boundaries.

## References

- [Git - file history](https://git-scm.com/docs/git-log)
- [Python - module imports](https://docs.python.org/3/reference/import.html)
