---
name: impact-statement
description: "State what the verified path lets an attacker do, because the path proves reachability and says nothing about the effect on its own. Use when writing the impact section of a verified claim"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [grade, impact, reporting]
---

# Impact Statement

> State what the verified path lets an attacker do, because the path proves reachability and says nothing about the effect on its own

**Use when:** writing the impact section of a verified claim

**Avoid when:** the claim is an internal note whose impact is already agreed

## Procedure

1. Name the primitive: read, write, execute, or state change.
2. Name the data or control it touches.
3. Name the attacker position required.
4. Separate what the code shows from what you infer.
5. Remove any consequence that needs a second unproven bug.
6. Tie the severity to the demonstrated primitive.

## Signals

- The impact says remote code execution and the path ends at a read.
- The impact assumes a second bug to become exploitable.
- The attacker position is not stated.
- The impact is a restatement of the sink kind.

## Patterns

**1. Primitive**

```text
write past a 64-byte stack buffer  -> control-flow or crash
```

**2. Position**

```text
unauthenticated POST to /upload  -> remote
```

**3. Inference split**

```text
shown: out-of-bounds write; not shown: reliable control
```

## Pitfalls

- Escalating a crash to code execution in the impact line.
- Burying a strong precondition in an appendix.
- Writing impact as a copy of the sink's name.

## Done when

- The impact names a primitive, a target and an attacker position.
- Speculative consequences are labelled as inference.

## References

- [FIRST - CVSS v3.1 specification](https://www.first.org/cvss/v3-1/specification-document)
- [Bugcrowd - vulnerability rating taxonomy](https://bugcrowd.com/vulnerability-rating-taxonomy)
