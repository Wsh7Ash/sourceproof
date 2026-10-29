---
name: build-variant-awareness
description: "State which build or branch the claim describes, because a sink compiled out by a feature flag is not a finding on the shipped artefact. Use when the code is behind preprocessor branches, feature flags or build tags"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [ground, build, scope]
---

# Build Variant Awareness

> State which build or branch the claim describes, because a sink compiled out by a feature flag is not a finding on the shipped artefact

**Use when:** the code is behind preprocessor branches, feature flags or build tags

**Avoid when:** the tree has a single unconditional build path

## Procedure

1. Identify the branch or tag the reviewed tree came from.
2. Find build flags that guard the sink or the path.
3. Determine whether the shipped build defines those flags.
4. Record the flag state in the claim next to the line.
5. If the flag state is unknown, mark the claim needs-review rather than verified.
6. Re-check when the build configuration changes.

## Signals

- The sink is inside an ifdef that defaults to off.
- Two branches implement the same function differently.
- The release build strips the debug path where the bug lives.
- The claim cites a file that does not exist on the release branch.

## Patterns

**1. Default off**

```text
#ifdef DEBUG around the copy  -> not in the shipped build
```

**2. Branch pin**

```text
reviewed main 7c1e9ab, not release/2.3
```

**3. Flag state**

```text
WITH_UPLOAD=1 in the release config  -> reachable
```

## Pitfalls

- Reviewing develop and reporting against the release build.
- Missing that a guard macro is defined by the build system, not the source.
- Treating a debug-only path as shipped reachability.

## Done when

- The claim names the branch and the guard state that make the sink live.
- Unknown flag state is recorded as needs-review.

## References

- [GCC - conditional compilation](https://gcc.gnu.org/onlinedocs/cpp/Conditional-Syntax.html)
- [CWE-489 - active debug code](https://cwe.mitre.org/data/definitions/489.html)
