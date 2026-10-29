---
name: command-execution-sinks
description: "Check whether the command string is built from input or selected from a fixed set, because only the first is command injection. Use when the path reaches system, popen, exec, subprocess or a shell wrapper"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [sink, command, injection]
---

# Command Execution Sinks

> Check whether the command string is built from input or selected from a fixed set, because only the first is command injection

**Use when:** the path reaches system, popen, exec, subprocess or a shell wrapper

**Avoid when:** the command is a constant with no interpolated value

## Procedure

1. Read the command string and mark every interpolated value.
2. Trace each interpolated value to its source.
3. Check whether the call uses a shell or an argument vector.
4. Check whether a library call takes an array, which removes shell parsing.
5. Check for quoting or an allowlist applied to the value.
6. Record the exact command text and the interpolation.

## Signals

- The command is assembled with string concatenation.
- A shell=True or a /bin/sh -c wrapper is present.
- The interpolated value is a filename from the request.
- An argument vector is used, so metacharacters are inert.

## Patterns

**1. Injection**

```text
system("convert " + name)  -> name is parsed by the shell
```

**2. Argument vector**

```text
subprocess.run(["convert", name])  -> no shell, different bug class
```

**3. Allowlist**

```text
name in {"a.png","b.png"}  -> guarded
```

## Pitfalls

- Reporting an argument-vector call as shell injection.
- Missing that the binary path itself is attacker-controlled.
- Assuming quotes make a value safe when the shell still expands inside them.

## Done when

- The command text, the interpolation and the shell mode are recorded.
- Any allowlist or escaping is quoted exactly.

## References

- [CWE-78 - OS command injection](https://cwe.mitre.org/data/definitions/78.html)
- [OWASP - command injection](https://owasp.org/www-community/attacks/Command_Injection)
