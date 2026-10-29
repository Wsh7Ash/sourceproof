---
name: sql-execution-sinks
description: "Check whether the value is bound or interpolated, because a parameterised query with a concatenated table name is still injectable. Use when the path reaches a query builder or a raw execute call"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [sink, sql, injection]
---

# SQL Execution Sinks

> Check whether the value is bound or interpolated, because a parameterised query with a concatenated table name is still injectable

**Use when:** the path reaches a query builder or a raw execute call

**Avoid when:** the statement is a constant with no input-derived fragment

## Procedure

1. Read the statement and mark every input-derived fragment.
2. Check whether values are passed as bound parameters.
3. Check identifiers: table and column names cannot be bound.
4. Check the driver's string formatting, which may interpolate before binding.
5. Check for an ORM raw block that bypasses parameterisation.
6. Record the statement and the fragment that is not bound.

## Signals

- The query is built with a format operator or concatenation.
- Only the WHERE value is bound, while the sort column is interpolated.
- The ORM exposes a raw or literal escape hatch on this path.
- The driver quotes values but not identifiers.

## Patterns

**1. Interpolated**

```text
cur.execute("... VALUES ('%s')" % name)  -> injectable
```

**2. Bound parameters**

```text
cur.execute("... VALUES (?)", (name,))  -> value safe
```

**3. Identifier**

```text
ORDER BY " + column  -> still injectable when values are bound
```

## Pitfalls

- Calling a finding safe because a prepared statement is used, when the identifier is concatenated.
- Missing a raw block inside an otherwise safe ORM call.
- Ignoring second-order injection through stored values.

## Done when

- The statement text and the unbound fragment are recorded.
- Identifier interpolation is treated as injectable unless allowlisted.

## References

- [CWE-89 - SQL injection](https://cwe.mitre.org/data/definitions/89.html)
- [OWASP - SQL injection prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
