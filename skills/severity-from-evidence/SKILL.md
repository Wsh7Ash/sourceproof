---
name: severity-from-evidence
description: "Derive the severity from the verified reachability and primitive, because a critical label on a locally reachable read is the fastest way to lose credibility. Use when assigning severity to a verified claim"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [grade, severity, evidence]
---

# Severity From Evidence

> Derive the severity from the verified reachability and primitive, because a critical label on a locally reachable read is the fastest way to lose credibility

**Use when:** assigning severity to a verified claim

**Avoid when:** the program pays a flat rate and ignores severity

## Procedure

1. Take exposure from the entry point, not from the intent.
2. Take the primitive from the sink and its arguments.
3. Take the prerequisites from the verified path and its guards.
4. Map those three to a severity, and record the mapping.
5. Compare with an existing claim of the same shape.
6. Re-derive after any of the three changes.

## Signals

- The severity was chosen before the path was verified.
- Two claims with identical fields have different severities.
- The score assumes pre-auth and the entry is behind a login.
- The severity ignores a compensating control the code shows.

## Patterns

**1. Derived severity**

```text
pre-auth + out-of-bounds write + deterministic  -> high
```

**2. Consistent**

```text
same field vector, same severity  -> reproducible
```

**3. Adjusted**

```text
manual downgrade because a guard reduces the primitive
```

## Pitfalls

- Choosing the label first and writing the path to fit.
- Letting a CVSS vector override the verified evidence.
- Ignoring a guard the path already records.

## Done when

- Severity is derived from exposure, primitive and prerequisites.
- Any manual adjustment carries a written reason.

## References

- [FIRST - CVSS v3.1 specification](https://www.first.org/cvss/v3-1/specification-document)
- [OWASP - risk rating methodology](https://owasp.org/www-community/OWASP_Risk_Rating_Methodology)
