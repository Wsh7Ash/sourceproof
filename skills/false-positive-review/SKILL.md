---
name: false-positive-review
description: "Try to kill the claim before filing it, because the cheapest place to find a false positive is your own ledger. Use when a claim verifies and is about to be submitted"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [grade, review, quality]
---

# False Positive Review

> Try to kill the claim before filing it, because the cheapest place to find a false positive is your own ledger

**Use when:** a claim verifies and is about to be submitted

**Avoid when:** the claim is a draft that will be reviewed by someone else first

## Procedure

1. Assume the code is correct and look for why the value cannot reach the sink.
2. Check the argument types and coercions at the call.
3. Check for a guard inside the sink's own implementation.
4. Check whether the input is length-limited before the sink.
5. Check whether the source of the value is actually untrusted.
6. Record the attempt and what survived it.

## Signals

- The value comes from a constant the program controls.
- The sink is a wrapper that validates internally.
- The input was already clamped by the framework.
- The path exists but the condition can never hold.

## Patterns

**1. Constant source**

```text
name comes from a static table  -> not attacker-controlled
```

**2. Internal guard**

```text
copy_field checks len against dst  -> claim dies here
```

**3. Framework clamp**

```text
the body parser caps Content-Length  -> reachability weakened
```

## Pitfalls

- Filing the first claim that verifies without trying to refute it.
- Accepting the sink at face value without reading its implementation.
- Ignoring a framework limit because it is outside the reviewed file.

## Done when

- At least one specific refutation was attempted and recorded.
- The claim states why the value is attacker-controlled and unbounded.

## References

- [OWASP - code review guide](https://owasp.org/www-project-code-review-guide/)
- [CWE-20 - improper input validation](https://cwe.mitre.org/data/definitions/20.html)
