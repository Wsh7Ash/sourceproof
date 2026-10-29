---
name: dedupe-by-anchor
description: "Compare claims by anchor rather than title, because two findings about one sink at one path are one finding however differently they are worded. Use when adding a claim to a ledger that already has entries"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [grade, dedupe, ledger]
---

# Dedupe by Anchor

> Compare claims by anchor rather than title, because two findings about one sink at one path are one finding however differently they are worded

**Use when:** adding a claim to a ledger that already has entries

**Avoid when:** the ledger is brand new and empty

## Procedure

1. Compute the anchor from sink file, sink function, kind and path.
2. Compare with every existing anchor.
3. Read any match's claim before deciding.
4. Merge when the anchor and the mechanism match.
5. Keep separate when the anchors match but the mechanisms differ.
6. Record the merge or the reason for keeping both.

## Signals

- Two claims have different titles and the same anchor.
- One claim is a subset of another's path.
- The same sink is reached by two different entries.
- A retest produced a new claim for a fixed one.

## Patterns

**1. Same anchor**

```text
identical path and sink  -> one claim
```

**2. Subset path**

```text
shorter path to the same sink  -> merge, keep the weaker exposure
```

**3. Different entry**

```text
two routes, two exposures  -> two claims sharing a sink
```

## Pitfalls

- Deduping on the title and filing the same bug twice.
- Merging two different entries that reach one sink with different exposure.
- Keeping a retest claim separate instead of updating the original.

## Done when

- No two claims share an anchor unless their difference is recorded.
- Merged claims keep the weakest exposure of the set.

## References

- [HackerOne - duplicate handling](https://docs.hackerone.com/en/articles/8475114-scope)
- [Bugcrowd - duplicate policy](https://docs.bugcrowd.com/researchers/reporting-managing-submissions/)
