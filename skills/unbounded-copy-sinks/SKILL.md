---
name: unbounded-copy-sinks
description: "Read the length argument against the destination size, because memcpy is only a bug when the length can exceed what was allocated. Use when a memory or string copy appears on a path from untrusted input"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [sink, memory, copy]
---

# Unbounded Copy Sinks

> Read the length argument against the destination size, because memcpy is only a bug when the length can exceed what was allocated

**Use when:** a memory or string copy appears on a path from untrusted input

**Avoid when:** the length is a compile-time constant or was checked against the destination one line above

## Procedure

1. Find the length argument and trace where its value comes from.
2. Find the destination and its allocated size.
3. Check whether a comparison between the two exists on every path.
4. Check the comparison's types: a signed length can pass while still huge.
5. Check for an off-by-one on the terminator write.
6. Record the destination size and the maximum attacker length.

## Signals

- The length is parsed from the request with atoi or a strtoul result.
- The destination is a fixed stack buffer.
- The check compares against sizeof a pointer rather than the buffer.
- The copy is followed by a terminator write at index len.

## Patterns

**1. Unchecked**

```text
len = atoi(body); memcpy(field, body + 4, len)  -> overflow
```

**2. Checked length**

```text
if (len > sizeof field) return -1;  -> guarded
```

**3. Off by one**

```text
memcpy(dst, src, len); dst[len] = 0;  -> one byte past
```

## Pitfalls

- Reporting a copy whose length is a constant.
- Missing that the guard compares against the pointer size, not the array size.
- Ignoring the terminator write when the copy itself is exactly bounded.

## Done when

- The destination size and the maximum reachable length are both recorded.
- Any guard is quoted with its exact comparison and types.

## References

- [CWE-120 - buffer copy without size check](https://cwe.mitre.org/data/definitions/120.html)
- [CWE-787 - out-of-bounds write](https://cwe.mitre.org/data/definitions/787.html)
