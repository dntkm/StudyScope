"""Check the actual generated page and archive, without external dependencies."""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlparse, urljoin

from build import ROOT, DIST, read_archive


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.sections = []
        self.headings = []
        self.scripts = 0
        self.viewport = False
        self.language = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if "href" in attrs:
            self.links.append(attrs["href"])
        if tag == "section":
            self.sections.append(attrs.get("id"))
        if tag == "script":
            self.scripts += 1
        if tag == "meta" and attrs.get("name") == "viewport":
            self.viewport = "width=device-width" in attrs.get("content", "")
        if tag == "html":
            self.language = attrs.get("lang") == "zh-CN"


def check():
    scope, plan, sources, checkpoints, _ = read_archive()
    raw = (DIST / "index.html").read_text(encoding="utf-8")
    page = Page()
    page.feed(raw)
    assert page.sections == ["now", "plan", "footprints"], page.sections
    assert len(page.ids) == len(set(page.ids)), "Duplicate HTML ids"
    assert page.viewport and page.language and page.scripts == 0
    for link in page.links:
        parsed = urlparse(link)
        if not parsed.scheme and parsed.path:
            assert not parsed.path.startswith("/"), "Root-relative URLs break project Pages"
            assert urlparse(urljoin("https://example.invalid/StudyScope/", link)).path.startswith("/StudyScope/")
        if parsed.scheme:
            assert parsed.scheme == "https" and parsed.netloc
        elif parsed.path:
            path = (DIST / unquote(parsed.path)).resolve()
            assert DIST.resolve() in path.parents and path.is_file(), link
        elif parsed.fragment:
            assert parsed.fragment in page.ids, link
    for path in (ROOT / "learning").rglob("*"):
        if path.is_file():
            copy = DIST / "archive" / path.relative_to(ROOT / "learning")
            assert copy.read_bytes() == path.read_bytes(), str(path)
    assert raw.count('class="checkpoint"') == len(checkpoints)
    from html import escape
    for _, cp in checkpoints:
        assert escape(cp["title"], quote=True) in raw
        assert escape(cp["next_step"], quote=True) in raw
    version = json.loads((DIST / "version.json").read_text(encoding="utf-8"))
    assert version["source_digest"][:12] in raw
    assert version["updated_at"] in raw
    assert '@media(max-width:760px)' in (DIST / "style.css").read_text(encoding="utf-8")
    assert not list(DIST.rglob(".git")), "Git metadata must not be published"
    print(json.dumps({"passed": True, "sections": page.sections, "checkpoints": len(checkpoints), "sources": len(sources), "links": len(page.links), "commit": version["commit"]}))


def exercise_update():
    # All fixture edits happen in a new OS temporary directory, never in the learning archive.
    with tempfile.TemporaryDirectory(prefix="studyscope-flow-") as temporary:
        fixture = Path(temporary).resolve()
        assert Path(tempfile.gettempdir()).resolve() in fixture.parents
        for directory in ("learning", "web", "scripts"):
            shutil.copytree(ROOT / directory, fixture / directory, ignore=shutil.ignore_patterns("__pycache__"))
        catalog = json.loads((fixture / "learning/scopes.json").read_text(encoding="utf-8"))
        active = next(s for s in catalog["scopes"] if s["id"] == catalog["active_scope"])
        cp_path = sorted((fixture / "learning" / active["path"] / "checkpoints").glob("*.json"))[-1]
        cp = json.loads(cp_path.read_text(encoding="utf-8"))
        cp["title"] = "UPDATE_FLOW_FIXTURE_ONLY"
        cp["next_step"] = "NEXT_STEP_FIXTURE_ONLY"
        cp_path.write_text(json.dumps(cp, ensure_ascii=False), encoding="utf-8")
        command = [sys.executable, str(fixture / "scripts/build.py")]
        subprocess.run(command, check=True, capture_output=True)
        output = (fixture / "dist/index.html").read_text(encoding="utf-8")
        assert cp["title"] in output and cp["next_step"] in output
        assert cp_path.read_bytes() == (fixture / "dist/archive" / cp_path.relative_to(fixture / "learning")).read_bytes()
        first = json.loads((fixture / "dist/version.json").read_text(encoding="utf-8"))["source_digest"]
        cp["next_step"] = "REVISED_STEP_FIXTURE_ONLY"
        cp_path.write_text(json.dumps(cp, ensure_ascii=False), encoding="utf-8")
        subprocess.run(command, check=True, capture_output=True)
        output = (fixture / "dist/index.html").read_text(encoding="utf-8")
        assert cp["next_step"] in output and "NEXT_STEP_FIXTURE_ONLY" not in output
        assert first != json.loads((fixture / "dist/version.json").read_text(encoding="utf-8"))["source_digest"]
    print(json.dumps({"document_update_to_page": "passed", "rebuild_replaces_previous_text": True, "real_archive_unchanged": True}))


if __name__ == "__main__":
    check()
    if "--flow" in sys.argv:
        exercise_update()
