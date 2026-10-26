"""Copy the official page and learning archive into dist/."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def git(*args):
    result = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ''


def source_files():
    return sorted(
        (p for directory in ['web', 'learning'] for p in (ROOT / directory).rglob('*') if p.is_file()),
        key=lambda p: p.relative_to(ROOT).as_posix(),
    )


def create_version(mode=None):
    digest = hashlib.sha256()
    dates = []
    for path in source_files():
        digest.update(path.relative_to(ROOT).as_posix().encode())
        digest.update(path.read_bytes())
        if path.suffix == '.json':
            data = load(path)
            if isinstance(data, dict):
                dates.extend(data[key] for key in ['updated_at', 'date'] if data.get(key))
                dates.extend(note['updated_at'] for note in data.get('notes', []) if note.get('updated_at'))
    return {
        'content_version': digest.hexdigest(),
        'commit': os.environ.get('GITHUB_SHA') or git('rev-parse', 'HEAD') or None,
        'dirty': bool(git('status', '--porcelain')),
        'updated_at': max(dates),
        'built_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'mode': mode or ('github-pages' if os.environ.get('GITHUB_ACTIONS') == 'true' else 'local'),
    }


def build():
    # dist is the only disposable output directory.
    if DIST.resolve() != ROOT.resolve() / 'dist':
        raise ValueError('Build output must stay inside this project')
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / 'web', DIST)
    shutil.copytree(ROOT / 'learning', DIST / 'learning')
    (DIST / '.nojekyll').touch()
    version = create_version()
    (DIST / 'version.json').write_text(json.dumps(version, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(DIST), 'version': version['content_version'][:12], 'commit': version['commit']}))


if __name__ == '__main__':
    build()
