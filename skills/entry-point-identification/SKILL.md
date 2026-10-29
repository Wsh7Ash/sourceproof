---
name: entry-point-identification
description: "Name the actual request entry point, because reachability claimed from an internal helper proves nothing about who can call it. Use when the finding claims an attacker can reach a sink"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [ground, entry, reachability]
---

# Entry Point Identification

> Name the actual request entry point, because reachability claimed from an internal helper proves nothing about who can call it

**Use when:** the finding claims an attacker can reach a sink

**Avoid when:** the finding is a latent defect with no claimed reachability

## Procedure

1. Find where untrusted input enters: a route, a handler, a parser callback, a socket read.
2. Confirm that entry point is registered somewhere the tree shows.
3. Record its exposure: pre-auth, authenticated, local.
4. Check whether a proxy or gateway in front changes the exposure.
5. Start the call path at that entry, not at a convenient middle function.
6. If the entry cannot be found, mark reachability unproven.

## Signals

- The route table names a handler the claim never mentions.
- The handler is registered behind an authentication middleware.
- The entry is a CLI flag parser, not a request handler.
- Two entry points reach the same sink with different exposure.

## Patterns

**1. Route to handler**

```text
add_route('/upload', route_upload)  -> starts at route_upload
```

**2. Socket read**

```text
recv in read_message  -> starts at handle_request
```

**3. Registration**

```text
a callback stored in a table and invoked later  -> name the invoker
```

## Pitfalls

- Starting the path at the vulnerable function and calling that reachability.
- Assuming a route is unauthenticated without reading the middleware.
- Missing that the exported handler is wrapped by a decorator that sanitises input.

## Done when

- The entry point is named with its file and line and its exposure.
- Registration of that entry is evidenced from the tree.

## References

- [OWASP - attack surface analysis](https://owasp.org/www-community/Attack_Surface_Analysis_Cheat_Sheet)
- [CWE-20 - improper input validation](https://cwe.mitre.org/data/definitions/20.html)
