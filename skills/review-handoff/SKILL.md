---
name: review-handoff
description: "Hand over the ledger, the tree revision and the tool version together, because a claim verified on a checkout the reviewer cannot reconstruct is unverifiable in practice. Use when another person or agent picks up the review"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [ledger, handoff, process]
---

# Review Handoff

> Hand over the ledger, the tree revision and the tool version together, because a claim verified on a checkout the reviewer cannot reconstruct is unverifiable in practice

**Use when:** another person or agent picks up the review

**Avoid when:** you are the only reader and will file immediately

## Procedure

1. Write the revision, branch and tool version on the handoff.
2. Include the command that re-verifies the whole ledger.
3. Include the sink catalogue version and any local additions.
4. Include the known limitations: unparsed files, vendored code.
5. Include the open questions per claim.
6. Verify the ledger once from a clean checkout before handing over.

## Signals

- The reviewer cannot reproduce a claim on their checkout.
- The handoff names a tool version that is not installed.
- The catalogue was customised and the change was not recorded.
- Half the claims depend on a branch the reviewer does not have.

## Patterns

**1. Re-verify command**

```text
sourceproof verify ledger.jsonl --root .  -> one command
```

**2. Pinned revision**

```text
branch, commit, tool version, catalogue version
```

**3. Limitations**

```text
two generated files unparsed  -> listed
```

## Pitfalls

- Handing over claims without the tree revision.
- Omitting local catalogue additions that change the hit list.
- Skipping the clean-checkout run and discovering a missing file later.

## Done when

- The handoff carries revision, tool version and the re-verify command.
- One clean-checkout verification was run and its result recorded.

## References

- [NIST - SP 800-115 testing guide](https://csrc.nist.gov/pubs/sp/800/115/final)
- [OWASP - code review guide](https://owasp.org/www-project-code-review-guide/)
