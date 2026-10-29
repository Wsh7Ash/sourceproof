---
name: unsupported-language-honesty
description: "Say when the tree cannot be parsed for a language, because a verification tool that silently skips a file reports confidence it does not have. Use when the reviewed tree contains generated, templated or exotic source files"
pack: sourceproof
version: 1.0.0
category: source-review
tags: [ground, limits, process]
---

# Unsupported Language Honesty

> Say when the tree cannot be parsed for a language, because a verification tool that silently skips a file reports confidence it does not have

**Use when:** the reviewed tree contains generated, templated or exotic source files

**Avoid when:** every file in the tree is in a supported language and parses

## Procedure

1. List the file types present in the tree.
2. List the types the indexer can parse.
3. Count the files that fall outside that list.
4. Mark any claim whose sink or hop lives in an unparsed file.
5. Record the limitation in the claim rather than leaving the field blank.
6. Prefer reading the file by hand and attaching the snippet as evidence.

## Signals

- The sink is in a template that generates C at build time.
- The tree contains vendored code the indexer skips.
- A hop is defined in a file with an unrecognised extension.
- The claim verifies but the file it names was never parsed.

## Patterns

**1. Parsed languages**

```text
.c .h .py .js .go .rs  -> indexer covers them
```

**2. Unparsed**

```text
.tpl .m4 .proto  -> mark the claim, attach a snippet
```

**3. Vendored**

```text
third_party skipped by design  -> state it
```

## Pitfalls

- Reading an empty call graph as proof of unreachability.
- Assuming a generated file is not in the shipped binary.
- Letting the tool's silence stand in for verification.

## Done when

- Every unparsed file touching the claim is listed with its suffix.
- The claim either excludes such files or records the gap explicitly.

## References

- [CWE-1059 - insufficient examination](https://cwe.mitre.org/data/definitions/1059.html)
- [OWASP - code review guide](https://owasp.org/www-project-code-review-guide/)
