---
name: anchor-identity
description: "Derive identity from the sink and the path rather than the line, because a line number changes without the bug changing. Use when assigning ids or comparing claims across revisions"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [ledger, identity, dedupe]
---

# Anchor Identity

> Derive identity from the sink and the path rather than the line, because a line number changes without the bug changing

**Use when:** assigning ids or comparing claims across revisions

**Avoid when:** the claim is deleted immediately after filing

## Procedure

1. Choose the fields that identify the bug: file, function, kind, path.
2. Exclude the line number and the title.
3. Hash the chosen fields into a short anchor.
4. Use the anchor for dedupe and for cross-revision matching.
5. Keep the human id separate, since people quote it.
6. Recompute the anchor when any identifying field changes.

## Signals

- The same bug gets a new id after a formatter shifts every line.
- Two claims with different titles share an anchor.
- The anchor changes when only the description was edited.
- A duplicate slipped in because ids differed but anchors matched.

## Patterns

**1. Identity**

```text
file + function + kind + path  -> anchor
```

**2. Excluded**

```text
line, title, severity  -> not identity
```

**3. Recompute**

```text
the path changed  -> new anchor, note the old one
```

## Pitfalls

- Including the line number, so every refactor forks the identity.
- Using the title as identity, which invites duplicate wording.
- Changing the anchor silently when the path is corrected.

## Done when

- The anchor excludes line and title and is used for dedupe.
- Anchor changes are recorded with the reason.

## References

- [RFC 6234 - SHA algorithms](https://www.rfc-editor.org/rfc/rfc6234)
- [HackerOne - duplicate handling](https://docs.hackerone.com/en/articles/8475114-scope)
