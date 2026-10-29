"""Tree indexing, call paths and claim grading."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sourceproof.claims import (  # noqa: E402
    ClaimError,
    anchor_of,
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
from sourceproof.sources import (  # noqa: E402
    Definition,
    SINK_KINDS,
    Tree,
    clike_definitions,
    index_tree,
    language_of,
    python_definitions,
    sink_kind,
    strip_noise,
)

EXAMPLES = ROOT / "examples"
WORKSPACE = EXAMPLES / "workspace"

C_SOURCE = """\
#include <string.h>

static int read_message(int fd, char *buf)
{
    return recv(fd, buf, 10, 0);
}

int copy_field(char *dst, const char *src, int len)
{
    memcpy(dst, src, (size_t)len);
    return len;
}

int parse_headers(char *body)
{
    return copy_field(body, body + 4, 8);
}
"""

PY_SOURCE = """\
import sqlite3


def route_upload(request):
    return store_file(request.args["name"])


def store_file(name):
    cur = sqlite3.connect("app.db").cursor()
    cur.execute("INSERT INTO files VALUES ('%s')" % name)
"""


# ----------------------------------------------------------------- parsing


def test_clike_definitions_are_bounded_by_braces() -> None:
    defs = {d.name: d for d in clike_definitions("parse.c", C_SOURCE.splitlines())}
    assert set(defs) == {"read_message", "copy_field", "parse_headers"}
    assert defs["copy_field"].start == 8
    assert defs["copy_field"].end == 12
    assert 10 >= defs["copy_field"].start and 10 <= defs["copy_field"].end


def test_clike_calls_are_extracted_inside_the_body_only() -> None:
    defs = {d.name: d for d in clike_definitions("parse.c", C_SOURCE.splitlines())}
    assert defs["copy_field"].calls_name("memcpy")
    assert not defs["parse_headers"].calls_name("memcpy")
    assert defs["parse_headers"].calls_name("copy_field")


def test_definition_does_not_look_recursive() -> None:
    defs = {d.name: d for d in clike_definitions("parse.c", C_SOURCE.splitlines())}
    assert not defs["copy_field"].calls_name("copy_field")


def test_python_definitions_respect_indentation() -> None:
    defs = {d.name: d for d in python_definitions("api.py", PY_SOURCE.splitlines())}
    assert set(defs) == {"route_upload", "store_file"}
    assert defs["route_upload"].calls_name("store_file")
    assert not defs["route_upload"].calls_name("execute")


def test_pointer_return_type_parses() -> None:
    defs = clike_definitions("s.c", ["void *worker(void *arg)", "{", "    return arg;", "}"])
    assert [d.name for d in defs] == ["worker"]


def test_static_function_parses() -> None:
    defs = clike_definitions("s.c", ["static int helper(int x)", "{", "    return x;", "}"])
    assert [d.name for d in defs] == ["helper"]


def test_prototype_is_not_a_definition() -> None:
    defs = clike_definitions("p.h", ["int parse_headers(char *body);"])
    assert defs == []


def test_brace_inside_a_string_does_not_end_the_body() -> None:
    source = ['int f(void)', '{', '    puts("}");', '    return 0;', '}', '', 'int g(void)', '{', '    return 1;', '}']
    defs = {d.name: d for d in clike_definitions("s.c", source)}
    assert defs["f"].end == 5
    assert set(defs) == {"f", "g"}


def test_control_words_are_not_definitions() -> None:
    defs = clike_definitions("s.c", ["if (x) {", "    y();", "}"])
    assert defs == []


def test_strip_noise_removes_comments_and_strings() -> None:
    assert "memcpy" not in strip_noise('    /* memcpy(dst, src) */ puts("memcpy(");')
    assert "memcpy" in strip_noise("    memcpy(dst, src);")


def test_language_detection() -> None:
    assert language_of("a/b.py") == "python"
    assert language_of("a/b.c") == "clike"
    assert language_of("a/b.tpl") == ""


def test_sink_catalogue_is_exact() -> None:
    assert sink_kind("memcpy") == "unbounded-copy"
    assert sink_kind("cursor.execute") == "sql-exec"
    assert sink_kind("safe_copy") == ""
    assert "memcpy" not in SINK_KINDS


# -------------------------------------------------------------------- paths


def tree_for(source: str, name: str = "s.c") -> Tree:
    defs = clike_definitions(name, source.splitlines())
    return Tree(root=Path("."), files=(name,), definitions=tuple(defs))


def test_path_follows_real_call_edges() -> None:
    tree = tree_for(C_SOURCE)
    trail = tree.path("parse_headers", "memcpy")
    assert trail is not None
    assert [d.name for d, _ in trail] == ["parse_headers", "copy_field"]
    assert trail[-1][1] == 10


def test_path_returns_none_when_unreachable() -> None:
    tree = tree_for(C_SOURCE)
    assert tree.path("read_message", "memcpy") is None


def test_path_from_unknown_entry_is_none() -> None:
    assert tree_for(C_SOURCE).path("nope", "memcpy") is None


def test_reachable_matches_path() -> None:
    tree = tree_for(C_SOURCE)
    assert tree.reachable("parse_headers", "memcpy")
    assert not tree.reachable("read_message", "memcpy")


def test_unresolved_lists_calls_without_definitions() -> None:
    tree = tree_for(C_SOURCE)
    assert "memcpy" in tree.unresolved
    assert "copy_field" not in tree.unresolved


def test_path_respects_depth_limit() -> None:
    """``max_depth`` counts hops, so two hops need a bound of at least two."""
    tree = tree_for(C_SOURCE)
    assert tree.path("parse_headers", "memcpy", max_depth=2) is not None
    assert tree.path("parse_headers", "memcpy", max_depth=1) is None


def test_path_is_deterministic() -> None:
    tree = tree_for(C_SOURCE)
    first = [(d.name, line) for d, line in tree.path("parse_headers", "memcpy") or []]
    second = [(d.name, line) for d, line in tree.path("parse_headers", "memcpy") or []]
    assert first == second


def test_enclosing_picks_the_innermost_definition() -> None:
    tree = tree_for(C_SOURCE)
    assert tree.enclosing("s.c", 10).name == "copy_field"
    assert tree.enclosing("s.c", 6).name == "read_message"


def test_index_tree_reads_the_example_workspace() -> None:
    tree = index_tree(WORKSPACE)
    assert "src/parse.c" in tree.files
    assert tree.exists("handle_request")
    assert tree.path("handle_request", "memcpy") is not None
    assert any(sink.kind == "sql-exec" for sink in tree.sinks)


def test_index_tree_rejects_a_missing_directory(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        index_tree(tmp_path / "nope")


# ----------------------------------------------------------------- grading


def example_claim() -> dict:
    return load_claim(EXAMPLES / "claim.json")


def test_example_claim_is_verified() -> None:
    report = grade(example_claim(), EXAMPLES, index_tree(EXAMPLES))
    assert report.grade == "A"
    assert report.score == 100
    assert report.submittable
    assert [f.rule for f in report.findings] == []


def test_example_python_claim_is_verified() -> None:
    claim = load_claim(EXAMPLES / "claim-python.json")
    assert grade(claim, EXAMPLES, index_tree(EXAMPLES)).submittable


def test_broken_hop_blocks_and_names_real_callees() -> None:
    claim = example_claim()
    claim["path"] = ["handle_request", "parse_headers", "dispatch_route", "copy_field"]
    report = grade(claim, EXAMPLES, index_tree(EXAMPLES))
    broken = [f for f in report.findings if f.rule == "broken-hop"]
    assert broken and "dispatch_route" in broken[0].hint
    assert not report.submittable


def test_unknown_hop_blocks() -> None:
    claim = example_claim()
    claim["path"] = ["handle_request", "does_not_exist", "copy_field"]
    report = grade(claim, EXAMPLES, index_tree(EXAMPLES))
    assert "unknown-hop" in {f.rule for f in report.blocking}


def test_snippet_mismatch_reports_where_the_line_moved() -> None:
    claim = example_claim()
    claim["sink"]["line"] = 12
    report = grade(claim, EXAMPLES, index_tree(EXAMPLES))
    mismatch = [f for f in report.blocking if f.rule == "snippet-mismatch"]
    assert mismatch and "parse.c:10" in mismatch[0].hint


def test_sink_absent_blocks() -> None:
    claim = example_claim()
    claim["sink"]["line"] = 12
    claim["sink"]["snippet_sha256"] = snippet_digest(
        (WORKSPACE / "src" / "parse.c").read_text(encoding="utf-8").splitlines()[11]
    )
    report = grade(claim, EXAMPLES, index_tree(EXAMPLES))
    assert "sink-absent" in {f.rule for f in report.blocking}


def test_sink_kind_mismatch_blocks() -> None:
    claim = example_claim()
    claim["sink"]["kind"] = "command-exec"
    report = grade(claim, EXAMPLES, index_tree(EXAMPLES))
    assert "sink-kind-mismatch" in {f.rule for f in report.blocking}


def test_sink_owner_mismatch_blocks() -> None:
    claim = example_claim()
    claim["path"] = ["handle_request", "dispatch_route", "parse_headers"]
    claim["entry"]["function"] = "handle_request"
    report = grade(claim, EXAMPLES, index_tree(EXAMPLES))
    assert "sink-owner" in {f.rule for f in report.blocking}


def test_entry_mismatch_blocks() -> None:
    claim = example_claim()
    claim["entry"]["function"] = "dispatch_route"
    report = grade(claim, EXAMPLES, index_tree(EXAMPLES))
    assert "entry-mismatch" in {f.rule for f in report.blocking}


def test_missing_path_blocks() -> None:
    claim = example_claim()
    claim["path"] = []
    assert "path" in {f.rule for f in grade(claim, EXAMPLES, index_tree(EXAMPLES)).blocking}


def test_line_past_end_blocks() -> None:
    claim = example_claim()
    claim["sink"]["line"] = 999
    assert "sink-line-range" in {
        f.rule for f in grade(claim, EXAMPLES, index_tree(EXAMPLES)).blocking
    }


def test_missing_sink_file_blocks(tmp_path: Path) -> None:
    claim = example_claim()
    claim["sink"]["file"] = "workspace/src/gone.c"
    report = grade(claim, EXAMPLES, index_tree(EXAMPLES))
    assert "sink-file-missing" in {f.rule for f in report.blocking}


def test_missing_impact_blocks() -> None:
    claim = example_claim()
    claim["impact"] = ""
    assert "impact" in {f.rule for f in grade(claim, EXAMPLES, index_tree(EXAMPLES)).blocking}


def test_missing_evidence_blocks() -> None:
    claim = example_claim()
    claim["evidence"] = []
    assert "evidence" in {f.rule for f in grade(claim, EXAMPLES, index_tree(EXAMPLES)).blocking}


def test_evidence_drift_blocks() -> None:
    claim = example_claim()
    claim["evidence"][0]["sha256"] = "0" * 64
    assert "evidence-drift" in {
        f.rule for f in grade(claim, EXAMPLES, index_tree(EXAMPLES)).blocking
    }


def test_evidence_missing_blocks() -> None:
    claim = example_claim()
    claim["evidence"][0]["ref"] = "evidence/nowhere.txt"
    assert "evidence-missing" in {
        f.rule for f in grade(claim, EXAMPLES, index_tree(EXAMPLES)).blocking
    }


def test_wrong_schema_blocks() -> None:
    claim = example_claim()
    claim["schema"] = "other/v1"
    assert not grade(claim, EXAMPLES, index_tree(EXAMPLES)).submittable


def test_unknown_exposure_is_major_not_blocking() -> None:
    claim = example_claim()
    claim["entry"]["exposure"] = "sometimes"
    report = grade(claim, EXAMPLES, index_tree(EXAMPLES))
    assert report.submittable
    assert "exposure" in {f.rule for f in report.findings}


def test_grading_without_a_tree_skips_reachability() -> None:
    claim = example_claim()
    claim["path"] = ["handle_request", "invented", "copy_field"]
    report = grade(claim, EXAMPLES, None)
    assert report.submittable  # no tree, so hops cannot be refuted


# ------------------------------------------------------------------ anchors


def test_anchor_ignores_line_and_title() -> None:
    claim = example_claim()
    other = json.loads(json.dumps(claim))
    other["sink"]["line"] = 99
    other["title"] = "Different words entirely"
    assert anchor_of(claim) == anchor_of(other)


def test_anchor_changes_when_the_path_changes() -> None:
    claim = example_claim()
    other = json.loads(json.dumps(claim))
    other["path"] = ["handle_request", "copy_field"]
    assert anchor_of(claim) != anchor_of(other)


def test_locate_finds_the_quoted_line() -> None:
    tree = index_tree(EXAMPLES)
    hits = locate(tree, example_claim()["sink"]["snippet_sha256"])
    assert ("workspace/src/parse.c", 10) in hits


def test_locate_returns_nothing_for_an_unknown_digest() -> None:
    assert locate(index_tree(EXAMPLES), "0" * 64) == []


# ------------------------------------------------------------------- ledger


def test_ledger_reads_jsonl_and_document_forms(tmp_path: Path) -> None:
    claim = example_claim()
    jsonl = tmp_path / "a.jsonl"
    jsonl.write_text(json.dumps(claim) + "\n" + json.dumps(claim) + "\n", encoding="utf-8")
    assert len(load_ledger(jsonl)) == 2

    document = tmp_path / "b.json"
    document.write_text(json.dumps({"claims": [claim]}), encoding="utf-8")
    assert len(load_ledger(document)) == 1


def test_ledger_rejects_broken_json(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text("{not json}\n", encoding="utf-8")
    with pytest.raises(ClaimError):
        load_ledger(path)


def test_verify_ledger_flags_a_duplicate_id() -> None:
    claim = example_claim()
    graded = verify_ledger([claim, json.loads(json.dumps(claim))], index_tree(EXAMPLES))
    rules = {f.rule for _, report in graded for f in report.findings}
    assert "ledger-duplicate-id" in rules
    # the first occurrence is the original; the repeat is the one that fails
    assert graded[0][1].submittable
    assert not graded[1][1].submittable


def test_verify_ledger_flags_a_duplicate_claim_with_a_new_id() -> None:
    claim = example_claim()
    copy = json.loads(json.dumps(claim))
    copy["id"] = "SP-777"
    graded = verify_ledger([claim, copy], index_tree(EXAMPLES))
    rules = {f.rule for _, report in graded for f in report.findings}
    assert "ledger-duplicate-claim" in rules
    assert graded[1][1].grade == "D"


def test_verify_ledger_keeps_two_entries_separate() -> None:
    tree = index_tree(EXAMPLES)
    graded = verify_ledger([example_claim(), load_claim(EXAMPLES / "claim-python.json")], tree)
    assert all(report.submittable for _, report in graded)


# ---------------------------------------------------------------- rendering


def test_scaffold_shape() -> None:
    claim = scaffold("A finding", "SP-009")
    assert claim["schema"] == "sourceproof/v1"
    assert claim["path"] == []
    assert claim["sink"]["line"] == 0


def test_render_claim_includes_path_and_grade() -> None:
    claim = example_claim()
    text = render_claim(claim, grade(claim, EXAMPLES, index_tree(EXAMPLES)))
    assert "## Path" in text and "## Verification" in text
    assert "copy_field" in text


def test_build_claim_takes_its_digest_from_the_tree() -> None:
    tree = index_tree(EXAMPLES)
    claim = build_claim(
        "SP-100",
        "Built claim",
        tree,
        "workspace/src/parse.c",
        10,
        ["handle_request", "dispatch_route", "parse_headers", "copy_field"],
        "pre-auth",
        "Out-of-bounds write.",
        "high",
        EXAMPLES / "evidence",
    )
    assert claim["sink"]["function"] == "memcpy"
    assert claim["sink"]["kind"] == "unbounded-copy"
    assert grade(claim, EXAMPLES, tree).submittable


def test_build_claim_rejects_evidence_outside_the_tree(tmp_path: Path) -> None:
    tree = index_tree(EXAMPLES)
    (tmp_path / "loose.txt").write_text("outside", encoding="utf-8")
    with pytest.raises(ClaimError):
        build_claim(
            "SP-101",
            "Outside",
            tree,
            "workspace/src/parse.c",
            10,
            ["copy_field"],
            "local",
            "Impact.",
            "low",
            tmp_path,
        )
