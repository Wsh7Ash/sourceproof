"""sourceproof command line interface.

Corpus commands (validate / list / show / search / build) come from the pack
harness. The domain commands work the claim-verification angle:

    sourceproof scan tree/ --sinks
    sourceproof path handle_request memcpy --root tree/
    sourceproof locate claim.json --root tree/
    sourceproof check claim.json --root tree/
    sourceproof verify ledger.jsonl --root tree/
    sourceproof report claim.json --root tree/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .claims import (
    ClaimError,
    build_claim,
    grade,
    load_claim,
    load_ledger,
    locate,
    render_claim,
    scaffold,
    snippet_digest,
    verify_ledger,
)
from .corpus import BY_SLUG, PACK, SKILLS
from .render import build_pack, render_skill
from .sources import SINK_CATALOGUE, SINK_KINDS, Tree, index_tree, sink_kind
from .validate import (
    MAX_DESCRIPTION,
    MIN_DONE,
    MIN_PATTERNS,
    MIN_PITFALLS,
    MIN_SIGNALS,
    MIN_STEPS,
    MIN_SUMMARY,
    MIN_WORDS,
    Issue,
    validate_pack,
)

FLOORS = {
    "min_steps": MIN_STEPS,
    "min_signals": MIN_SIGNALS,
    "min_patterns": MIN_PATTERNS,
    "min_pitfalls": MIN_PITFALLS,
    "min_done_when": MIN_DONE,
    "min_summary_chars": MIN_SUMMARY,
    "min_words": MIN_WORDS,
    "max_description_chars": MAX_DESCRIPTION,
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _display_path(path: Path) -> str:
    """A path a reader can use: relative to the working directory when possible."""
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _report(issues: list[Issue], total: int, as_json: bool, title: str) -> int:
    bad = {issue.slug for issue in issues if issue.slug}
    valid = total - len(bad)
    if as_json:
        print(
            json.dumps(
                {
                    "pack": title,
                    "checked": total,
                    "valid": valid,
                    "passed": not issues,
                    "floors": FLOORS,
                    "issues": [
                        {"slug": issue.slug, "rule": issue.rule, "message": issue.message}
                        for issue in issues
                    ],
                },
                indent=2,
            )
        )
    else:
        print(f"{title}: {valid}/{total} skills valid")
        for issue in issues:
            print(f"  FAIL {issue}")
        if not issues:
            print(
                f"  ok  steps>={MIN_STEPS} signals>={MIN_SIGNALS} patterns>={MIN_PATTERNS} "
                f"pitfalls>={MIN_PITFALLS} words>={MIN_WORDS} refs canonical https"
            )
    return 0 if not issues else 1


def cmd_validate(args: argparse.Namespace) -> int:
    return _report(validate_pack(PACK, SKILLS), len(SKILLS), args.json, PACK["name"])


def cmd_list(args: argparse.Namespace) -> int:
    rows = [
        skill
        for skill in SKILLS
        if (not args.tag or args.tag in skill.tags)
        and (not args.phase or skill.meta_get("phase") == args.phase)
    ]
    if args.json:
        print(
            json.dumps(
                [
                    {
                        "slug": s.slug,
                        "title": s.title,
                        "phase": s.meta_get("phase"),
                        "tags": list(s.tags),
                    }
                    for s in rows
                ],
                indent=2,
            )
        )
        return 0
    for skill in rows:
        print(f"{skill.meta_get('phase'):12s} {skill.slug:40s} {skill.title}")
    print(f"# {len(rows)} skill(s)")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    skill = BY_SLUG.get(args.slug)
    if skill is None:
        print(f"unknown skill: {args.slug}", file=sys.stderr)
        return 2
    text = render_skill(PACK, skill)
    print(text if args.raw else text.split("---\n", 2)[-1].lstrip())
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    terms = [term.lower() for term in args.terms]

    def score(skill) -> int:
        blob = " ".join([skill.slug, skill.title, skill.summary, *skill.tags, *skill.steps]).lower()
        return sum(blob.count(term) for term in terms)

    ranked = sorted(
        ((score(skill), skill) for skill in SKILLS if score(skill)),
        key=lambda pair: (-pair[0], pair[1].slug),
    )[: args.limit]
    if not ranked:
        print("no matches", file=sys.stderr)
        return 1
    for points, skill in ranked:
        print(f"{points:3d}  {skill.slug:40s} {skill.title}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else repo_root()
    written = build_pack(root, PACK, SKILLS)
    print(f"wrote {len(written)} file(s) under {root}")
    return 0


def _load_tree(root: str | None, fallback: str = ".") -> Tree:
    return index_tree(Path(root or fallback))


def cmd_scan(args: argparse.Namespace) -> int:
    try:
        tree = _load_tree(args.root)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.sinks:
        rows = tree.sinks
        if args.kind:
            rows = tuple(sink for sink in rows if sink.kind == args.kind)
        if args.json:
            print(json.dumps([sink.as_dict() for sink in rows], indent=2))
            return 0
        for sink in rows:
            print(
                f"{sink.kind:16s} {sink.file}:{sink.line:<5d} "
                f"{sink.function:24s} in {sink.enclosing or '?'}"
            )
        print(f"# {len(rows)} sink(s) in {len(tree.files)} file(s)")
        return 0

    if args.json:
        payload = [
            definition.as_dict()
            for definition in tree.definitions
            if not args.function or definition.name == args.function
        ]
        print(json.dumps({"tree": tree.as_dict(), "definitions": payload}, indent=2))
        return 0

    for definition in tree.definitions:
        if args.function and definition.name != args.function:
            continue
        print(f"{definition.file}:{definition.start}-{definition.end}  {definition.name}")
    print(
        f"# {len(tree.definitions)} definition(s) in {len(tree.files)} file(s), "
        f"{len(tree.sinks)} sink(s), {len(tree.unresolved)} unresolved call name(s)"
    )
    return 0


def cmd_path(args: argparse.Namespace) -> int:
    try:
        tree = _load_tree(args.root)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not tree.exists(args.entry):
        print(f"entry not defined in the tree: {args.entry}", file=sys.stderr)
        return 2
    # The sink does not need a definition of its own: memcpy and cursor.execute
    # live outside the tree. Anything else must at least be a catalogue name.
    if not tree.exists(args.sink) and not sink_kind(args.sink):
        print(
            f"sink is neither defined in the tree nor in the catalogue: {args.sink}",
            file=sys.stderr,
        )
        return 2

    trail = tree.path(args.entry, args.sink, args.max_depth)
    if trail is None:
        if args.json:
            print(json.dumps({"entry": args.entry, "sink": args.sink, "path": None}, indent=2))
        else:
            print(f"no call path from {args.entry} to {args.sink}", file=sys.stderr)
        return 1

    if args.json:
        hops = [
            {
                "function": definition.name,
                "file": definition.file,
                "start": definition.start,
                "called_at": line or None,
            }
            for definition, line in trail
        ]
        print(json.dumps({"entry": args.entry, "sink": args.sink, "path": hops}, indent=2))
        return 0

    for index, (definition, line) in enumerate(trail):
        marker = "->" if index else "  "
        called = f" (calls on line {line})" if line else ""
        print(f"{marker} {definition.name}  {definition.file}:{definition.start}{called}")
    print(f"# {len(trail)} hop(s), verified against the tree")
    return 0


def cmd_locate(args: argparse.Namespace) -> int:
    try:
        claim = load_claim(Path(args.claim))
    except ClaimError as exc:
        print(f"cannot read claim: {exc}", file=sys.stderr)
        return 2
    digest = str((claim.get("sink") or {}).get("snippet_sha256") or "").lower()
    if not digest:
        print("claim has no sink.snippet_sha256", file=sys.stderr)
        return 2
    try:
        tree = _load_tree(args.root, str(claim.get("root") or "."))
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    hits = locate(tree, digest)
    if args.json:
        print(json.dumps({"digest": digest, "hits": [{"file": f, "line": n} for f, n in hits]}, indent=2))
        return 0 if hits else 1
    for rel, number in hits:
        print(f"{rel}:{number}")
    print(f"# {len(hits)} match(es) for the quoted line", file=sys.stderr)
    return 0 if hits else 1


def cmd_check(args: argparse.Namespace) -> int:
    try:
        claim = load_claim(Path(args.claim))
    except ClaimError as exc:
        print(f"cannot read claim: {exc}", file=sys.stderr)
        return 2
    root = Path(args.root or claim.get("root") or ".")
    try:
        tree = index_tree(root)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    report = grade(claim, root, tree)
    if args.json:
        print(json.dumps(report.as_dict(), indent=2))
    else:
        verdict = "verified" if report.submittable else "NOT verified"
        print(f"{report.claim_id}: grade {report.grade} ({report.score}/100) {verdict}")
        print(f"  anchor {report.anchor}")
        for finding in report.findings:
            print(f"  {finding.severity:8s} {finding.rule}: {finding.message}")
            if finding.hint and args.verbose:
                print(f"           -> {finding.hint}")
    return 0 if report.submittable else 1


def cmd_verify(args: argparse.Namespace) -> int:
    try:
        claims = load_ledger(Path(args.ledger))
    except ClaimError as exc:
        print(f"cannot read ledger: {exc}", file=sys.stderr)
        return 2
    if not claims:
        print("ledger contains no claims", file=sys.stderr)
        return 2

    root = Path(args.root) if args.root else Path(".")
    try:
        tree = index_tree(root)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    graded = verify_ledger(claims, tree)
    if args.json:
        print(
            json.dumps(
                {
                    "root": str(tree.root),
                    "claims": [report.as_dict() for _, report in graded],
                    "submittable": sum(1 for _, report in graded if report.submittable),
                    "failed": [report.claim_id for _, report in graded if not report.submittable],
                },
                indent=2,
            )
        )
    else:
        for claim, report in graded:
            status = "ok  " if report.submittable else "FAIL"
            title = str(claim.get("title") or "")
            print(f"{status} {report.claim_id:12s} {report.grade} {report.score:3d}  {title}")
            if args.verbose:
                for finding in report.findings:
                    print(f"       {finding.severity:8s} {finding.rule}: {finding.message}")
        ok = sum(1 for _, report in graded if report.submittable)
        print(f"# {ok}/{len(graded)} claim(s) verified against {_display_path(tree.root)}")

    return 0 if all(report.submittable for _, report in graded) else 1


def cmd_report(args: argparse.Namespace) -> int:
    try:
        claim = load_claim(Path(args.claim))
    except ClaimError as exc:
        print(f"cannot read claim: {exc}", file=sys.stderr)
        return 2
    root = Path(args.root or claim.get("root") or ".")
    try:
        tree = index_tree(root)
    except FileNotFoundError:
        tree = None
    report = grade(claim, root, tree)
    text = render_claim(claim, report)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {args.out}")
    else:
        print(text, end="")
    return 0 if report.submittable else 1


def cmd_scaffold(args: argparse.Namespace) -> int:
    claim = scaffold(args.title, args.id)
    text = json.dumps(claim, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {args.out}")
    else:
        print(text, end="")
    return 0


def cmd_sinks(args: argparse.Namespace) -> int:
    if args.json:
        print(
            json.dumps(
                [{"kind": kind, "functions": list(functions)} for kind, functions in SINK_CATALOGUE],
                indent=2,
            )
        )
        return 0
    for kind, functions in SINK_CATALOGUE:
        print(f"{kind:18s} {' '.join(functions)}")
    print(f"# {len(SINK_KINDS)} kind(s), {sum(len(f) for _, f in SINK_CATALOGUE)} function(s)")
    return 0


def cmd_anchor(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.is_file():
        print(f"file not found: {path}", file=sys.stderr)
        return 2
    try:
        line = path.read_text(encoding="utf-8", errors="replace").splitlines()[args.line - 1]
    except IndexError:
        print(f"{path} has fewer than {args.line} lines", file=sys.stderr)
        return 2
    print(f"line     {line.strip()}")
    print(f"digest   {snippet_digest(line)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=PACK["name"], description=PACK["description"])
    parser.add_argument("--version", action="version", version=f"{PACK['name']} {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="run every corpus rule")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("list", help="list skills")
    p.add_argument("--tag", default=None)
    p.add_argument("--phase", default=None)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("show", help="print one SKILL.md")
    p.add_argument("slug")
    p.add_argument("--raw", action="store_true")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("search", help="rank skills by keyword")
    p.add_argument("terms", nargs="+")
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("build", help="regenerate skills/, pack.json and results/")
    p.add_argument("--root", default=None)
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("scan", help="index a tree and list definitions or sinks")
    p.add_argument("root", nargs="?", default=".")
    p.add_argument("--sinks", action="store_true")
    p.add_argument("--kind", default=None)
    p.add_argument("--function", default=None)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("path", help="verify a call path from an entry to a sink")
    p.add_argument("entry")
    p.add_argument("sink")
    p.add_argument("--root", default=".")
    p.add_argument("--max-depth", type=int, default=12)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_path)

    p = sub.add_parser("locate", help="find the quoted line anywhere in the tree")
    p.add_argument("claim")
    p.add_argument("--root", default=None)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_locate)

    p = sub.add_parser("check", help="grade one claim against the tree")
    p.add_argument("claim")
    p.add_argument("--root", default=None)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("verify", help="grade every claim in a ledger")
    p.add_argument("ledger")
    p.add_argument("--root", default=None)
    p.add_argument("--json", action="store_true")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("report", help="render a claim as markdown")
    p.add_argument("claim")
    p.add_argument("--root", default=None)
    p.add_argument("--out", default=None)
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("scaffold", help="emit an empty claim")
    p.add_argument("title")
    p.add_argument("--id", default="SP-000")
    p.add_argument("--out", default=None)
    p.set_defaults(func=cmd_scaffold)

    p = sub.add_parser("sinks", help="print the sink catalogue")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_sinks)

    p = sub.add_parser("anchor", help="print the snippet digest for a file:line")
    p.add_argument("file")
    p.add_argument("line", type=int)
    p.set_defaults(func=cmd_anchor)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
