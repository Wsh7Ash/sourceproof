"""Claim rules: is this source-level finding actually true of the tree?

A finding written in prose is a claim about code the reviewer may not have open.
This module checks the five parts that make the claim checkable:

1. the file exists and the line exists
2. the bytes on that line are the bytes the claim quoted
3. a catalogued sink is called on that line, with the claimed kind
4. the enclosing function is the last hop of the claimed call path
5. every consecutive pair in that path is a real call edge in the tree

Rules 1-3 are cheap. Rules 4-5 are the ones that turn "reachable from
``handle_request``" from an assertion into something the tree either supports or
refutes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .sources import (
    SINK_KINDS,
    Tree,
    index_tree,
    language_of,
    sink_kind,
)

SCHEMA = "sourceproof/v1"
EXPOSURES = ("pre-auth", "authenticated", "local", "unknown")
SEVERITIES = ("low", "medium", "high", "critical")
STATUSES = ("verified", "needs-review", "rejected", "duplicate")

BLOCKING = "blocking"
MAJOR = "major"
MINOR = "minor"
PENALTY = {BLOCKING: 25, MAJOR: 10, MINOR: 3}

EVIDENCE_KINDS = ("path", "snippet", "callers", "guard", "request", "log", "other")


class ClaimError(RuntimeError):
    """Raised when a claim or ledger cannot be read."""


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    message: str
    hint: str = ""

    def as_dict(self) -> dict[str, str]:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "message": self.message,
            "hint": self.hint,
        }


@dataclass
class Report:
    claim_id: str
    score: int
    grade: str
    anchor: str = ""
    findings: list[Finding] = field(default_factory=list)

    @property
    def blocking(self) -> list[Finding]:
        return [finding for finding in self.findings if finding.severity == BLOCKING]

    @property
    def submittable(self) -> bool:
        return not self.blocking

    def as_dict(self) -> dict[str, Any]:
        return {
            "claim": self.claim_id,
            "anchor": self.anchor,
            "score": self.score,
            "grade": self.grade,
            "submittable": self.submittable,
            "counts": {
                severity: len([f for f in self.findings if f.severity == severity])
                for severity in PENALTY
            },
            "findings": [finding.as_dict() for finding in self.findings],
        }


def normalise_line(text: str) -> str:
    """The form that gets hashed: leading and trailing whitespace removed."""
    return text.strip()


def snippet_digest(text: str) -> str:
    return hashlib.sha256(normalise_line(text).encode("utf-8")).hexdigest()


def anchor_of(claim: dict[str, Any]) -> str:
    """A stable identity for a claim: where it is and what it is about.

    Deliberately line-free, so a claim that survives a refactor keeps its
    identity and a duplicate cannot hide behind a moved line number.
    """
    sink = _block(claim, "sink")
    parts = [
        _text(sink.get("file")),
        _text(sink.get("function")),
        _text(sink.get("kind")),
        "/".join(_path(claim)),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _block(record: dict[str, Any], key: str) -> dict[str, Any]:
    value = record.get(key)
    return value if isinstance(value, dict) else {}


def _items(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _path(claim: dict[str, Any]) -> list[str]:
    return [item.strip() for item in _items(claim.get("path")) if isinstance(item, str) and item.strip()]


def _resolve(path_text: str, root: Path | None) -> Path:
    path = Path(path_text)
    if root is not None and not path.is_absolute():
        path = root / path
    return path


def load_claim(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ClaimError(f"claim not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ClaimError(f"claim is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ClaimError("claim must be a JSON object")
    return data


def load_ledger(path: Path) -> list[dict[str, Any]]:
    """Read a ledger: newline-delimited claims, or ``{"claims": [...]}``."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ClaimError(f"ledger not found: {path}") from exc

    stripped = text.lstrip()
    if stripped.startswith("{"):
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = None
        if isinstance(data, dict) and isinstance(data.get("claims"), list):
            return [claim for claim in data["claims"] if isinstance(claim, dict)]

    claims: list[dict[str, Any]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            claim = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ClaimError(f"ledger line {number} is not valid JSON: {exc}") from exc
        if not isinstance(claim, dict):
            raise ClaimError(f"ledger line {number} is not a JSON object")
        claims.append(claim)
    return claims


def locate(tree: Tree, digest: str) -> list[tuple[str, int]]:
    """Every ``file:line`` whose normalised text hashes to ``digest``."""
    hits: list[tuple[str, int]] = []
    for rel in tree.files:
        path = tree.root / rel
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for number, line in enumerate(lines, start=1):
            if snippet_digest(line) == digest:
                hits.append((rel, number))
    return hits


def grade(claim: dict[str, Any], root: Path | None = None, tree: Tree | None = None) -> Report:
    """Grade one claim against the tree. Blocking findings mean: not verified."""
    findings: list[Finding] = []

    def add(rule: str, severity: str, message: str, hint: str = "") -> None:
        findings.append(Finding(rule, severity, message, hint))

    if _text(claim.get("schema")) != SCHEMA:
        add("schema", BLOCKING, f"claim schema must be {SCHEMA!r}")

    claim_id = _text(claim.get("id")) or "unnamed"
    if not _text(claim.get("id")):
        add("id", MAJOR, "claim has no stable id")

    sink = _block(claim, "sink")
    sink_file = _text(sink.get("file"))
    sink_line_raw = sink.get("line")
    sink_function = _text(sink.get("function"))
    sink_claimed_kind = _text(sink.get("kind"))

    if not sink_file:
        add("sink-file", BLOCKING, "sink.file is missing, so there is nothing to verify")
    if not sink_function:
        add("sink-function", BLOCKING, "sink.function is missing")

    line = sink_line_raw if isinstance(sink_line_raw, int) else 0
    if line <= 0:
        add(
            "sink-line",
            BLOCKING,
            "sink.line must be a positive integer",
            "A finding without a line cannot be re-anchored after a refactor.",
        )

    if not sink_claimed_kind:
        add("sink-kind", MAJOR, "sink.kind is missing, so the sink is uncatalogued")
    elif sink_claimed_kind not in SINK_KINDS:
        add("sink-kind-unknown", MAJOR, f"sink.kind {sink_claimed_kind!r} is not in the catalogue")
    elif sink_function:
        expected = sink_kind(sink_function)
        if expected and expected != sink_claimed_kind:
            add(
                "sink-kind-mismatch",
                BLOCKING,
                f"{sink_function} is catalogued as {expected!r}, not {sink_claimed_kind!r}",
            )

    lines: list[str] = []
    if root is not None and sink_file:
        path = _resolve(sink_file, root)
        if not path.is_file():
            add("sink-file-missing", BLOCKING, f"sink file does not exist: {sink_file}")
        else:
            if not language_of(sink_file):
                add(
                    "unsupported-language",
                    MAJOR,
                    f"{sink_file} has no supported parser, so the path cannot be verified",
                )
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            if line > 0 and line > len(lines):
                add(
                    "sink-line-range",
                    BLOCKING,
                    f"line {line} is past the end of {sink_file} ({len(lines)} lines)",
                )

    if lines and 0 < line <= len(lines):
        actual = lines[line - 1]
        declared_digest = _text(sink.get("snippet_sha256"))
        if not declared_digest:
            add(
                "snippet",
                BLOCKING,
                "sink.snippet_sha256 is missing",
                f"The quoted line hashes to {snippet_digest(actual)}; record that value.",
            )
        elif snippet_digest(actual) != declared_digest.lower():
            hint = ""
            if tree is not None:
                moved = [(rel, number) for rel, number in locate(tree, declared_digest.lower()) if rel != sink_file or number != line]
                if moved:
                    rel, number = moved[0]
                    hint = f"The quoted line is now at {rel}:{number}; run locate to re-anchor."
                else:
                    hint = "The quoted line is not anywhere in the tree: recapture the snippet."
            add(
                "snippet-mismatch",
                BLOCKING,
                f"the line at {sink_file}:{line} is not the line the claim quoted",
                hint,
            )

        if sink_function and not _line_calls(actual, sink_function):
            add(
                "sink-absent",
                BLOCKING,
                f"{sink_file}:{line} does not call {sink_function}",
                "The sink moved, or the finding points at a comment or a wrapper.",
            )

    path = _path(claim)
    entry = _block(claim, "entry")
    entry_function = _text(entry.get("function"))

    if not path:
        add(
            "path",
            BLOCKING,
            "claim has no call path",
            "Reachability is the claim; record the hop list from entry to sink.",
        )
    elif len(path) < 2 and entry_function != path[0]:
        add("path-length", MAJOR, "a path of one hop cannot show reachability")

    if not entry_function:
        add("entry", BLOCKING, "entry.function is missing")
    elif path and entry_function != path[0]:
        add(
            "entry-mismatch",
            BLOCKING,
            f"entry.function {entry_function!r} is not the first hop {path[0]!r}",
        )

    exposure = _text(entry.get("exposure")).lower()
    if exposure not in EXPOSURES:
        add("exposure", MAJOR, f"entry.exposure must be one of {EXPOSURES}")

    if not _text(claim.get("impact")):
        add("impact", BLOCKING, "impact is missing, so the finding has no stated effect")

    severity = _text(claim.get("severity")).lower()
    if severity not in SEVERITIES:
        add("severity", MINOR, f"severity must be one of {SEVERITIES}")

    status = _text(claim.get("status")).lower()
    if status not in STATUSES:
        add("status", MINOR, f"status must be one of {STATUSES}")

    # ------------------------------------------------- reachability, verified
    if tree is not None and path:
        verified = True
        for name in path:
            if not tree.exists(name):
                add(
                    "unknown-hop",
                    BLOCKING,
                    f"no definition of {name!r} in the tree",
                    "A hop the tree cannot find is a hop the reviewer cannot check.",
                )
                verified = False
        if verified:
            for caller, callee in zip(path, path[1:]):
                if not _edge(tree, caller, callee):
                    actual = sorted({d.name for d in tree.named(caller) for d in tree.callees(d)})
                    add(
                        "broken-hop",
                        BLOCKING,
                        f"{caller!r} does not call {callee!r}",
                        "Callees found in the tree: " + (", ".join(actual) if actual else "none"),
                    )
            # the sink must sit inside the last hop, not merely after it
            if 0 < line <= len(lines) and sink_file:
                owner = tree.enclosing(sink_file, line)
                if owner is not None and owner.name != path[-1]:
                    add(
                        "sink-owner",
                        BLOCKING,
                        f"{sink_file}:{line} is inside {owner.name!r}, not {path[-1]!r}",
                    )

    # --------------------------------------------------------------- evidence
    evidence = [item for item in _items(claim.get("evidence")) if isinstance(item, dict)]
    if not evidence:
        add(
            "evidence",
            BLOCKING,
            "no evidence entries",
            "Attach the call-path output and the quoted snippet as files.",
        )
    for number, item in enumerate(evidence, start=1):
        ref = _text(item.get("ref"))
        kind = _text(item.get("kind"))
        if not ref:
            add("evidence-ref", BLOCKING, f"evidence {number} has no ref")
            continue
        if kind not in EVIDENCE_KINDS:
            add("evidence-kind", MINOR, f"evidence {number} kind {kind!r} is not recognised")
        digest = _text(item.get("sha256")).lower()
        if digest and (len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest)):
            add("evidence-digest", MAJOR, f"evidence {number} sha256 is not 64 hex characters")
        if root is not None:
            resolved = _resolve(ref, root)
            if not resolved.is_file():
                add("evidence-missing", BLOCKING, f"evidence file is missing: {ref}")
            elif digest and _sha256_file(resolved) != digest:
                add("evidence-drift", BLOCKING, f"evidence changed since it was hashed: {ref}")

    if not _text(claim.get("reported_at")):
        add("reported-at", MINOR, "reported_at is missing")

    report = Report(claim_id, 0, "", anchor_of(claim), findings)
    return finalise(report)


def finalise(report: Report) -> Report:
    """Recompute score and grade from the findings.

    Called after grading and again after ledger-level checks add findings, so a
    duplicate id cannot leave a claim showing grade A.
    """
    penalty = sum(PENALTY[finding.severity] for finding in report.findings)
    report.score = max(0, 100 - penalty)
    if any(finding.severity == BLOCKING for finding in report.findings):
        report.grade = "D"
    elif report.score >= 90:
        report.grade = "A"
    elif report.score >= 75:
        report.grade = "B"
    elif report.score >= 55:
        report.grade = "C"
    else:
        report.grade = "D"
    return report


def _line_calls(text: str, function: str) -> bool:
    import re

    return re.search(r"\b" + re.escape(function) + r"\s*\(", text) is not None


def _edge(tree: Tree, caller: str, callee: str) -> bool:
    return any(d.calls_name(callee) for d in tree.named(caller))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(64 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_ledger(claims: Iterable[dict[str, Any]], tree: Tree) -> list[tuple[dict[str, Any], Report]]:
    """Grade every claim, then flag duplicates and conflicting anchors."""
    graded = [(claim, grade(claim, tree.root, tree)) for claim in claims]

    seen_ids: dict[str, int] = {}
    seen_anchors: dict[str, str] = {}
    for claim, report in graded:
        claim_id = _text(claim.get("id"))
        anchor = report.anchor
        if claim_id:
            seen_ids[claim_id] = seen_ids.get(claim_id, 0) + 1
            if seen_ids[claim_id] > 1:
                report.findings.append(
                    Finding("ledger-duplicate-id", BLOCKING, f"claim id {claim_id!r} appears more than once")
                )
        if anchor in seen_anchors and seen_anchors[anchor] != claim_id:
            report.findings.append(
                Finding(
                    "ledger-duplicate-claim",
                    BLOCKING,
                    f"same sink, function and path as {seen_anchors[anchor]!r}",
                )
            )
        else:
            seen_anchors[anchor] = claim_id
        finalise(report)

    return graded


def render_claim(claim: dict[str, Any], report: Report) -> str:
    sink = _block(claim, "sink")
    entry = _block(claim, "entry")
    path = _path(claim)
    lines = [
        f"# {_text(claim.get('title')) or report.claim_id}",
        "",
        f"**Claim:** `{report.claim_id}`  ",
        f"**Anchor:** `{report.anchor}`  ",
        f"**Severity:** {_text(claim.get('severity'))}  ",
        f"**Status:** {_text(claim.get('status'))}",
        "",
        "## Sink",
        "",
        f"- `{_text(sink.get('file'))}:{sink.get('line')}` — `{_text(sink.get('text'))}`",
        f"- Function: `{_text(sink.get('function'))}` ({_text(sink.get('kind'))})",
        "",
        "## Path",
        "",
    ]
    for index, hop in enumerate(path):
        prefix = "entry" if index == 0 else ("sink" if index == len(path) - 1 else "hop")
        lines.append(f"{index + 1}. `{hop}` ({prefix})")
    lines += [
        "",
        f"Exposure: {_text(entry.get('exposure'))}",
        "",
        "## Impact",
        "",
        _text(claim.get("impact")) or "(none)",
        "",
        "## Evidence",
        "",
    ]
    for item in _items(claim.get("evidence")):
        if isinstance(item, dict):
            lines.append(f"- `{_text(item.get('kind'))}` {_text(item.get('ref'))}")
    lines += [
        "",
        "## Verification",
        "",
        f"- Grade: **{report.grade}** ({report.score}/100), submittable: "
        f"{'yes' if report.submittable else 'no'}",
    ]
    for finding in report.findings:
        lines.append(f"- `{finding.severity}` {finding.rule}: {finding.message}")
    lines.append("")
    return "\n".join(lines)


def scaffold(title: str, claim_id: str = "SP-000") -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "id": claim_id,
        "title": title,
        "reported_at": "",
        "status": "verified",
        "sink": {"kind": "", "function": "", "file": "", "line": 0, "snippet_sha256": "", "text": ""},
        "entry": {"function": "", "exposure": "unknown"},
        "path": [],
        "impact": "",
        "severity": "medium",
        "evidence": [],
    }


def build_claim(
    claim_id: str,
    title: str,
    tree: Tree,
    sink_file: str,
    sink_line: int,
    path: list[str],
    exposure: str,
    impact: str,
    severity: str,
    evidence_root: Path | None = None,
) -> dict[str, Any]:
    """Assemble a claim whose snippet digest is taken from the tree itself.

    Used by the example builder and by tests: a claim should never be authored
    with a hand-typed digest, because a wrong digest is exactly the failure this
    tool exists to catch.
    """
    lines = (tree.root / sink_file).read_text(encoding="utf-8", errors="replace").splitlines()
    text = lines[sink_line - 1]
    function = ""
    import re

    match = re.search(r"\b([A-Za-z_]\w*)\s*\(", text)
    if match:
        function = match.group(1)

    evidence: list[dict[str, Any]] = []
    if evidence_root is not None:
        for item in sorted(evidence_root.rglob("*")):
            if item.is_file():
                try:
                    rel = item.resolve().relative_to(tree.root).as_posix()
                except ValueError as exc:
                    raise ClaimError(f"evidence {item} is outside the indexed tree") from exc
                evidence.append(
                    {
                        "kind": item.parent.name if item.parent.name in EVIDENCE_KINDS else "other",
                        "ref": rel,
                        "sha256": _sha256_file(item),
                    }
                )

    return {
        "schema": SCHEMA,
        "id": claim_id,
        "title": title,
        "reported_at": "2026-10-29",
        "status": "verified",
        "sink": {
            "kind": sink_kind(function),
            "function": function,
            "file": sink_file,
            "line": sink_line,
            "snippet_sha256": snippet_digest(text),
            "text": text.strip(),
        },
        "entry": {"function": path[0] if path else "", "exposure": exposure},
        "path": list(path),
        "impact": impact,
        "severity": severity,
        "evidence": evidence,
    }
