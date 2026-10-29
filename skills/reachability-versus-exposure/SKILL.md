---
name: reachability-versus-exposure
description: "Separate the two claims, because a verified path proves reachability and says nothing about who is allowed to start it. Use when the finding states both a call path and an attacker position"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [graph, exposure, severity]
---

# Reachability Versus Exposure

> Separate the two claims, because a verified path proves reachability and says nothing about who is allowed to start it

**Use when:** the finding states both a call path and an attacker position

**Avoid when:** the finding is a latent defect with no claimed exposure

## Procedure

1. Verify the call path independently of the exposure claim.
2. Identify the check that gates the entry: auth, role, network position.
3. Read that check and record how it decides.
4. State exposure as the weakest path that reaches the sink.
5. If two entries reach the sink, report the weaker one.
6. Grade severity from exposure, not from path length.

## Signals

- The path is pre-auth but the handler is behind a login decorator.
- One entry is admin-only and the other is public.
- A proxy authenticates before the application does.
- The auth check happens after the vulnerable parse.

## Patterns

**1. Path verified**

```text
4 hops, each edge checked  -> reachable
```

**2. Exposure checked**

```text
decorator requires a session  -> authenticated
```

**3. Order matters**

```text
auth after parse  -> the parse is pre-auth
```

## Pitfalls

- Treating a verified path as proof of pre-auth reach.
- Missing that authentication happens after the vulnerable code runs.
- Averaging two entries into one exposure claim.

## Done when

- Reachability and exposure are stated as two separate verified claims.
- The weakest entry that reaches the sink determines severity.

## References

- [OWASP - broken access control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- [FIRST - CVSS v3.1 specification](https://www.first.org/cvss/v3-1/specification-document)
