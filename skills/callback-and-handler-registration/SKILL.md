---
name: callback-and-handler-registration
description: "Follow a handler from where it is registered to where it is invoked, because the call the attacker triggers is often made by a framework, not by your code. Use when the entry is a route, middleware, event listener or signal handler"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [graph, callback, framework]
---

# Callback and Handler Registration

> Follow a handler from where it is registered to where it is invoked, because the call the attacker triggers is often made by a framework, not by your code

**Use when:** the entry is a route, middleware, event listener or signal handler

**Avoid when:** the entry point calls the next function directly in its own body

## Procedure

1. Find where the handler is registered, with the registration line.
2. Find where the framework invokes that registration.
3. Check whether the invocation passes the raw request or a sanitised view.
4. Record the registration and the invoker as two separate pieces of evidence.
5. Start the call path at the handler, and note the framework edge separately.
6. State the framework version, since invocation differs between versions.

## Signals

- The handler is a bare function name in a table.
- Middleware wraps the handler and rewrites the argument.
- The same handler is registered for two routes with different auth.
- The framework resolves handlers by string name.

## Patterns

**1. Route table**

```text
{'/upload', route_upload}  -> invoked by the dispatcher
```

**2. Decorator**

```text
@app.route('/upload')  -> the framework owns the edge
```

**3. Event listener**

```text
on('upload', handler)  -> the emitter owns the edge
```

## Pitfalls

- Claiming the framework call as a direct edge from main.
- Missing middleware that validates or rewrites the input before the handler.
- Assuming a handler registered twice has the same exposure on both routes.

## Done when

- Registration and invocation are both evidenced, with lines.
- The framework edge is distinguished from direct calls in the path.

## References

- [OWASP - attack surface analysis](https://owasp.org/www-community/Attack_Surface_Analysis_Cheat_Sheet)
- [CWE-20 - improper input validation](https://cwe.mitre.org/data/definitions/20.html)
