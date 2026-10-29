"""Index a source tree: function definitions, call sites and sink sites.

The point of this module is not to be a compiler. It is to answer one question
the reviewer cannot answer from prose: *does the call path this finding claims
actually exist in the tree?* That needs three things — where functions start and
end, what each one calls, and where catalogue sinks appear — and nothing else.

The parser is heuristic and says so:

* **Python** definitions are found by ``def``/``async def`` and bounded by
  indentation.
* **C-like** definitions (C, C++, Java, Go, Rust, JavaScript, TypeScript) are
  found by a signature line followed by a brace block, bounded by brace counting.
* Comments and string literals are stripped per line before calls and braces are
  counted, so ``printf("{")`` does not break the brace depth.
* A call is an identifier followed by ``(`` inside a definition body. That is an
  over-approximation: it counts calls in dead branches, and it cannot see calls
  made through a function pointer, a macro, a virtual dispatch or a callback
  registered elsewhere.

Those limits are reported rather than hidden: ``Tree.unresolved`` counts call
names that no definition in the tree matches, and a claim that depends on such a
hop is graded on what the tree proves, not on what the prose asserts.
"""

from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Sequence

LANG_BY_SUFFIX = {
    ".py": "python",
    ".c": "clike",
    ".h": "clike",
    ".cc": "clike",
    ".cpp": "clike",
    ".hpp": "clike",
    ".js": "clike",
    ".mjs": "clike",
    ".ts": "clike",
    ".go": "clike",
    ".rs": "clike",
    ".java": "clike",
    ".kt": "clike",
    ".php": "clike",
    ".rb": "clike",
}

# Directory names that are never part of the reviewed tree.
SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "target",
    "__pycache__",
    ".venv",
    "venv",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
}

MAX_FILE_BYTES = 2 * 1024 * 1024

CONTROL_WORDS = {
    "if",
    "for",
    "while",
    "switch",
    "else",
    "do",
    "return",
    "case",
    "sizeof",
    "catch",
    "try",
    "defined",
    "typedef",
    "elif",
    "with",
    "assert",
    "del",
    "lambda",
}

TYPE_WORDS = (
    "static",
    "inline",
    "extern",
    "const",
    "unsigned",
    "signed",
    "struct",
    "enum",
    "union",
    "pub",
    "async",
    "export",
    "virtual",
    "override",
    "final",
    "public",
    "private",
    "protected",
    "internal",
)

PY_DEF_RE = re.compile(r"^(?P<indent>[ \t]*)(?:async\s+)?def\s+(?P<name>[A-Za-z_]\w*)\s*\(")
CLIKE_DEF_RE = re.compile(
    r"^[ \t]*(?:(?:" + "|".join(TYPE_WORDS) + r")\s+)*"
    r"(?:[A-Za-z_][\w:<>\[\],\*&]*?[ \t]+)?"
    # A pointer return type puts a '*' between the type and the name:
    # ``void *worker(void *arg)``. Without this the name cannot start.
    r"[*&]*[ \t]*"
    r"(?P<name>[A-Za-z_]\w*)[ \t]*\((?P<params>[^;{}]*)\)[ \t]*(?:const[ \t]*)?"
    r"(?:->[^{]*)?(?P<brace>\{)?[ \t]*$"
)
CALL_RE = re.compile(r"\b(?P<name>[A-Za-z_]\w*)\s*\(")
STRING_RE = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/")

# (kind, function name) pairs. A sink is a function whose call is worth a
# finding when its arguments are attacker-controlled.
SINK_CATALOGUE: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "unbounded-copy",
        ("memcpy", "memmove", "strcpy", "strcat", "sprintf", "vsprintf", "gets", "wcscpy", "bcopy", "alloca"),
    ),
    (
        "command-exec",
        (
            "system",
            "popen",
            "execl",
            "execv",
            "execve",
            "execlp",
            "execvp",
            "os.system",
            "os.popen",
            "subprocess.call",
            "subprocess.run",
            "subprocess.Popen",
            "Runtime.getRuntime().exec",
            "child_process.exec",
            "shell_exec",
            "passthru",
        ),
    ),
    (
        "sql-exec",
        (
            "mysql_query",
            "mysqli_query",
            "PQexec",
            "sqlite3_exec",
            "cursor.execute",
            "execute",
            "rawQuery",
            "query",
            "Exec",
            "createQuery",
        ),
    ),
    (
        "path-open",
        ("fopen", "open", "os.open", "readFile", "readFileSync", "sendfile", "SendFile", "FileInputStream"),
    ),
    (
        "deserialization",
        (
            "pickle.loads",
            "yaml.load",
            "unserialize",
            "readObject",
            "JSON.parse",
            "marshal.loads",
            "loads",
        ),
    ),
    ("dynamic-code", ("eval", "exec", "compile", "Function", "setTimeout")),
    ("format-string", ("printf", "fprintf", "syslog", "snprintf", "vprintf")),
    ("template-render", ("render", "render_template", "Template", "from_string")),
    ("redirect", ("redirect", "Redirect", "sendRedirect", "header")),
)

SINK_KIND: dict[str, str] = {
    function: kind for kind, functions in SINK_CATALOGUE for function in functions
}
SINK_KINDS: tuple[str, ...] = tuple(kind for kind, _ in SINK_CATALOGUE)


def sink_kind(function: str) -> str:
    """Catalogue kind for a function name, or ``""`` when it is not a sink.

    Names are compared exactly, including a dotted receiver
    (``cursor.execute``). Guessing a kind from a substring would mark every
    ``execute`` wrapper as SQL, so unknown names stay unknown.
    """
    return SINK_KIND.get(function, "")


def language_of(path: str | Path) -> str:
    return LANG_BY_SUFFIX.get(Path(path).suffix.lower(), "")


@dataclass(frozen=True)
class Definition:
    """One function definition, bounded by its real start and end line."""

    name: str
    file: str
    start: int
    end: int
    language: str
    params: str = ""
    calls: dict[str, tuple[int, ...]] = field(default_factory=dict)

    def where(self) -> str:
        return f"{self.file}:{self.start}"

    def calls_name(self, name: str) -> bool:
        return name in self.calls

    def call_lines(self, name: str) -> tuple[int, ...]:
        return self.calls.get(name, ())

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "file": self.file,
            "start": self.start,
            "end": self.end,
            "language": self.language,
            "params": self.params,
            "calls": sorted(self.calls),
        }


@dataclass(frozen=True)
class SinkSite:
    """A catalogue sink call, with the function that contains it."""

    kind: str
    function: str
    file: str
    line: int
    text: str
    enclosing: str

    def as_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "function": self.function,
            "file": self.file,
            "line": self.line,
            "enclosing": self.enclosing,
            "text": self.text,
        }


def strip_noise(line: str) -> str:
    """Remove comments and string literals so calls and braces can be counted."""
    text = BLOCK_COMMENT_RE.sub("", line)
    text = STRING_RE.sub('""', text)
    for marker in ("//", "#"):
        index = text.find(marker)
        if index != -1:
            text = text[:index]
    return text


def _indent_width(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def python_definitions(rel: str, lines: Sequence[str]) -> list[Definition]:
    defs: list[Definition] = []
    index = 0
    total = len(lines)
    while index < total:
        match = PY_DEF_RE.match(lines[index])
        if not match:
            index += 1
            continue
        indent = len(match.group("indent").expandtabs(4))
        end = index
        cursor = index + 1
        while cursor < total:
            line = lines[cursor]
            if line.strip() and _indent_width(line.expandtabs(4)) <= indent:
                break
            end = cursor
            cursor += 1
        body = lines[index : end + 1]
        defs.append(
            Definition(
                name=match.group("name"),
                file=rel,
                start=index + 1,
                end=end + 1,
                language="python",
                params=_params_of(lines[index]),
                calls=_calls_in(body, index + 1, skip=1),
            )
        )
        index = end + 1
    return defs


def _params_of(line: str) -> str:
    start = line.find("(")
    end = line.rfind(")")
    return line[start + 1 : end].strip() if start != -1 and end > start else ""


def _calls_in(body: Sequence[str], first_line: int, skip: int = 0) -> dict[str, tuple[int, ...]]:
    """Calls made inside a definition body.

    The signature line is skipped: ``int copy_field(char *dst)`` contains
    ``copy_field(``, and counting it would make every function look recursive
    and would let a function appear reachable from itself.
    """
    calls: dict[str, list[int]] = {}
    for offset, line in enumerate(body):
        if offset < skip:
            continue
        cleaned = strip_noise(line)
        for match in CALL_RE.finditer(cleaned):
            name = match.group("name")
            if name in CONTROL_WORDS:
                continue
            calls.setdefault(name, []).append(first_line + offset)
    return {name: tuple(sorted(set(where))) for name, where in calls.items()}


def clike_definitions(rel: str, lines: Sequence[str]) -> list[Definition]:
    defs: list[Definition] = []
    index = 0
    total = len(lines)
    while index < total:
        match = CLIKE_DEF_RE.match(lines[index])
        if not match or match.group("name") in CONTROL_WORDS:
            index += 1
            continue

        brace_line = index if match.group("brace") else None
        if brace_line is None:
            cursor = index + 1
            while cursor < total and not lines[cursor].strip():
                cursor += 1
            if cursor < total and lines[cursor].lstrip().startswith("{"):
                brace_line = cursor
        if brace_line is None:
            index += 1  # a declaration or a call, not a definition
            continue

        depth = 0
        end = brace_line
        started = False
        cursor = brace_line
        while cursor < total:
            cleaned = strip_noise(lines[cursor])
            depth += cleaned.count("{") - cleaned.count("}")
            if "{" in cleaned:
                started = True
            if started and depth <= 0:
                end = cursor
                break
            cursor += 1
        else:
            end = total - 1

        body = lines[index : end + 1]
        defs.append(
            Definition(
                name=match.group("name"),
                file=rel,
                start=index + 1,
                end=end + 1,
                language="clike",
                params=(match.group("params") or "").strip(),
                calls=_calls_in(body, index + 1, skip=1),
            )
        )
        index = end + 1
    return defs


@dataclass
class Tree:
    """An indexed source tree."""

    root: Path
    files: tuple[str, ...] = ()
    definitions: tuple[Definition, ...] = ()
    sinks: tuple[SinkSite, ...] = ()
    skipped: tuple[str, ...] = ()
    unsupported: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        self._by_name: dict[str, list[Definition]] = {}
        for definition in self.definitions:
            self._by_name.setdefault(definition.name, []).append(definition)

    # ------------------------------------------------------------- lookups
    def named(self, name: str) -> list[Definition]:
        return list(self._by_name.get(name, ()))

    def exists(self, name: str) -> bool:
        return name in self._by_name

    @property
    def unresolved(self) -> tuple[str, ...]:
        """Call names that no definition in the tree matches."""
        called = {name for definition in self.definitions for name in definition.calls}
        return tuple(sorted(name for name in called if name not in self._by_name))

    def enclosing(self, file: str, line: int) -> Definition | None:
        """The innermost definition containing ``file:line``."""
        best: Definition | None = None
        for definition in self.definitions:
            if definition.file != file:
                continue
            if definition.start <= line <= definition.end:
                if best is None or definition.start >= best.start:
                    best = definition
        return best

    def callees(self, definition: Definition) -> list[Definition]:
        """Definitions this one calls, resolved by name."""
        out: list[Definition] = []
        for name in definition.calls:
            out.extend(self.named(name))
        return out

    def edges(self, definition: Definition) -> list[tuple[Definition, int]]:
        """``(callee, call line)`` for every resolved call inside ``definition``."""
        pairs: list[tuple[Definition, int]] = []
        for name in definition.calls:
            for target in self.named(name):
                for line in definition.call_lines(name):
                    pairs.append((target, line))
        pairs.sort(key=lambda pair: (pair[1], pair[0].file, pair[0].start))
        return pairs

    # ---------------------------------------------------------------- paths
    def path(self, entry: str, sink: str, max_depth: int = 12) -> list[tuple[Definition, int]] | None:
        """Shortest call path from a definition named ``entry`` that calls ``sink``.

        The sink does not have to be defined in the tree — ``memcpy`` and
        ``cursor.execute`` never are — so the goal is a definition whose body
        calls it, and the returned path ends with the function that contains
        the sink. Each hop carries the line where it calls the next one; the
        last hop carries the sink's line.

        Breadth-first, so the path is shortest in hops, and deterministic
        because callers are visited in name order.
        """
        starts = sorted(self.named(entry), key=lambda d: (d.file, d.start))
        if not starts:
            return None

        queue: deque[tuple[Definition, list[tuple[Definition, int]]]] = deque()
        for start in starts:
            queue.append((start, [(start, 0)]))
        seen: set[tuple[str, int]] = {(d.file, d.start) for d in starts}

        while queue:
            current, trail = queue.popleft()
            if len(trail) > max_depth:
                continue
            if current.calls_name(sink):
                line = current.call_lines(sink)[0]
                return trail[:-1] + [(current, line)]
            for target, line in self.edges(current):
                key = (target.file, target.start)
                if key in seen:
                    continue
                seen.add(key)
                queue.append((target, trail[:-1] + [(current, line), (target, 0)]))
        return None

    def reachable(self, entry: str, sink: str, max_depth: int = 12) -> bool:
        return self.path(entry, sink, max_depth) is not None

    # ---------------------------------------------------------------- report
    def as_dict(self) -> dict[str, object]:
        return {
            "root": str(self.root),
            "files": len(self.files),
            "definitions": len(self.definitions),
            "sinks": len(self.sinks),
            "skipped": list(self.skipped),
            "unsupported": list(self.unsupported),
            "unresolved_calls": list(self.unresolved),
        }


def _iter_sources(root: Path) -> Iterator[tuple[str, str, str]]:
    """Yield ``(relative posix path, language, text)`` for every source file."""
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        parts = set(path.relative_to(root).parts[:-1])
        if parts & SKIP_DIRS:
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            continue
        language = language_of(path)
        if not language:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        yield path.relative_to(root).as_posix(), language, text


def index_tree(root: Path) -> Tree:
    """Index every supported source file under ``root``."""
    if not root.is_dir():
        raise FileNotFoundError(f"source tree not found: {root}")

    root = root.resolve()
    files: list[str] = []
    definitions: list[Definition] = []
    sinks: list[SinkSite] = []
    unsupported: list[str] = []
    skipped: list[str] = []

    for rel, language, text in _iter_sources(root):
        lines = text.splitlines()
        files.append(rel)
        found = (
            python_definitions(rel, lines)
            if language == "python"
            else clike_definitions(rel, lines)
        )
        definitions.extend(found)
        for number, line in enumerate(lines, start=1):
            cleaned = strip_noise(line)
            for match in CALL_RE.finditer(cleaned):
                function = match.group("name")
                kind = sink_kind(function)
                if not kind:
                    continue
                owner = next(
                    (d for d in found if d.start <= number <= d.end),
                    None,
                )
                sinks.append(
                    SinkSite(
                        kind=kind,
                        function=function,
                        file=rel,
                        line=number,
                        text=line.strip()[:200],
                        enclosing=owner.name if owner else "",
                    )
                )

    for path in sorted(root.rglob("*")):
        if path.is_file() and not language_of(path):
            suffix = path.suffix.lower() or path.name
            if suffix not in {".md", ".json", ".jsonl", ".txt", ".yml", ".yaml"}:
                unsupported.append(suffix)
    unsupported = sorted(set(unsupported))
    skipped = sorted(set(skipped))

    return Tree(
        root=root,
        files=tuple(files),
        definitions=tuple(sorted(definitions, key=lambda d: (d.file, d.start))),
        sinks=tuple(sinks),
        skipped=tuple(skipped),
        unsupported=tuple(unsupported),
    )


def enclosing_function(tree: Tree, file: str, line: int) -> str:
    definition = tree.enclosing(file, line)
    return definition.name if definition else ""
