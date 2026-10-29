---
name: sanitizer-recognition
description: "Read what a sanitiser actually guarantees, because an escape function for one context does not protect a different sink. Use when a validation or escaping call sits between the input and the sink"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [sink, sanitizer, context]
---

# Sanitizer Recognition

> Read what a sanitiser actually guarantees, because an escape function for one context does not protect a different sink

**Use when:** a validation or escaping call sits between the input and the sink

**Avoid when:** there is no sanitiser on the path at all

## Procedure

1. Name the sanitiser and the context it is written for.
2. Check that the context matches the sink: SQL, shell, HTML, path, header.
3. Check that a sanitiser for a different context is not being reused.
4. Check that the sanitiser runs on every path to the sink.
5. Check for a decode after the sanitiser that re-introduces the payload.
6. Record the sanitiser, its context and the sink it protects.

## Signals

- htmlspecialchars is used before a SQL query.
- The escape happens before a decode step.
- A sanitiser is applied in the controller but not in the second route.
- The function name says escape but the body only strips quotes.

## Patterns

**1. Right context**

```text
parameter binding before execute  -> protects that statement
```

**2. Wrong context**

```text
HTML escaping before system()  -> no protection
```

**3. Check ordering**

```text
escape then url_decode  -> payload restored
```

## Pitfalls

- Accepting any escaping call as proof of safety.
- Missing a second entry point that skips the sanitiser.
- Treating an allowlist check on one argument as covering all of them.

## Done when

- The sanitiser, its context and the sink it guards are recorded together.
- Every path to the sink is checked for the sanitiser.

## References

- [OWASP - cross site scripting prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [CWE-116 - improper encoding of output](https://cwe.mitre.org/data/definitions/116.html)
