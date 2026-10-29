---
name: format-string-sinks
description: "Check whether the format argument is a variable, because printf(user_input) is a different bug from printf(\"%s\", user_input). Use when the path reaches a printf-family or logging call"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [sink, format, memory]
---

# Format String Sinks

> Check whether the format argument is a variable, because printf(user_input) is a different bug from printf("%s", user_input)

**Use when:** the path reaches a printf-family or logging call

**Avoid when:** the format string is a literal and the values are arguments

## Procedure

1. Identify which argument is the format string.
2. Check whether it is a literal at the call site.
3. If it is a variable, trace where its value comes from.
4. Check for a wrapper that fixes the format and passes values separately.
5. Check the compiler's format warnings and whether they are suppressed.
6. Record the format argument and its source.

## Signals

- The first argument to the call is a request-derived string.
- The wrapper forwards the caller's format argument unchanged.
- Format warnings are disabled for that translation unit.
- A log macro takes the message as a format.

## Patterns

**1. Variable format**

```text
printf(msg) with msg from the request  -> format string bug
```

**2. Literal format**

```text
printf("%s", msg)  -> safe
```

**3. Via a wrapper**

```text
log_info(msg) forwards to printf(msg)  -> still a bug
```

## Pitfalls

- Reporting printf("%s", input) as a format string bug.
- Missing a logging wrapper that forwards the format argument.
- Ignoring that the value is a constant built by the program itself.

## Done when

- The format argument's origin is recorded, not just its type.
- Wrapper chains are followed to the real printf call.

## References

- [CWE-134 - uncontrolled format string](https://cwe.mitre.org/data/definitions/134.html)
- [OWASP - format string](https://owasp.org/www-community/attacks/Format_string_attack)
