---
name: path-traversal-sinks
description: "Check canonicalisation, not just for dots, because a check applied before normalisation is bypassed by an encoded sequence. Use when the path reaches a file open, read or write with an input-derived name"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [sink, path, filesystem]
---

# Path Traversal Sinks

> Check canonicalisation, not just for dots, because a check applied before normalisation is bypassed by an encoded sequence

**Use when:** the path reaches a file open, read or write with an input-derived name

**Avoid when:** the filename is selected from a fixed map

## Procedure

1. Find the input-derived part of the path.
2. Find where normalisation happens relative to the check.
3. Check whether the resolved path is confined to a base directory.
4. Check encoded forms: percent, double percent, unicode, backslash.
5. Check for a null byte or a trailing separator trick.
6. Record the check, its position relative to canonicalisation, and the bypass.

## Signals

- The code rejects a substring but opens the raw value.
- The base directory is prepended after the value is normalised.
- A symlink in the writable directory escapes the base.
- The check strips a prefix once, so a doubled prefix survives.

## Patterns

**1. Checked before**

```text
if (strstr(name, "..")) reject; fopen(name)  -> encoded bypass
```

**2. Checked after**

```text
realpath(name) then prefix compare  -> confined
```

**3. Symlink escape**

```text
base is writable, link points outside  -> traversal by link
```

## Pitfalls

- Accepting a substring check as traversal prevention.
- Missing backslash handling when the code also runs on Windows.
- Forgetting that the writable upload directory makes symlinks an escape.

## Done when

- The check, its ordering and the base confinement are all recorded.
- At least one encoded form was tested against the check.

## References

- [CWE-22 - path traversal](https://cwe.mitre.org/data/definitions/22.html)
- [OWASP - path traversal](https://owasp.org/www-community/attacks/Path_Traversal)
