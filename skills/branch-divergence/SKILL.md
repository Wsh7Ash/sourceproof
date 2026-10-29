---
name: branch-divergence
description: "Verify against each deployed branch separately, because a finding that is fixed on main can still be live on the release branch. Use when the project maintains release branches or long-lived forks"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [locate, branches, scope]
---

# Branch Divergence

> Verify against each deployed branch separately, because a finding that is fixed on main can still be live on the release branch

**Use when:** the project maintains release branches or long-lived forks

**Avoid when:** a single branch is built and deployed

## Procedure

1. List the branches that are built and deployed.
2. Check out each one and re-run the snippet and path checks.
3. Record the result per branch, including the branch's head commit.
4. Report the weakest branch as the finding's scope.
5. Note which branch carries the fix, with its commit.
6. Re-check when a release is cut.

## Signals

- The fix exists on main and not on release/2.3.
- The release branch has an older parser with the same sink.
- A fork is deployed by a downstream package.
- The branches differ only in configuration.

## Patterns

**1. Per branch**

```text
main fixed, release/2.3 vulnerable  -> severity from the release
```

**2. Same everywhere**

```text
all three branches vulnerable  -> one claim, wide scope
```

**3. Config only**

```text
same code, different flag  -> build variant, not a branch claim
```

## Pitfalls

- Verifying on main and reporting the release as affected.
- Missing a downstream fork that ships the vulnerable code.
- Treating a cherry-pick as a fix on every branch.

## Done when

- Each deployed branch has a recorded verification result and head commit.
- The reported scope names the branch that is actually vulnerable.

## References

- [Git - branching](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell)
- [OWASP - vulnerability management](https://owasp.org/www-community/vulnerability_management)
