---
name: snippet-hash-anchoring
description: "Hash the exact line you quoted, so a claim can prove its bytes instead of relying on a line number that any edit above will move. Use when every claim, because a line number alone is the weakest possible anchor"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [ground, anchor, integrity]
---

# Snippet Hash Anchoring

> Hash the exact line you quoted, so a claim can prove its bytes instead of relying on a line number that any edit above will move

**Use when:** every claim, because a line number alone is the weakest possible anchor

**Avoid when:** never; the digest costs one command and survives refactors

## Procedure

1. Take the exact source line containing the sink call.
2. Strip only leading and trailing whitespace before hashing.
3. Hash the result with SHA-256 and record the hex digest in the claim.
4. Record the human-readable text as well, for the reviewer.
5. Re-hash after any reformatting of the tree.
6. Treat a digest mismatch as a moved claim, not a false finding.

## Signals

- The line number still points at code, but not the same code.
- The digest matches a line in a different file.
- Reformatting the repository broke every claim at once.
- The claim quotes a line that appears in three places.

## Patterns

**1. Hash the line**

```text
memcpy(dst, src, (size_t)len);  ->  sha256 of the trimmed text
```

**2. Indentation ignored**

```text
four spaces vs eight spaces  -> same digest
```

**3. Move detection**

```text
digest found at parse.c:14  -> the fix moved the line
```

## Pitfalls

- Hashing the file instead of the line, so every unrelated edit breaks the claim.
- Hashing with indentation included and then reformatting the tree.
- Updating the digest to match an edited line instead of re-verifying the finding.

## Done when

- The claim carries a digest and the text it hashes to.
- A moved line is detected by digest rather than by eye.

## References

- [RFC 6234 - SHA algorithms](https://www.rfc-editor.org/rfc/rfc6234)
- [NIST - SP 800-86 forensic techniques](https://csrc.nist.gov/pubs/sp/800/86/final)
