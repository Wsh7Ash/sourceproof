---
name: sink-catalogue-scoping
description: "Decide which functions count as sinks for this codebase before scanning, because a generic catalogue floods a tree with calls that cannot be abused. Use when starting a source review or configuring the scanner for a new tree"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [sink, catalogue, scope]
---

# Sink Catalogue Scoping

> Decide which functions count as sinks for this codebase before scanning, because a generic catalogue floods a tree with calls that cannot be abused

**Use when:** starting a source review or configuring the scanner for a new tree

**Avoid when:** the review is a single hand-written claim with a known sink

## Procedure

1. List the sinks that matter for the trust boundaries in this code.
2. Add project-specific wrappers and framework calls to the list.
3. Remove catalogue entries the project never calls.
4. Record the catalogue version used for the review.
5. Re-run the scan after the catalogue changes and diff the hits.
6. Keep the catalogue in the repository, not in a local shell alias.

## Signals

- A wrapper around the real sink appears in results instead of the sink.
- The catalogue matches a logging helper named like a sink.
- New hits appear after a dependency upgrade adds a helper.
- The project has its own safe-copy wrapper that should not be a sink.

## Patterns

**1. Project wrappers**

```text
safe_copy in utils/  -> not a sink, it validates
```

**2. Framework**

```text
cur.execute for this ORM  -> sink, keep
```

**3. Versioned**

```text
catalogue v3, 69 functions  -> recorded with the review
```

## Pitfalls

- Using a generic list and reporting every printf as a format string bug.
- Leaving a project wrapper in the sink list when it performs bounds checks.
- Changing the catalogue mid-review and losing comparability of the hits.

## Done when

- The catalogue used is recorded and versioned with the review.
- Project wrappers are classified as sinks or guards explicitly.

## References

- [CWE - software development view](https://cwe.mitre.org/data/definitions/699.html)
- [OWASP - code review guide](https://owasp.org/www-project-code-review-guide/)
