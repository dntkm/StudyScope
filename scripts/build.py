"""Build the read-only learning archive using Python's standard library."""
from __future__ import annotations

import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timezone
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / ("docs" if "--docs" in sys.argv else "dist")
STATUS = {"待探索", "讨论中", "待验证", "阶段性理解", "暂缓"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def texts(value, label: str, allow_empty=False):
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ValueError(f"{label} must be a list")
    if any(not isinstance(v, str) or not v.strip() for v in value):
        raise ValueError(f"{label} must contain non-empty strings")


def git(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), *args], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def read_archive():
    catalog = load(ROOT / "learning/scopes.json")
    if catalog["schema_version"] != 1:
        raise ValueError("Unsupported scope index schema")
    scope_ids = [item["id"] for item in catalog["scopes"]]
    if len(scope_ids) != len(set(scope_ids)) or catalog["active_scope"] not in scope_ids:
        raise ValueError("Scope ids must be unique and active_scope must exist")
    scope = next(item for item in catalog["scopes"] if item["id"] == catalog["active_scope"])
    if not re.fullmatch(r"[a-z0-9-]+", scope["id"]) or scope["path"] != "scopes/" + scope["id"]:
        raise ValueError("Invalid scope path")
    scope_dir = ROOT / "learning" / scope["path"]
    if scope_dir.is_symlink() or (ROOT / "learning").resolve() not in scope_dir.resolve().parents:
        raise ValueError("Scope must be inside the learning archive")
    if not (scope_dir / "profile.md").is_file():
        raise ValueError("The active scope needs a profile")
    plan = load(scope_dir / "map.json")
    sources = load(scope_dir / "sources.json")
    checkpoints = [(p, load(p)) for p in sorted((scope_dir / "checkpoints").glob("*.json"))]
    if not checkpoints:
        raise ValueError("At least one honest setup or learning checkpoint is required")
    source_map = {}
    for source in sources:
        if not re.fullmatch(r"[a-z0-9-]+", source["id"]) or source["id"] in source_map:
            raise ValueError("Source ids must be unique URL-safe slugs")
        parsed = urlparse(source["url"])
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise ValueError("Sources must use public HTTPS URLs without credentials")
        for field in ("title", "use"):
            if not isinstance(source[field], str) or not source[field].strip():
                raise ValueError(f"Missing source {field}")
        if source.get("verified_at"):
            date.fromisoformat(source["verified_at"])
        source_map[source["id"]] = source
    if plan["schema_version"] != 1:
        raise ValueError("Unsupported map schema")
    date.fromisoformat(plan["updated_at"])
    refs = list(plan["current"]["source_ids"]) + [plan["direction"]["source_id"]]
    for field in ("topic", "state", "last_stop", "next_step"):
        if not isinstance(plan["current"][field], str) or not plan["current"][field].strip():
            raise ValueError(f"Missing current.{field}")
    seen = set()
    for area in plan["areas"]:
        if not re.fullmatch(r"[a-z0-9-]+", area["id"]) or area["id"] in seen:
            raise ValueError("Area ids must be unique slugs")
        seen.add(area["id"])
        if area["status"] not in STATUS:
            raise ValueError(f"Use an observation status from {sorted(STATUS)}")
        texts(area["questions"], "questions")
    if not plan["areas"]:
        raise ValueError("The active scope needs a coarse question map")
    for _, cp in checkpoints:
        if cp["schema_version"] != 1 or cp["kind"] not in {"setup", "learning"}:
            raise ValueError("Unsupported checkpoint schema or kind")
        date.fromisoformat(cp["date"])
        for field in ("resolved", "evidence", "open_questions", "source_ids"):
            texts(cp[field], field, allow_empty=field in {"open_questions", "source_ids"})
        if not isinstance(cp["next_step"], str) or not cp["next_step"].strip():
            raise ValueError("Each checkpoint needs one next_step")
        refs.extend(cp["source_ids"])
    if set(refs) - set(source_map):
        raise ValueError(f"Unknown source ids: {set(refs) - set(source_map)}")
    return scope, plan, sources, checkpoints, source_map


def render(scope, plan, sources, checkpoints, source_map, version):
    archive_prefix = "archive/" + scope["path"]
    def source_links(ids):
        return " · ".join(
            f'<a href="{esc(source_map[s]["url"])}">{esc(source_map[s]["title"])}</a>'
            for s in ids
        )

    def bullets(items):
        return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"

    current = plan["current"]
    areas = "".join(
        f'''<article class="area" id="area-{esc(a['id'])}">
        <div class="area-top"><span class="eyebrow">{index:02d}</span><span class="badge">{esc(a['status'])}</span></div>
        <h3>{esc(a['title'])}</h3><p>{esc(a['purpose'])}</p>
        <details open><summary>想弄懂的问题</summary><div class="questions">{bullets(a['questions'])}</div></details></article>'''
        for index, a in enumerate(plan["areas"], 1)
    )
    records = []
    for path, cp in reversed(checkpoints):
        open_items = bullets(cp["open_questions"]) if cp["open_questions"] else '<p class="quiet">本次没有另记未解问题；后续可补充。</p>'
        records.append(f'''<article class="checkpoint">
        <time datetime="{esc(cp['date'])}">{esc(cp['date'])}</time> <span class="badge">{'准备就绪 · 待学习' if cp['kind'] == 'setup' else '学习记录'}</span>
        <h3>{esc(cp['title'])}</h3>
        <h4>今天解决的问题</h4>{bullets(cp['resolved'])}
        <h4>理解证据 · 可修订观察</h4>{bullets(cp['evidence'])}
        <h4>尚未解决</h4>{open_items}
        <h4>一个下一步</h4><p>{esc(cp['next_step'])}</p>
        <p class="sources-inline">参考：{source_links(cp['source_ids'])}</p>
        <p class="source-note">{esc(cp.get('source_note', ''))}</p>
        <a class="archive-link" href="{esc(archive_prefix)}/checkpoints/{esc(path.name)}">查看这份记录的原文（JSON）</a></article>''')
    resources = "".join(
        f'''<div class="resource"><a href="{esc(s['url'])}">{esc(s['title'])}</a>
        <p>{esc(s['use'])}</p><span class="source-note">{'链接核实：' + esc(s['verified_at']) if s.get('verified_at') else '链接待核实；首次教学时检查原文'}</span></div>'''
        for s in sources
    )
    commit = version["commit"]
    version_label = {"github-pages": "Actions 构建", "branch-docs": "分支静态构建", "local": "本地预览"}[version["mode"]]
    source_label = commit[:12] if commit else "未提交"
    if version["dirty"]:
        version_label += "（含未提交更改）"
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="StudyScope：围绕真想弄懂的问题，逐步理解。当前领域、学习计划、停留点与整理记录。">
<meta name="color-scheme" content="light"><title>StudyScope · 一次弄懂一个问题</title><link rel="stylesheet" href="style.css"></head>
<body><a class="skip" href="#now">跳到正文</a>
<header class="topbar"><div class="shell bar"><a class="brand" href="#now">StudyScope<small>学习档案</small></a><nav aria-label="主要导航"><a href="#now">现在</a><a href="#plan">计划</a><a href="#footprints">足迹</a></nav></div></header>
<main class="shell"><div class="intro"><div><span class="eyebrow">从问题出发 · 对话式学习</span><h1>一次，弄懂一个问题。</h1><p>围绕真想弄懂的问题，逐步建立自己的理解。<br>在家教会话里学习，在这里找到停留点与走过的路。</p></div>
<aside class="direction"><span class="label">当前领域 · {esc(scope['title'])}</span><strong>{esc(plan['direction']['title'])}</strong><p>{esc(plan['direction']['note'])}</p><a href="{esc(source_map[plan['direction']['source_id']]['url'])}">查看本领域的方向资料 →</a></aside></div>
<section class="section" id="now" aria-labelledby="now-title"><div class="section-head"><h2 id="now-title"><span class="number">01</span>现在</h2><p>先从眼前的问题开始</p></div>
<div class="now"><article class="panel lead-panel"><span class="badge">{esc(current['state'])}</span><span class="label" style="margin-top:16px">建议的当前主题 · 可以改题</span><h3 class="topic">{esc(current['topic'])}</h3><div class="next"><span class="label">下一步</span>{esc(current['next_step'])}</div><p class="sources-inline">候选参考：{source_links(current['source_ids'])}</p></article>
<aside class="panel"><span class="label">上次停留</span><p>{esc(current['last_stop'])}</p><span class="label">我们的学习方式</span><p class="quiet">先听理解，再补关键缺口。学习方式由当前领域画像决定；卡住就直接教。</p><p><a class="archive-link" href="archive/agreement.md">通用学习约定 →</a></p><p><a class="archive-link" href="{esc(archive_prefix)}/profile.md">本领域画像 →</a></p><a class="archive-link" href="archive/scopes.json">当前领域索引 →</a></aside></div></section>
<section class="section" id="plan" aria-labelledby="plan-title"><div class="section-head"><h2 id="plan-title"><span class="number">02</span>计划</h2><p>粗粒度的问题地图 · 随讨论修订</p></div><p class="quiet">这些是想探索的问题，不是已学会的清单。状态来自学习观察，不以刷题次数或分数判断。</p><div class="map">{areas}</div><p class="archive-link"><a href="{esc(archive_prefix)}/map.json">查看当前问题地图原文（JSON）</a></p></section>
<section class="section" id="footprints" aria-labelledby="footprints-title"><div class="section-head"><h2 id="footprints-title"><span class="number">03</span>足迹</h2><p>只记录实际发生的学习，保留未解的问题</p></div><div class="footprints"><div>{''.join(records)}</div><aside class="resources"><h3>按需取用的资料</h3><p class="quiet">资料帮助回答问题，不构成全套必修。解释具体结论时再回到原始材料。</p>{resources}</aside></div></section></main>
<footer class="meta"><div class="shell"><div class="meta-row"><span>内容最后更新：<time datetime="{esc(version['updated_at'])}">{esc(version['updated_at'])}</time></span><span>内容版本：<a href="version.json"><code>{esc(version['content_version'][:12])}</code></a></span></div><p>{esc(version_label)} · 内容源提交：<code>{esc(source_label)}</code> · 构建时间：{esc(version['built_at'])}</p><p>公开的学习计划与整理记录。学习请回到专用家教会话。</p></div></footer></body></html>'''


def build():
    scope, plan, sources, checkpoints, source_map = read_archive()
    inputs = sorted((ROOT / "learning").rglob("*")) + [ROOT / "web/style.css", Path(__file__).resolve()]
    digest = hashlib.sha256()
    for path in inputs:
        if path.is_file():
            digest.update(path.relative_to(ROOT).as_posix().encode())
            digest.update(path.read_bytes())
    sha = os.environ.get("GITHUB_SHA") or os.environ.get("STUDYSCOPE_SOURCE_COMMIT") or git("rev-parse", "HEAD") or None
    if sha and not re.fullmatch(r"[0-9a-f]{40,64}", sha):
        raise ValueError("Invalid source commit SHA")
    version = {
        "schema_version": 1,
        "mode": "github-pages" if os.environ.get("GITHUB_ACTIONS") == "true" else ("branch-docs" if DIST.name == "docs" else "local"),
        "scope": scope["id"],
        "commit": sha,
        "dirty": bool(git("status", "--porcelain")),
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "updated_at": max([plan["updated_at"]] + [cp["date"] for _, cp in checkpoints]),
        "source_digest": digest.hexdigest(),
        "content_version": digest.hexdigest(),
    }
    # Delete only the known generated directory under this project, never a link.
    if DIST.is_symlink() or DIST.resolve().parent != ROOT or DIST.name not in {"dist", "docs"}:
        raise ValueError("Unsafe build target")
    if DIST.exists():
        if not (DIST / ".studyscope-generated").is_file() or any(p.is_symlink() for p in DIST.rglob("*")):
            raise ValueError("Refusing to replace an unrecognized or linked output directory")
        shutil.rmtree(DIST)
    DIST.mkdir()
    (DIST / ".studyscope-generated").write_text("StudyScope build output\n", encoding="utf-8")
    (DIST / ".nojekyll").touch()
    shutil.copytree(ROOT / "learning", DIST / "archive")
    shutil.copyfile(ROOT / "web/style.css", DIST / "style.css")
    (DIST / "index.html").write_text(render(scope, plan, sources, checkpoints, source_map, version), encoding="utf-8")
    (DIST / "version.json").write_text(json.dumps(version, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(DIST), "commit": sha, "checkpoints": len(checkpoints), "mode": version["mode"]}))


if __name__ == "__main__":
    build()
