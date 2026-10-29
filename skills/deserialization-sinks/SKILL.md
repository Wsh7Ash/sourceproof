---
name: deserialization-sinks
description: "Identify the format and the loader, because safe YAML and unsafe YAML call the same function name and differ only by argument. Use when the path reaches a parser for pickle, yaml, JSON, Java serialization or PHP unserialize"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [sink, deserialization, parser]
---

# Deserialization Sinks

> Identify the format and the loader, because safe YAML and unsafe YAML call the same function name and differ only by argument

**Use when:** the path reaches a parser for pickle, yaml, JSON, Java serialization or PHP unserialize

**Avoid when:** the data is parsed from a constant embedded in the binary

## Procedure

1. Identify the data format from the call site.
2. Identify the loader and its unsafe mode, if it has one.
3. Check whether the input is authenticated or integrity-protected.
4. Check whether the object graph is restricted to known types.
5. Check the library version, since defaults changed between releases.
6. Record the loader call and the argument that selects the unsafe mode.

## Signals

- yaml.load is called without a SafeLoader argument.
- Java readObject runs on a session cookie.
- PHP unserialize is given a request parameter.
- The data is signed, so an attacker cannot choose it.

## Patterns

**1. Unsafe loader**

```text
yaml.load(data)  -> arbitrary constructors
```

**2. Safe loader**

```text
yaml.safe_load(data)  -> plain types only
```

**3. Signed payload**

```text
MAC verified before unpickling  -> not attacker-chosen
```

## Pitfalls

- Treating JSON.parse as equivalent to pickle.loads.
- Missing the safe loader argument and calling the call safe.
- Ignoring that a signature check happens after deserialization.

## Done when

- The loader, its mode and the integrity check are recorded with lines.
- The claim states which condition makes the input attacker-controlled.

## References

- [CWE-502 - deserialization of untrusted data](https://cwe.mitre.org/data/definitions/502.html)
- [OWASP - deserialization cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html)
