---
name: dynamic-code-sinks
description: "Distinguish evaluation of a constant template from evaluation of request data, because eval on a fixed string is not remote code execution. Use when the path reaches eval, exec, compile, Function or a template renderer"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [sink, eval, code]
---

# Dynamic Code Sinks

> Distinguish evaluation of a constant template from evaluation of request data, because eval on a fixed string is not remote code execution

**Use when:** the path reaches eval, exec, compile, Function or a template renderer

**Avoid when:** the evaluated string is a literal in the binary

## Procedure

1. Identify the string being evaluated.
2. Determine whether any part of it is input-derived.
3. If templating is involved, find the template and whether it is user-supplied.
4. Check the context passed to the evaluator, which may expose more than intended.
5. Check for a sandbox and what it actually restricts.
6. Record the evaluated expression and the input-derived fragment.

## Signals

- The evaluated string is built from a request field.
- The template file is uploadable.
- The sandbox is a globals dict that still exposes builtins.
- The expression is compiled once from a config value and never re-derived.

## Patterns

**1. Constant**

```text
eval("1 + 1")  -> not a finding
```

**2. Template**

```text
render_template(request.args['t'])  -> server-side template injection
```

**3. Sandboxed**

```text
SafeGlobals without builtins  -> weaker, still review
```

## Pitfalls

- Reporting every eval call regardless of what it evaluates.
- Assuming a template engine escapes when it only escapes HTML context.
- Trusting a sandbox without reading what it removes.

## Done when

- The evaluated string and its input-derived fragment are recorded.
- Any sandbox or allowlist is quoted exactly.

## References

- [CWE-95 - code injection](https://cwe.mitre.org/data/definitions/95.html)
- [CWE-1336 - template injection](https://cwe.mitre.org/data/definitions/1336.html)
