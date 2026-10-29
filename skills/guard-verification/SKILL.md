---
name: guard-verification
description: "Verify that a guard runs on every path and covers the right value, because a check on a copy of the data does not protect the original. Use when a validation call sits on the claimed path"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [grade, guards, control-flow]
---

# Guard Verification

> Verify that a guard runs on every path and covers the right value, because a check on a copy of the data does not protect the original

**Use when:** a validation call sits on the claimed path

**Avoid when:** no guard exists between input and sink

## Procedure

1. Locate the guard and the value it checks.
2. Confirm it is the same variable the sink uses, not a copy.
3. Confirm it dominates the sink on every branch.
4. Confirm the comparison covers the dangerous range, including negatives.
5. Confirm the failure path actually returns rather than logging.
6. Record the guard's line and its exact condition.

## Signals

- The guard checks the pointer but not the length.
- The failure path logs and continues.
- The guard runs on one branch and the sink on both.
- The comparison is signed and the length unsigned.

## Patterns

**1. Dominates**

```text
if (len > sizeof field) return -1;  -> guard holds
```

**2. Log and continue**

```text
syslog then memcpy  -> no guard
```

**3. Signedness**

```text
int len vs size_t  -> negative passes the check
```

## Pitfalls

- Reading a guard's presence as protection without checking dominance.
- Missing a signed comparison that accepts a negative length.
- Accepting a check on a truncated copy of the value.

## Done when

- The guard's condition, variable and dominance are recorded.
- A guard that fails any of the three is reported as absent.

## References

- [CWE-1284 - improper validation of specified quantity](https://cwe.mitre.org/data/definitions/1284.html)
- [OWASP - input validation cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
