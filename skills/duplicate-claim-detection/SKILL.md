---
name: duplicate-claim-detection
description: "Flag repeated anchors and repeated ids automatically, because a ledger that accumulates duplicates makes its own counts meaningless. Use when every ledger verification run, so duplicates cannot accumulate quietly over a review"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [ledger, dedupe, quality]
---

# Duplicate Claim Detection

> Flag repeated anchors and repeated ids automatically, because a ledger that accumulates duplicates makes its own counts meaningless

**Use when:** every ledger verification run, so duplicates cannot accumulate quietly over a review

**Avoid when:** the ledger holds one claim that is filed and closed in the same session

## Procedure

1. Detect repeated ids and treat them as blocking.
2. Detect repeated anchors and treat them as a merge candidate.
3. Read both claims before merging.
4. Merge the weaker exposure into the stronger claim.
5. Record the merge in both claim histories.
6. Re-run the check to confirm the counts.

## Signals

- Two entries share an id after a bad copy-paste.
- The same anchor appears with two severities.
- A retest added a claim instead of updating one.
- The total claim count grows without new code.

## Patterns

**1. Repeated id**

```text
two SP-004 entries  -> blocking, fix the id
```

**2. Repeated anchor**

```text
same sink and path  -> merge
```

**3. Retest update**

```text
updated evidence on the original claim
```

## Pitfalls

- Renaming the duplicate instead of merging it.
- Merging claims that share a sink but differ in entry point.
- Letting duplicate ids through because the file still parses.

## Done when

- No id appears twice and no anchor appears twice without a recorded reason.
- Merged claims keep one id and one set of evidence.

## References

- [HackerOne - duplicate handling](https://docs.hackerone.com/en/articles/8475114-scope)
- [Bugcrowd - duplicate policy](https://docs.bugcrowd.com/researchers/reporting-managing-submissions/)
