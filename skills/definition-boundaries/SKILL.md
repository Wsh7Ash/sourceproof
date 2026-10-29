---
name: definition-boundaries
description: "Establish where each function starts and ends, because a sink two functions below the one you named is not reachable from that function at all. Use when the sink line must be attributed to an enclosing function"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [ground, parsing, source]
---

# Definition Boundaries

> Establish where each function starts and ends, because a sink two functions below the one you named is not reachable from that function at all

**Use when:** the sink line must be attributed to an enclosing function

**Avoid when:** the finding is a global initializer or a macro with no enclosing function

## Procedure

1. Find the nearest definition above the sink line in the same file.
2. Check that its closing brace comes after the sink line.
3. Check that no other definition starts between them.
4. Confirm the sink is inside the body, not in a nested local function.
5. Record the enclosing function in the claim.
6. If the attribution is ambiguous, say so instead of guessing.

## Signals

- The sink sits after a closing brace that looks like the function end.
- Two definitions appear to overlap because a brace is unbalanced.
- The sink is inside a macro body that expands into another function.
- The file uses significant indentation and a nested def shadows the outer one.

## Patterns

**1. Nearest above**

```text
parse.c:10 with defs at 8 and 14  -> copy_field
```

**2. Brace bound**

```text
the def at 8 closes at 12, so line 10 is inside it
```

**3. Nested definition**

```text
an inner def at Python indent 8 is its own boundary
```

## Pitfalls

- Attributing the sink to the file's first function because it is the biggest.
- Ignoring brace imbalance caused by a string containing a brace.
- Treating a nested definition as part of its parent for reachability.

## Done when

- The enclosing function is identified by start and end line.
- Ambiguous attribution is flagged rather than guessed.

## References

- [CWE - improper check of function return value](https://cwe.mitre.org/data/definitions/252.html)
- [Python - compound statements](https://docs.python.org/3/reference/compound_stmts.html)
