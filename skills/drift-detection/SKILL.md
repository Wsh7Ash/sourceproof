---
name: drift-detection
description: "Re-verify a stored claim against the current tree before quoting it, because a claim verified last quarter may now point at a fixed line. Use when reusing a finding, retesting, or reporting against a newer revision"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [locate, drift, verification]
---

# Drift Detection

> Re-verify a stored claim against the current tree before quoting it, because a claim verified last quarter may now point at a fixed line

**Use when:** reusing a finding, retesting, or reporting against a newer revision

**Avoid when:** the claim was verified against this exact revision minutes ago

## Procedure

1. Check that the recorded revision differs from the current one.
2. Re-run the snippet hash against the recorded line.
3. Re-run the call path check.
4. Re-run the sink confirmation on the current line.
5. Record which of the three changed.
6. Update the claim's revision only after all three pass.

## Signals

- The line still exists but contains different code.
- The path still verifies but through a different function.
- The sink is gone and the file shrank.
- The digest is found on a different line in the same file.

## Patterns

**1. Snippet moved**

```text
same digest, new line  -> re-anchor, still valid
```

**2. Snippet fixed**

```text
digest absent  -> the code changed, re-review
```

**3. Path changed**

```text
same sink, new hops  -> rewrite the path
```

## Pitfalls

- Trusting a stored claim because the file still compiles.
- Updating the revision without re-running the checks.
- Reporting a fixed finding because the function name survived.

## Done when

- Snippet, sink and path are each re-checked and the results recorded.
- The claim's revision reflects the tree it was actually verified against.

## References

- [NIST - SP 800-115 testing guide](https://csrc.nist.gov/pubs/sp/800/115/final)
- [Git - diffing revisions](https://git-scm.com/docs/git-diff)
