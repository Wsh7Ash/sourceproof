---
name: disclosure-mapping
description: "Map each ledger claim to the report it was filed as, because a verified claim with no filing record is work nobody can be credited for. Use when claims are being submitted to a program"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [ledger, disclosure, process]
---

# Disclosure Mapping

> Map each ledger claim to the report it was filed as, because a verified claim with no filing record is work nobody can be credited for

**Use when:** claims are being submitted to a program

**Avoid when:** the engagement is internal and nothing is filed externally

## Procedure

1. Record the report id or advisory id against each claim.
2. Record the date and the program for each.
3. Record rejections and their reasons.
4. Keep the mapping in the ledger, not in an inbox.
5. Re-check the mapping before a retest.
6. Note claims that were never filed and why.

## Signals

- A verified claim has no report id months later.
- Two claims map to one report and one is uncredited.
- A rejection reason contradicts the claim's recorded evidence.
- The program changed and the old mapping is stale.

## Patterns

**1. Filed report**

```text
SP-001 -> report 4412, 2026-10-29
```

**2. Rejected**

```text
SP-002 -> report 4413, rejected as duplicate of 441
```

**3. Unfiled claim**

```text
SP-003 -> held, needs a second entry point
```

## Pitfalls

- Filing a claim and never recording the report id.
- Losing a rejection reason and re-filing the same claim.
- Letting two claims share a report without noting which is which.

## Done when

- Every submitted claim has a report id, a date and a status.
- Unfiled verified claims are listed with the reason they are held.

## References

- [HackerOne - report states](https://docs.hackerone.com/en/articles/8475114-scope)
- [Bugcrowd - submission guidelines](https://docs.bugcrowd.com/researchers/reporting-managing-submissions/)
