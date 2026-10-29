---
name: cross-file-resolution
description: "Resolve hops across translation units by name, and say when a name is ambiguous, because the tree is not a linker and cannot pick the right symbol for you. Use when the path crosses files, packages or modules"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [graph, resolution, source]
---

# Cross File Resolution

> Resolve hops across translation units by name, and say when a name is ambiguous, because the tree is not a linker and cannot pick the right symbol for you

**Use when:** the path crosses files, packages or modules

**Avoid when:** every hop lives in the same file, so a name can only resolve to one definition

## Procedure

1. Index definitions by name across the whole tree.
2. For each hop, list the candidate definitions.
3. Prefer a candidate in the caller's file, then in the same package.
4. Record the choice and the reason when candidates remain.
5. Check headers and imports to see which declaration the caller sees.
6. Mark genuinely ambiguous hops rather than picking silently.

## Signals

- Two files define a function with the same name.
- A static function shadows a global one.
- The caller includes one of two headers that declare the same symbol.
- The same name is a method on two unrelated classes.

## Patterns

**1. Same file first**

```text
parse.c defines copy_field  -> prefer it
```

**2. Included header**

```text
#include "parse.h"  -> narrows the declaration
```

**3. Static linkage**

```text
static int read_message  -> file-local, unambiguous
```

## Pitfalls

- Matching the first definition in sort order and calling it resolved.
- Ignoring static linkage, which makes two same-named functions unrelated.
- Treating a method name as a free function when resolving a hop.

## Done when

- Each hop records which definition it resolved to and why.
- Ambiguous hops are flagged rather than silently chosen.

## References

- [CWE-710 - coding standards violation](https://cwe.mitre.org/data/definitions/710.html)
- [GCC - linkage](https://gcc.gnu.org/onlinedocs/gcc/Code-Gen-Options.html)
