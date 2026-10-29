---
name: rename-tracking
description: "Follow a renamed function through its history, because a claim whose hop was renamed looks broken until you find the new name. Use when a hop no longer resolves but the code around it looks unchanged"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [locate, rename, history]
---

# Rename Tracking

> Follow a renamed function through its history, because a claim whose hop was renamed looks broken until you find the new name

**Use when:** a hop no longer resolves but the code around it looks unchanged

**Avoid when:** the hop was deleted outright and nothing replaced it

## Procedure

1. Search the history for the old name.
2. Find the commit that removed it and read the replace.
3. Map the old name to the new one and update the hop.
4. Check whether the new function still calls the next hop.
5. Record the rename commit id in the claim's history.
6. Re-verify the full path after the rename.

## Signals

- The old name appears in the history but not in the tree.
- The new name has the same body and a different signature.
- A wrapper was introduced with the new name and calls the old one.
- The rename also changed the argument order.

## Patterns

**1. Straight rename**

```text
safe_copy -> copy_field  -> one hop rewrite
```

**2. Wrapper added**

```text
new safe_copy calls copy_field  -> path got longer
```

**3. Argument change**

```text
len moved from second to third argument  -> re-read the call
```

## Pitfalls

- Reporting a dead hop when the function was simply renamed.
- Assuming the signature is unchanged after a rename.
- Missing that the rename introduced a new guard.

## Done when

- The old-to-new mapping is recorded with the commit.
- The path verifies end to end under the new names.

## References

- [Git - rename detection](https://git-scm.com/docs/git-log)
- [CWE-710 - coding standards violation](https://cwe.mitre.org/data/definitions/710.html)
