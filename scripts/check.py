"""Check the current archive, built files, and relative asset paths."""
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
import json
from build import ROOT, DIST, load, source_files, create_version


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.assets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'script' and attrs.get('src'):
            self.assets.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') == 'stylesheet':
            self.assets.append(attrs['href'])


def check():
    catalog = load(ROOT / 'learning/scopes.json')
    assert catalog['active_scope'] in {scope['id'] for scope in catalog['scopes']}
    topic_count = 0
    note_count = 0
    for scope in catalog['scopes']:
        base = ROOT / 'learning' / scope['path']
        plan = load(base / 'path.json')
        topics = [topic for stage in plan['stages'] for topic in stage['topics']]
        topic_ids = {topic['id'] for topic in topics}
        stage_ids = {stage['id'] for stage in plan['stages']}
        assert len(topic_ids) == len(topics) and len(stage_ids) == len(plan['stages'])
        assert plan['current_topic'] is None or plan['current_topic'] in topic_ids
        targets = {'scope': {scope['id']}, 'stage': stage_ids, 'topic': topic_ids}
        notes = load(base / 'notes/index.json')['notes']
        keys = {(note['level'], note['target_id']) for note in notes}
        assert len(keys) == len(notes)
        for note in notes:
            assert note['target_id'] in targets[note['level']]
            assert (base / 'notes' / note['file']).is_file()
        assert {topic['id'] for topic in topics if topic['status'] == 'completed'} <= {note['target_id'] for note in notes if note['level'] == 'topic'}
        topic_count += len(topics)
        note_count += len(notes)
    for path in source_files():
        relative = path.relative_to(ROOT)
        destination = DIST / (relative.relative_to('web') if relative.parts[0] == 'web' else relative)
        assert destination.read_bytes() == path.read_bytes(), str(relative)
    page = Page()
    page.feed((DIST / 'index.html').read_text(encoding='utf-8'))
    assert len(page.ids) == len(set(page.ids))
    for asset in page.assets:
        assert not urlparse(asset).scheme and not asset.startswith('/')
        assert (DIST / asset).is_file()
        assert urlparse(urljoin('https://example.invalid/StudyScope/', asset)).path.startswith('/StudyScope/')
    assert (DIST / 'notes.js').is_file()
    version = load(DIST / 'version.json')
    assert version['content_version'] == create_version()['content_version']
    print(json.dumps({'passed': True, 'scopes': len(catalog['scopes']), 'topics': topic_count, 'notes': note_count, 'version': version['content_version'][:12]}))


if __name__ == '__main__':
    check()
