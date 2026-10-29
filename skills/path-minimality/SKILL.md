---
name: path-minimality
description: "Report the shortest path that actually reaches the sink, because a padded path is harder to verify and hides which hop is load-bearing. Use when several call paths reach the same sink"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [graph, path, reporting]
---

# Path Minimality

> Report the shortest path that actually reaches the sink, because a padded path is harder to verify and hides which hop is load-bearing

**Use when:** several call paths reach the same sink

**Avoid when:** exactly one path exists and it is already short

## Procedure

1. Search breadth-first so the first path found is the shortest.
2. Count hops and record the count next to the path.
3. Check whether a shorter path exists through a different entry.
4. Drop hops that only appear because of the search order.
5. Keep the path that a reviewer can verify in the fewest reads.
6. Note any other path that is materially different, such as pre-auth versus authenticated.

## Signals

- The path goes through a helper that adds nothing.
- Two entries reach the sink, one with weaker auth.
- The path length changes between runs because iteration order is not fixed.
- A shorter path exists but was not searched because of a depth limit.

## Patterns

**1. Shortest**

```text
4 hops through dispatch  -> report it
```

**2. Alternative**

```text
a 6-hop authenticated path exists  -> mention, do not lead with it
```

**3. Deterministic**

```text
callers visited in name order  -> same path every run
```

## Pitfalls

- Reporting a long path because it was found first by depth-first search.
- Omitting the pre-auth alternative in favour of a shorter authenticated one.
- Letting non-deterministic iteration produce a different path each run.

## Done when

- The reported path is the shortest found, with its hop count.
- Alternative paths with different exposure are recorded separately.

## References

- [Wikipedia - shortest path problem](https://en.wikipedia.org/wiki/Shortest_path_problem)
- [OWASP - attack surface analysis](https://owasp.org/www-community/Attack_Surface_Analysis_Cheat_Sheet)
