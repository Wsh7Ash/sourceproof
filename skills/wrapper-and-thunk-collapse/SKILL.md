---
name: wrapper-and-thunk-collapse
description: "Decide whether a wrapper is part of the path or a guard on it, because collapsing wrappers can hide the check that makes the sink safe. Use when the path passes through thin wrappers, adapters or generated thunks"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [graph, path, wrappers]
---

# Wrapper and Thunk Collapse

> Decide whether a wrapper is part of the path or a guard on it, because collapsing wrappers can hide the check that makes the sink safe

**Use when:** the path passes through thin wrappers, adapters or generated thunks

**Avoid when:** every hop is a substantial function that does real work

## Procedure

1. Read each wrapper on the path in full.
2. Check whether it validates, truncates or escapes its arguments.
3. Keep a wrapper in the path when it transforms the input.
4. Collapse a wrapper only when it forwards arguments unchanged.
5. Record the collapse in the claim so a reviewer can undo it.
6. Re-expand when the wrapper's implementation changes.

## Signals

- The wrapper has a length check the claim never mentions.
- The wrapper is a macro that expands to the real call.
- The wrapper clamps the length to the destination size.
- Two wrappers on the path do the same job at different layers.

## Patterns

**1. Guard wrapper**

```text
safe_copy checks len <= sizeof(dst)  -> the sink is safe
```

**2. Pure thunk**

```text
retry(parse_headers, body)  -> forwarding, collapse it
```

**3. Transform**

```text
decode_then_copy escapes before copying  -> keep it
```

## Pitfalls

- Collapsing a wrapper that contains the only bounds check.
- Keeping every generated thunk in the path until it becomes unreadable.
- Assuming a wrapper with a safe name is safe.

## Done when

- Each collapsed wrapper is recorded with why it forwards unchanged.
- No wrapper containing validation is collapsed.

## References

- [CWE-1173 - improper use of validation framework](https://cwe.mitre.org/data/definitions/1173.html)
- [OWASP - code review guide](https://owasp.org/www-project-code-review-guide/)
