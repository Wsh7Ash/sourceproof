---
name: ledger-format
description: "Keep claims in one machine-readable file per engagement, because a folder of prose documents cannot be re-verified in one pass. Use when starting an engagement or moving claims out of notes"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [ledger, format, process]
---

# Ledger Format

> Keep claims in one machine-readable file per engagement, because a folder of prose documents cannot be re-verified in one pass

**Use when:** starting an engagement or moving claims out of notes

**Avoid when:** there is exactly one claim and it will be filed immediately

## Procedure

1. Choose one file format and one schema version.
2. Store one claim per line or one document with a claims array.
3. Keep the schema version in every claim.
4. Keep the ledger in version control alongside the review.
5. Never mix hand-edited prose into the ledger file.
6. Validate the whole file after every edit.

## Signals

- The file has claims in two different shapes.
- A claim lacks a schema field.
- The ledger is a directory of markdown files.
- Two people edited the same line and one claim was lost.

## Patterns

**1. JSONL ledger**

```text
one claim per line  -> diffable and appendable
```

**2. Document**

```text
claims array in one object  -> easy to review whole
```

**3. Versioned**

```text
"schema": "sourceproof/v1"  -> parsed strictly
```

## Pitfalls

- Mixing formats so half the ledger silently fails to load.
- Storing the ledger outside version control and losing the history.
- Appending a claim by hand and breaking the JSON of the line above.

## Done when

- Every entry parses under one declared schema version.
- The ledger is versioned with the review it belongs to.

## References

- [JSON Lines](https://jsonlines.org/)
- [JSON Schema](https://json-schema.org/)
