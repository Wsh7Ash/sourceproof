---
name: blocking-versus-advisory
description: "Decide which failures make a claim unverifiable, because a ledger where everything is advisory is a ledger nobody can act on. Use when defining or reviewing the rules a claim must pass"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [grade, rules, process]
---

# Blocking Versus Advisory

> Decide which failures make a claim unverifiable, because a ledger where everything is advisory is a ledger nobody can act on

**Use when:** defining or reviewing the rules a claim must pass

**Avoid when:** the claim is a note to self with no submission path

## Procedure

1. List every field the claim requires.
2. For each, ask whether the claim is still checkable without it.
3. Mark it blocking when the answer is no.
4. Mark it advisory when the claim survives but is weaker.
5. Apply the same rule to every claim in the ledger.
6. Revisit the split when a triager rejects a claim the rules passed.

## Signals

- A claim without a version is graded A.
- A missing negative control is only a penalty.
- Every rule is blocking, so every claim fails.
- A rule was demoted after it rejected a favourite finding.

## Patterns

**1. Blocking**

```text
no line, no path, or a broken hop  -> not verified
```

**2. Advisory**

```text
no reported_at, odd status  -> score penalty only
```

**3. Revision**

```text
a rejection becomes a new blocking rule
```

## Pitfalls

- Making everything blocking so nothing is ever verified.
- Making everything advisory so the rules mean nothing.
- Demoting a rule because one claim you liked failed it.

## Done when

- Each rule's severity is justified by whether the claim stays checkable.
- The rule table is versioned with the ledger.

## References

- [OWASP - vulnerability management](https://owasp.org/www-community/vulnerability_management)
- [NIST - SP 800-115 testing guide](https://csrc.nist.gov/pubs/sp/800/115/final)
