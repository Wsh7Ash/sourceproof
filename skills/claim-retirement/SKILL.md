---
name: claim-retirement
description: "Retire a claim with a reason and a commit, because a ledger that only grows hides which findings were fixed and which were wrong. Use when a claim is fixed, refuted, duplicated or superseded"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [ledger, retirement, process]
---

# Claim Retirement

> Retire a claim with a reason and a commit, because a ledger that only grows hides which findings were fixed and which were wrong

**Use when:** a claim is fixed, refuted, duplicated or superseded

**Avoid when:** the claim is still open and nothing changed

## Procedure

1. Choose the reason: fixed, rejected, duplicate, superseded.
2. Record the commit or the event that justifies it.
3. Keep the claim in the ledger rather than deleting it.
4. Keep its evidence hashes even if the evidence is removed.
5. Re-open rather than re-create if the code returns.
6. Report retirements alongside new claims.

## Signals

- A fixed claim disappears from the count without a record.
- A rejected claim is deleted and re-filed later as new.
- A duplicate is removed rather than merged.
- The ledger shrank and nobody knows why.

## Patterns

**1. Fixed by commit**

```text
commit 91ab2f adds the bounds check  -> retired
```

**2. Rejected**

```text
input is a constant  -> retired with the reason
```

**3. Superseded**

```text
SP-001 replaced by SP-009 with a longer path
```

## Pitfalls

- Deleting claims to keep the ledger tidy.
- Retiring without a commit, so nobody can check the fix.
- Re-filing a rejected claim as a new one to avoid the history.

## Done when

- Every retired claim has a reason and a reference.
- Retirements are reported next to new claims.

## References

- [OWASP - vulnerability management](https://owasp.org/www-community/vulnerability_management)
- [Git - revert](https://git-scm.com/docs/git-revert)
