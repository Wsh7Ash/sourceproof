"""Corpus rules, generated artifacts and the CLI surface."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sourceproof.corpus import BY_SLUG, PACK, SKILLS  # noqa: E402
from sourceproof.render import build_pack, render_skill, word_count  # noqa: E402
from sourceproof.validate import (  # noqa: E402
    MIN_PATTERNS,
    MIN_PITFALLS,
    MIN_SIGNALS,
    MIN_STEPS,
    MIN_WORDS,
    validate_pack,
)

EXAMPLES = ROOT / "examples"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = {"PYTHONPATH": str(ROOT / "src"), "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, "-m", "sourceproof", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=120,
    )


# ---------------------------------------------------------------- corpus shape


def test_pack_declares_fifty_and_delivers_fifty() -> None:
    assert PACK["expected_skills"] == 50
    assert len(SKILLS) == 50


def test_slugs_and_titles_are_unique() -> None:
    assert len({skill.slug for skill in SKILLS}) == 50
    assert len({skill.title.lower() for skill in SKILLS}) == 50


def test_every_skill_passes_every_rule() -> None:
    assert validate_pack(PACK, SKILLS) == []


def test_phases_cover_the_pack() -> None:
    expected = {"ground", "graph", "sink", "locate", "grade", "ledger"}
    phases = {skill.meta_get("phase") for skill in SKILLS}
    assert phases == expected
    counts = {phase: 0 for phase in expected}
    for skill in SKILLS:
        counts[skill.meta_get("phase")] += 1
    assert min(counts.values()) >= 8


def test_strength_floors_hold_for_every_skill() -> None:
    for skill in SKILLS:
        assert len(skill.steps) >= MIN_STEPS, skill.slug
        assert len(skill.signals) >= MIN_SIGNALS, skill.slug
        assert len(skill.patterns) >= MIN_PATTERNS, skill.slug
        assert len(skill.pitfalls) >= MIN_PITFALLS, skill.slug
        assert word_count(render_skill(PACK, skill)) >= MIN_WORDS, skill.slug


def test_summaries_are_all_different() -> None:
    assert len({skill.summary for skill in SKILLS}) == 50


def test_every_reference_is_https_and_labelled() -> None:
    for skill in SKILLS:
        for ref in skill.refs:
            assert ref.startswith("[") and "](https://" in ref, (skill.slug, ref)


def test_lookup_index_covers_the_corpus() -> None:
    assert set(BY_SLUG) == {skill.slug for skill in SKILLS}


# ----------------------------------------------------------- generated files


def test_committed_skills_match_a_fresh_render() -> None:
    for skill in SKILLS:
        path = ROOT / "skills" / skill.slug / "SKILL.md"
        assert path.is_file(), f"missing generated file for {skill.slug}"
        assert path.read_text(encoding="utf-8") == render_skill(PACK, skill), skill.slug


def test_pack_json_lists_fifty_skills_with_digests() -> None:
    manifest = json.loads((ROOT / "pack.json").read_text(encoding="utf-8"))
    assert manifest["skill_count"] == 50
    assert len(manifest["skills"]) == 50
    assert all(len(entry["sha256"]) == 64 for entry in manifest["skills"])


def test_build_is_deterministic(tmp_path: Path) -> None:
    first = build_pack(tmp_path, PACK, SKILLS)
    second = build_pack(tmp_path, PACK, SKILLS)
    assert first == second
    assert len(first) == 52  # 50 skills, pack.json, results/catalog.md


def test_catalog_lists_every_skill() -> None:
    catalog = (ROOT / "results" / "catalog.md").read_text(encoding="utf-8")
    assert catalog.count("| `") == 50


# ----------------------------------------------------------------------- CLI


def test_cli_validate_reports_fifty_of_fifty() -> None:
    result = run_cli("validate")
    assert result.returncode == 0
    assert "50/50 skills valid" in result.stdout


def test_cli_validate_json_is_machine_readable() -> None:
    payload = json.loads(run_cli("validate", "--json").stdout)
    assert payload["valid"] == 50 and payload["passed"] is True


def test_cli_list_filters_by_phase() -> None:
    result = run_cli("list", "--phase", "ledger")
    assert result.returncode == 0
    assert len([line for line in result.stdout.splitlines() if line.startswith("ledger")]) >= 8


def test_cli_list_json_counts_fifty() -> None:
    assert len(json.loads(run_cli("list", "--json").stdout)) == 50


def test_cli_show_prints_front_matter() -> None:
    result = run_cli("show", "broken-hop-handling", "--raw")
    assert result.returncode == 0
    assert result.stdout.startswith("---\nname: broken-hop-handling")
    assert "## Procedure" in result.stdout


def test_cli_show_rejects_an_unknown_slug() -> None:
    assert run_cli("show", "no-such-skill").returncode == 2


def test_cli_search_ranks_matches() -> None:
    result = run_cli("search", "call path", "--limit", "5")
    assert result.returncode == 0
    assert "call" in result.stdout.lower()


def test_cli_search_reports_no_matches() -> None:
    assert run_cli("search", "zzzznotaterm").returncode == 1


def test_cli_scan_lists_definitions() -> None:
    result = run_cli("scan", "examples")
    assert result.returncode == 0
    assert "copy_field" in result.stdout
    assert "definition(s)" in result.stdout


def test_cli_scan_lists_sinks_with_their_enclosing_function() -> None:
    result = run_cli("scan", "examples", "--sinks", "--json")
    assert result.returncode == 0
    sinks = json.loads(result.stdout)
    memcpy = [sink for sink in sinks if sink["function"] == "memcpy"]
    assert memcpy and memcpy[0]["enclosing"] == "copy_field"
    assert memcpy[0]["kind"] == "unbounded-copy"


def test_cli_scan_filters_by_sink_kind() -> None:
    sinks = json.loads(run_cli("scan", "examples", "--sinks", "--kind", "sql-exec", "--json").stdout)
    assert [sink["function"] for sink in sinks] == ["execute"]


def test_cli_path_verifies_four_hops() -> None:
    result = run_cli("path", "handle_request", "memcpy", "--root", "examples")
    assert result.returncode == 0
    assert "4 hop(s), verified against the tree" in result.stdout
    assert "copy_field" in result.stdout


def test_cli_path_json_exposes_call_lines() -> None:
    payload = json.loads(
        run_cli("path", "handle_request", "memcpy", "--root", "examples", "--json").stdout
    )
    assert [hop["function"] for hop in payload["path"]] == [
        "handle_request",
        "dispatch_route",
        "parse_headers",
        "copy_field",
    ]
    assert payload["path"][0]["called_at"] == 33


def test_cli_path_exits_one_when_unreachable() -> None:
    result = run_cli("path", "route_upload", "memcpy", "--root", "examples")
    assert result.returncode == 1
    assert "no call path" in result.stderr


def test_cli_path_rejects_an_unknown_entry() -> None:
    assert run_cli("path", "nope", "memcpy", "--root", "examples").returncode == 2


def test_cli_check_verifies_the_example_claim() -> None:
    result = run_cli("check", "examples/claim.json", "--root", "examples")
    assert result.returncode == 0
    assert "grade A (100/100) verified" in result.stdout


def test_cli_check_fails_a_broken_hop(tmp_path: Path) -> None:
    claim = json.loads((EXAMPLES / "claim.json").read_text(encoding="utf-8"))
    claim["path"] = ["handle_request", "parse_headers", "dispatch_route", "copy_field"]
    path = tmp_path / "claim.json"
    path.write_text(json.dumps(claim), encoding="utf-8")
    result = run_cli("check", str(path), "--root", "examples")
    assert result.returncode == 1
    assert "broken-hop" in result.stdout


def test_cli_locate_finds_a_moved_line(tmp_path: Path) -> None:
    claim = json.loads((EXAMPLES / "claim.json").read_text(encoding="utf-8"))
    claim["sink"]["line"] = 12
    path = tmp_path / "claim.json"
    path.write_text(json.dumps(claim), encoding="utf-8")
    result = run_cli("locate", str(path), "--root", "examples")
    assert result.returncode == 0
    assert "workspace/src/parse.c:10" in result.stdout


def test_cli_locate_exits_one_when_the_line_is_gone(tmp_path: Path) -> None:
    claim = json.loads((EXAMPLES / "claim.json").read_text(encoding="utf-8"))
    claim["sink"]["snippet_sha256"] = "0" * 64
    path = tmp_path / "claim.json"
    path.write_text(json.dumps(claim), encoding="utf-8")
    assert run_cli("locate", str(path), "--root", "examples").returncode == 1


def test_cli_verify_passes_the_example_ledger() -> None:
    result = run_cli("verify", "examples/ledger.jsonl", "--root", "examples")
    assert result.returncode == 0
    assert "2/2 claim(s) verified" in result.stdout


def test_cli_verify_fails_an_empty_ledger(tmp_path: Path) -> None:
    path = tmp_path / "empty.jsonl"
    path.write_text("", encoding="utf-8")
    assert run_cli("verify", str(path), "--root", "examples").returncode == 2


def test_cli_report_renders_sections() -> None:
    result = run_cli("report", "examples/claim.json", "--root", "examples")
    assert result.returncode == 0
    for heading in ("## Sink", "## Path", "## Impact", "## Verification"):
        assert heading in result.stdout


def test_cli_scaffold_emits_the_schema(tmp_path: Path) -> None:
    out = tmp_path / "new.json"
    assert run_cli("scaffold", "A finding", "--id", "SP-010", "--out", str(out)).returncode == 0
    claim = json.loads(out.read_text(encoding="utf-8"))
    assert claim["schema"] == "sourceproof/v1"
    assert claim["id"] == "SP-010"


def test_cli_sinks_prints_the_catalogue() -> None:
    result = run_cli("sinks", "--json")
    assert result.returncode == 0
    catalogue = json.loads(result.stdout)
    assert any("memcpy" in entry["functions"] for entry in catalogue)


def test_cli_anchor_prints_a_digest() -> None:
    result = run_cli("anchor", "examples/workspace/src/parse.c", "10")
    assert result.returncode == 0
    assert "digest" in result.stdout
    assert len(result.stdout.split("digest")[1].strip().split()) == 1


def test_cli_anchor_rejects_a_line_past_the_end() -> None:
    assert run_cli("anchor", "examples/workspace/src/parse.c", "999").returncode == 2


def test_cli_version_is_printed() -> None:
    result = run_cli("--version")
    assert result.returncode == 0
    assert "sourceproof 1.0.0" in result.stdout
