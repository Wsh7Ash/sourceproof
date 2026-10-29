---
name: dynamic-dispatch-limits
description: "Declare when a hop is dispatched at runtime, because a virtual call or a function pointer is not an edge the tree can confirm. Use when the path crosses an interface call, a function pointer, or a message bus"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [graph, dynamic, limits]
---

# Dynamic Dispatch Limits

> Declare when a hop is dispatched at runtime, because a virtual call or a function pointer is not an edge the tree can confirm

**Use when:** the path crosses an interface call, a function pointer, or a message bus

**Avoid when:** all hops are direct calls between statically resolvable functions

## Procedure

1. Identify every hop that is dispatched through a pointer, vtable or registry.
2. Find the assignments that install concrete implementations.
3. Narrow to the implementation that is registered for the reviewed build.
4. Record the dispatch site and the installed target.
5. Mark hops whose target cannot be narrowed as unproven.
6. Never claim a virtual hop as a direct edge.

## Signals

- The call is through a struct of function pointers.
- The implementation is chosen by a config string at startup.
- The registry is populated in a different translation unit.
- The interface has one implementation in the tree but more at runtime.

## Patterns

**1. Installed pointer**

```text
ops->read = file_read  -> the edge to file_read
```

**2. Registry**

```text
register_handler('upload', parse_headers)  -> name the key
```

**3. Unnarrowable**

```text
target loaded from a plugin  -> unproven, say so
```

## Pitfalls

- Treating an interface method call as an edge to every implementation.
- Ignoring that a plugin can replace the implementation at runtime.
- Claiming reachability through a pointer that is never assigned in the tree.

## Done when

- Each dynamic hop records its dispatch site and its narrowed target, or is marked unproven.
- The claim does not present a dynamic hop as a verified direct edge.

## References

- [CWE-470 - unsafe reflection](https://cwe.mitre.org/data/definitions/470.html)
- [CWE-477 - obsolete functions](https://cwe.mitre.org/data/definitions/477.html)
