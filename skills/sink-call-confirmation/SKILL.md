---
name: sink-call-confirmation
description: "Confirm the line actually calls the sink, because a name in a comment, a string or a wrapper is not a call and triage closes those reports. Use when the claim names a dangerous function at a specific line"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [ground, sink, verification]
---

# Sink Call Confirmation

> Confirm the line actually calls the sink, because a name in a comment, a string or a wrapper is not a call and triage closes those reports

**Use when:** the claim names a dangerous function at a specific line

**Avoid when:** the sink is reached through a function pointer the tree cannot resolve

## Procedure

1. Read the line and locate the function name.
2. Check that the name is followed by an open parenthesis.
3. Check that the name is not inside a string literal or a comment.
4. Check that the call is a call, not a declaration or a prototype.
5. Confirm the arguments include the attacker-controlled value.
6. Record the call text in the claim as proof.

## Signals

- The line is a comment that mentions the function.
- The name appears in a log message.
- The line is a prototype ending in a semicolon.
- The call passes a constant, so the value is not attacker-controlled.

## Patterns

**1. Real call**

```text
memcpy(dst, src, (size_t)len);  -> sink confirmed
```

**2. In a comment**

```text
/* memcpy goes here */  -> not a sink
```

**3. Via a wrapper**

```text
safe_copy(dst, src, len)  -> the wrapper is the hop, not the sink
```

## Pitfalls

- Grepping for the name and reporting the first hit, which is often an include.
- Accepting a prototype as a call site.
- Naming the sink when the code calls a wrapper that may sanitise.

## Done when

- The sink line is a real call with an attacker-controlled argument.
- The call text is recorded, not just the function name.

## References

- [CWE-119 - buffer overflow](https://cwe.mitre.org/data/definitions/119.html)
- [OWASP - code review guide](https://owasp.org/www-project-code-review-guide/)
