---
name: line-range-validation
description: "Reject a line past the end of the file before reading it, because a stale claim with a large line number silently resolves to nothing and looks like a clean check. Use when every check that reads a line by number"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [locate, validation, anchor]
---

# Line Range Validation

> Reject a line past the end of the file before reading it, because a stale claim with a large line number silently resolves to nothing and looks like a clean check

**Use when:** every check that reads a line by number

**Avoid when:** never; this is the cheapest guard in the tool

## Procedure

1. Read the file and count its lines.
2. Reject line zero and negative values.
3. Reject a line greater than the count.
4. Distinguish a missing file from a short file in the error.
5. Record both the requested and the actual line count on failure.
6. Re-anchor rather than truncating the line number.

## Signals

- The file shrank after the claim was written.
- The line number is zero because the field was left empty.
- The file was replaced by a shorter stub.
- The claim was written against a generated file that is no longer produced.

## Patterns

**1. Range check**

```text
line 40 in a 27-line file  -> blocking, with counts
```

**2. Zero line number**

```text
line 0  -> a missing field, not a location
```

**3. Re-anchor**

```text
search the digest first, then validate the result
```

## Pitfalls

- Indexing a list by line number and letting the exception decide.
- Treating a missing file as an empty one with zero lines.
- Clamping the line to the last line, which silently points at the wrong code.

## Done when

- Out-of-range lines are rejected with both counts in the message.
- A missing file is reported separately from a short one.

## References

- [OWASP - code review guide](https://owasp.org/www-project-code-review-guide/)
- [NIST - SP 800-115 testing guide](https://csrc.nist.gov/pubs/sp/800/115/final)
