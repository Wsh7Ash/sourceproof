---
name: duplicate-snippet-disambiguation
description: "Break ties with the enclosing function and the file, because a copied line is the normal case in generated and vendored code. Use when a snippet digest matches in more than one place"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [locate, dedupe, anchor]
---

# Duplicate Snippet Disambiguation

> Break ties with the enclosing function and the file, because a copied line is the normal case in generated and vendored code

**Use when:** a snippet digest matches in more than one place

**Avoid when:** the digest is unique in the tree

## Procedure

1. List every hit with its file and enclosing function.
2. Compare the enclosing functions with the claimed last hop.
3. Compare the files with the claimed path's files.
4. Prefer the hit whose path still verifies end to end.
5. If two hits both verify, report both sites rather than choosing.
6. Record the tie-break rule used.

## Signals

- The same helper is copied into two services.
- A generated file mirrors a hand-written one.
- One hit is under a vendored directory.
- Both hits verify but one is behind a disabled route.

## Patterns

**1. Function tie-break**

```text
hit inside copy_field vs main  -> copy_field
```

**2. File tie-break**

```text
the hit in the file the path names
```

**3. Report both**

```text
two live services, same code  -> two claims, not one
```

## Pitfalls

- Choosing a hit at random and reporting the wrong service.
- Merging two live sites into one claim and understating the spread.
- Ignoring a vendored copy that is deployed separately.

## Done when

- Every digest hit is classified as claimed, other, or vendored.
- Two independently deployed sites produce two claims.

## References

- [CWE-1104 - use of unmaintained components](https://cwe.mitre.org/data/definitions/1104.html)
- [Git - copying directories](https://git-scm.com/docs/git-log)
