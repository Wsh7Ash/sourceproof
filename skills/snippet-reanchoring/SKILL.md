---
name: snippet-reanchoring
description: "Move a claim by searching for its quoted line, because a line number is a hint and the bytes are the anchor. Use when the snippet digest no longer matches at the recorded line"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [locate, anchor, drift]
---

# Snippet Reanchoring

> Move a claim by searching for its quoted line, because a line number is a hint and the bytes are the anchor

**Use when:** the snippet digest no longer matches at the recorded line

**Avoid when:** the quoted line is so generic that it appears many times

## Procedure

1. Search the tree for a line whose normalised text hashes to the digest.
2. If exactly one hit exists, re-anchor the claim to it.
3. If several exist, narrow by file, then by enclosing function.
4. If none exist, treat the snippet as changed and re-review the code.
5. Record the move in the claim's history rather than overwriting the old line.
6. Re-verify the path after re-anchoring.

## Signals

- Exactly one hit, in the same file, a few lines down.
- Several hits because the line is a common idiom.
- No hit because a formatter rewrapped the statement.
- The hit is in a vendored copy of the same file.

## Patterns

**1. Single hit**

```text
digest at parse.c:14  -> re-anchor, keep the finding
```

**2. Many hits**

```text
same line in three branches  -> narrow by revision
```

**3. No definition**

```text
the statement was rewritten  -> re-review, do not guess
```

## Pitfalls

- Picking the first of several digest hits without narrowing.
- Re-anchoring to a vendored copy that ships separately.
- Editing the stored line without re-verifying the path.

## Done when

- The claim points at a line whose digest matches, and the move is recorded.
- Ambiguous hits are narrowed by file and function before re-anchoring.

## References

- [RFC 6234 - SHA algorithms](https://www.rfc-editor.org/rfc/rfc6234)
- [Git - blame and history](https://git-scm.com/docs/git-blame)
