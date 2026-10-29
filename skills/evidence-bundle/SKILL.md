---
name: evidence-bundle
description: "Attach the path output, the quoted line and the guard state as files, because a reviewer should not have to rebuild your checkout to check a claim. Use when a claim is verified and about to be handed to someone else"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [grade, evidence, bundle]
---

# Evidence Bundle

> Attach the path output, the quoted line and the guard state as files, because a reviewer should not have to rebuild your checkout to check a claim

**Use when:** a claim is verified and about to be handed to someone else

**Avoid when:** the claim is a personal note that will never leave your machine

## Procedure

1. Save the path output, including the call line for every hop.
2. Save the quoted sink line with its file and number.
3. Save the guard reading, or a note that there is none.
4. Hash each file and record the digest in the claim.
5. Check that every referenced file exists before handing over.
6. Keep the bundle with the revision it was captured from.

## Signals

- The claim cites a path that exists only in chat.
- The quoted line is pasted without a file or line.
- The bundle has no digest, so it cannot be checked for drift.
- Evidence files were captured from a different revision.

## Patterns

**1. Path capture**

```text
path-c.txt with four hops and call lines
```

**2. Snippet capture**

```text
workspace/src/parse.c:10: memcpy(...)
```

**3. Guard note**

```text
guard.txt: none between entry and sink
```

## Pitfalls

- Describing the path in prose and calling it evidence.
- Capturing evidence from a different checkout than the claim's revision.
- Shipping a bundle whose digests were computed before the last edit.

## Done when

- Every evidence reference resolves to a file with a recorded digest.
- The bundle names the revision it was captured from.

## References

- [NIST - SP 800-86 forensic techniques](https://csrc.nist.gov/pubs/sp/800/86/final)
- [RFC 8785 - JSON canonicalization](https://www.rfc-editor.org/rfc/rfc8785)
