---
name: recursion-and-cycle-handling
description: "Treat cycles as bounded, because a recursive path search that ignores depth either loops forever or reports a path that unwinds before reaching the sink. Use when the tree contains recursive functions or mutual recursion on the path"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [graph, recursion, search]
---

# Recursion and Cycle Handling

> Treat cycles as bounded, because a recursive path search that ignores depth either loops forever or reports a path that unwinds before reaching the sink

**Use when:** the tree contains recursive functions or mutual recursion on the path

**Avoid when:** the call graph is acyclic and small

## Procedure

1. Detect self-calls and mutual recursion among the path functions.
2. Bound the search depth and record the bound used.
3. Check whether the sink is reached on the first pass or a later recursion level.
4. Record the recursion condition that has to hold for the sink to be reached.
5. Prefer the shortest path, and note when a recursive edge is the only route.
6. Report the depth bound alongside the result.

## Signals

- The function calls itself in a loop over children.
- Two functions call each other.
- The path finder returns a path longer than the graph's diameter.
- The sink is only reachable when the recursion terminates early.

## Patterns

**1. Self-call**

```text
walk(dir) calls walk(child)  -> bounded by depth
```

**2. Mutual recursion**

```text
parse calls lex, lex calls parse  -> cycle, needs a visited set
```

**3. Depth bound**

```text
max 12 hops  -> recorded with the result
```

## Pitfalls

- Searching without a visited set and looping until timeout.
- Reporting a path that relies on infinite recursion.
- Ignoring that the recursive call is the edge that reaches the sink.

## Done when

- The search bound and the visited set are both in the implementation or the record.
- Any recursive hop is named as recursive in the claim.

## References

- [CWE-674 - uncontrolled recursion](https://cwe.mitre.org/data/definitions/674.html)
- [Wikipedia - breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)
