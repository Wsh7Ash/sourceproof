---
name: symbol-resolution
description: "Resolve every name in the claim to a real definition, because a hop that exists only in prose is the most common way a path turns out to be invented. Use when the claim names functions across files, modules or packages"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [ground, symbols, source]
---

# Symbol Resolution

> Resolve every name in the claim to a real definition, because a hop that exists only in prose is the most common way a path turns out to be invented

**Use when:** the claim names functions across files, modules or packages

**Avoid when:** the finding is a single statement in one function with no call chain

## Procedure

1. List every function name in the claimed path.
2. Resolve each to at least one definition with a file and line.
3. Note names with several definitions and record which one is meant.
4. Note names with no definition: library calls, macros, generated code.
5. Separate the two lists, since only the first can be verified by the tree.
6. Write the unresolved names into the claim rather than dropping them.

## Signals

- A hop resolves to two definitions in different modules.
- A hop resolves to nothing, and the code compiles only because of a macro.
- The name is a wrapper that is generated at build time.
- Two functions share a name in different translation units.

## Patterns

**1. One definition**

```text
parse_headers -> src/parse.c:14  -> resolvable
```

**2. Several definitions**

```text
open -> three candidates  -> record which, or mark ambiguous
```

**3. No definition**

```text
memcpy -> libc, not in the tree  -> verified as a sink, not as a hop
```

## Pitfalls

- Assuming a hop exists because the code compiles.
- Picking the first definition when several share the name.
- Dropping an unresolved name from the path and shortening it silently.

## Done when

- Every hop resolves to a definition or is listed as unresolved with a reason.
- Ambiguous names record which definition the claim means.

## References

- [GNU C - name lookup](https://gcc.gnu.org/onlinedocs/cpp/Macro-Arguments.html)
- [CWE - code quality](https://cwe.mitre.org/data/definitions/710.html)
