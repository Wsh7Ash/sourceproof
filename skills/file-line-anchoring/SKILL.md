---
name: file-line-anchoring
description: "Pin every claim to one repository-relative path and one line number, because a finding that says only which module it is in cannot be re-checked. Use when writing up a source-level finding that will be read by someone who is not sitting at your checkout"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [ground, anchor, source]
---

# File Line Anchoring

> Pin every claim to one repository-relative path and one line number, because a finding that says only which module it is in cannot be re-checked

**Use when:** writing up a source-level finding that will be read by someone who is not sitting at your checkout

**Avoid when:** the finding is a design observation with no specific faulty statement

## Procedure

1. Record the path relative to the repository root, using forward slashes.
2. Record the line of the sink call itself, not the line of the enclosing function.
3. Confirm the line number against the revision you actually reviewed.
4. Record the revision as a commit id next to the path.
5. Re-read the line after writing the claim, because tabs and editors shift numbering.
6. Never quote a path from an absolute local checkout.

## Signals

- The path starts with a drive letter or a home directory.
- The quoted line is a comment or a closing brace.
- The line number differs between your editor and the claim.
- The claim names a directory, not a file.

## Patterns

**1. Relative path**

```text
src/parse.c:10  -> the same number on any host
```

**2. Sink line**

```text
the line with the call, not the line with the signature
```

**3. Revision pinned**

```text
commit 7c1e9ab, so a moved line is explainable later
```

## Pitfalls

- Quoting a path from an absolute local checkout that no reviewer can resolve.
- Pointing at the function signature and calling the whole function the sink.
- Recording a line number from a different branch than the one you reviewed.

## Done when

- The claim has one relative path and one line, both checked against the tree.
- The revision under review is recorded beside them.

## References

- [CWE - software development view](https://cwe.mitre.org/data/definitions/699.html)
- [Git - revision identifiers](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
