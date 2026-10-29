---
name: branch-pinning
description: "Store the branch and commit with every claim, because a verified claim with no revision is a claim about nothing in particular. Use when writing or re-verifying any claim"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [ledger, revision, scope]
---

# Branch Pinning

> Store the branch and commit with every claim, because a verified claim with no revision is a claim about nothing in particular

**Use when:** writing or re-verifying any claim

**Avoid when:** the tree has one commit and is never updated

## Procedure

1. Record the branch name and the head commit in the claim.
2. Record the same for each evidence file's capture.
3. Check that the sink file exists at that commit, not just on disk.
4. Re-verify on a different branch as a separate run.
5. Update the pin only after a passing re-verify.
6. Note when a fix exists on a branch other than the pinned one.

## Signals

- The claim names a branch that was deleted.
- Local uncommitted edits are part of the verified tree.
- The evidence was captured on a different commit than the claim.
- Two claims about one file name different commits.

## Patterns

**1. Pinned revision**

```text
release/2.3 @ 7c1e9ab  -> reproducible
```

**2. Dirty tree**

```text
uncommitted changes present  -> record the diff
```

**3. Per branch**

```text
one pin per branch verified
```

## Pitfalls

- Verifying a working tree with uncommitted edits and not saying so.
- Pinning a branch name without the commit, which moves under you.
- Updating the pin to make a failing claim pass.

## Done when

- Every claim carries a branch and commit, including dirty-tree state.
- Evidence captures are pinned to the same commit as the claim.

## References

- [Git - revisions](https://git-scm.com/docs/git-rev-parse)
- [Git - status](https://git-scm.com/docs/git-status)
