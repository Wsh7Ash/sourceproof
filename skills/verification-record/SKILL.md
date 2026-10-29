---
name: verification-record
description: "Record what was checked and when, because a claim marked verified with no record is indistinguishable from a claim nobody looked at. Use when after running the checks on a claim"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [grade, record, process]
---

# Verification Record

> Record what was checked and when, because a claim marked verified with no record is indistinguishable from a claim nobody looked at

**Use when:** after running the checks on a claim

**Avoid when:** never; this is what makes the ledger auditable

## Procedure

1. Record the revision the checks ran against.
2. Record each check and its result: snippet, sink, hops, guard.
3. Record the tool version and the sink catalogue version.
4. Record the date and who ran it.
5. Store the record beside the claim, not inside a chat log.
6. Re-run and replace the record when the claim changes.

## Signals

- The claim says verified and no revision is recorded.
- The record predates the claim's last edit.
- Two claims verified on different days share one record.
- The tool version is missing, so the rules used are unknown.

## Patterns

**1. Per check**

```text
snippet: match, sink: match, hops: 4/4, guard: none
```

**2. Pinned revision**

```text
revision 7c1e9ab, catalogue v3, sourceproof 1.0.0
```

**3. Dated record**

```text
2026-10-29, verified against release/2.3
```

## Pitfalls

- Marking verified from memory without a recorded run.
- Keeping the record in a terminal scrollback that is already gone.
- Reusing an old record after the claim's line changed.

## Done when

- Each check has a recorded result with the revision and tool version.
- The record is newer than the claim's last edit.

## References

- [NIST - SP 800-115 testing guide](https://csrc.nist.gov/pubs/sp/800/115/final)
- [OWASP - vulnerability management](https://owasp.org/www-community/vulnerability_management)
