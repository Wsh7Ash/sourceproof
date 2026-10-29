---
name: reverification-cadence
description: "Re-verify on a schedule tied to code change, because a ledger verified once decays into a list of historical statements. Use when a ledger is kept across weeks or releases"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [ledger, cadence, process]
---

# Reverification Cadence

> Re-verify on a schedule tied to code change, because a ledger verified once decays into a list of historical statements

**Use when:** a ledger is kept across weeks or releases

**Avoid when:** the engagement ends with the submission

## Procedure

1. Trigger a re-verify on every merge to the reviewed branch.
2. Trigger one before every submission and every retest.
3. Trigger one when the sink catalogue changes.
4. Record the revision and date of each run.
5. Compare results and report claims that changed state.
6. Retire claims whose code is gone, with the commit.

## Signals

- The ledger's last verification predates several merges.
- A claim verified against a branch that no longer exists.
- The tool version changed since the last run.
- A retest cites evidence from an older revision.

## Patterns

**1. On merge**

```text
one run per merge to release/2.3
```

**2. Before submission**

```text
re-verify, then file
```

**3. On catalogue change**

```text
new sinks  -> re-scan, diff the hits
```

## Pitfalls

- Verifying once at the start of the engagement and never again.
- Skipping the re-verify because the claim is already filed.
- Re-running but not comparing against the previous result.

## Done when

- The cadence is written down and each run records its revision.
- State changes between runs are reported, not just the current state.

## References

- [OWASP - vulnerability management](https://owasp.org/www-community/vulnerability_management)
- [NIST - SP 800-115 testing guide](https://csrc.nist.gov/pubs/sp/800/115/final)
