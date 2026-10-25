// A small, safe Markdown subset; note text is never inserted as HTML.
function appendInline(parent, text, sourceUrl) {
  const pattern = /`([^`]+)`|\*\*([^*]+)\*\*|\[([^\]]+)\]\(([^\s)]+)\)/g;
  let offset = 0;
  for (const match of text.matchAll(pattern)) {
    parent.append(document.createTextNode(text.slice(offset, match.index)));
    if (match[1] != null || match[2] != null) {
      const element = document.createElement(match[1] != null ? 'code' : 'strong');
      element.textContent = match[1] ?? match[2];
      parent.append(element);
    } else {
      let url;
      try { url = new URL(match[4], sourceUrl); } catch { url = null; }
      if (url && ['http:', 'https:'].includes(url.protocol)) {
        const link = document.createElement('a');
        link.href = url.href;
        link.textContent = match[3];
        if (url.origin !== location.origin) { link.target = '_blank'; link.rel = 'noopener noreferrer'; }
        parent.append(link);
      } else parent.append(document.createTextNode(match[3]));
    }
    offset = match.index + match[0].length;
  }
  parent.append(document.createTextNode(text.slice(offset)));
}

function renderMarkdown(container, markdown, sourceUrl, title) {
  const lines = markdown.replace(/\r\n?/g, '\n').split('\n');
  const output = document.createDocumentFragment();
  let i = 0;
  let firstContent = true;
  const isBlock = line => /^(#{1,4})\s|^\s*```|^\s*[-*]\s|^\s*\d+\.\s|^>\s?/.test(line);
  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim()) { i++; continue; }
    const heading = line.match(/^(#{1,4})\s+(.+)$/);
    if (heading) {
      if (!(firstContent && heading[1] === '#' && heading[2].trim() === title)) {
        const element = document.createElement('h' + Math.min(4, heading[1].length + 1));
        appendInline(element, heading[2], sourceUrl);
        output.append(element);
      }
      i++;
    } else if (/^\s*```/.test(line)) {
      const codeLines = [];
      for (i++; i < lines.length && !/^\s*```/.test(lines[i]); i++) codeLines.push(lines[i]);
      const pre = document.createElement('pre');
      const code = document.createElement('code');
      code.textContent = codeLines.join('\n');
      pre.append(code);
      output.append(pre);
      if (i < lines.length) i++;
    } else if (/^\s*[-*]\s/.test(line) || /^\s*\d+\.\s/.test(line)) {
      const ordered = /^\s*\d+\.\s/.test(line);
      const list = document.createElement(ordered ? 'ol' : 'ul');
      const itemPattern = ordered ? /^\s*\d+\.\s+(.*)$/ : /^\s*[-*]\s+(.*)$/;
      while (i < lines.length) {
        const item = lines[i].match(itemPattern);
        if (!item) break;
        const element = document.createElement('li');
        appendInline(element, item[1], sourceUrl);
        list.append(element);
        i++;
      }
      output.append(list);
    } else if (/^>\s?/.test(line)) {
      const quoteLines = [];
      while (i < lines.length && /^>\s?/.test(lines[i])) quoteLines.push(lines[i++].replace(/^>\s?/, ''));
      const quote = document.createElement('blockquote');
      appendInline(quote, quoteLines.join(' '), sourceUrl);
      output.append(quote);
    } else {
      const paragraphLines = [line];
      for (i++; i < lines.length && lines[i].trim() && !isBlock(lines[i]); i++) paragraphLines.push(lines[i]);
      const paragraph = document.createElement('p');
      appendInline(paragraph, paragraphLines.join(' '), sourceUrl);
      output.append(paragraph);
    }
    firstContent = false;
  }
  container.replaceChildren(output);
}

export function createNotebook(catalogUrl) {
  const empty = document.getElementById('notes-empty');
  const layout = document.getElementById('notes-layout');
  const list = document.getElementById('note-list');
  const title = document.getElementById('note-title');
  const date = document.getElementById('note-date');
  const body = document.getElementById('note-body');
  const error = document.getElementById('notes-error');
  const explorerToggle = document.getElementById('toggle-notes');
  let scope = null;
  let notes = new Map();
  let targets = new Map();
  let requestNumber = 0;

  explorerToggle.addEventListener('click', () => {
    const collapsed = layout.classList.toggle('notebook-collapsed');
    list.hidden = collapsed;
    explorerToggle.setAttribute('aria-expanded', String(!collapsed));
    explorerToggle.setAttribute('aria-label', collapsed ? '展开笔记目录' : '收起笔记目录');
    explorerToggle.title = collapsed ? '展开笔记目录' : '收起笔记目录';
  });

  function setNodeExpanded(button, expanded) {
    document.getElementById(button.getAttribute('aria-controls')).hidden = !expanded;
    button.setAttribute('aria-expanded', String(expanded));
    button.setAttribute('aria-label', (expanded ? '收起子笔记：' : '展开子笔记：') + button.dataset.noteTitle);
  }

  function setScope(nextScope, index, path) {
    requestNumber++;
    scope = nextScope;
    targets = new Map([['scope/' + scope.id, scope.label || scope.title]]);
    for (const [index, stage] of path.stages.entries()) {
      targets.set('stage/' + stage.id, 'Stage ' + (index + 1) + ' · ' + stage.title);
      for (const topic of stage.topics) targets.set('topic/' + topic.id, topic.title);
    }
    const byKey = new Map(index.notes.map(note => [note.level + '/' + note.target_id, note]));
    const orderedKeys = ['scope/' + scope.id, ...path.stages.map(stage => 'stage/' + stage.id), ...path.stages.flatMap(stage => stage.topics.map(topic => 'topic/' + topic.id))];
    notes = new Map(orderedKeys.filter(key => byKey.has(key)).map(key => [key, byKey.get(key)]));
    empty.hidden = notes.size !== 0;
    layout.hidden = notes.size === 0;
    error.hidden = true;
    document.getElementById('notes-panel').setAttribute('aria-busy', 'false');
    title.textContent = '';
    date.textContent = '';
    body.replaceChildren();
    list.replaceChildren();
    function icon(kind) {
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('viewBox', '0 0 20 20');
      svg.setAttribute('aria-hidden', 'true');
      svg.setAttribute('class', kind === 'caret' ? 'note-caret' : 'note-icon');
      const shape = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      shape.setAttribute('d', kind === 'caret' ? 'M7 4l6 6-6 6' : 'M5 2h7l4 4v12H5zM12 2v5h4M8 11h5M8 14h5');
      svg.append(shape);
      return svg;
    }
    function noteNode(key, childNodes = []) {
      const note = notes.get(key);
      const name = note?.title || targets.get(key);
      const item = document.createElement('li');
      const row = document.createElement('div');
      row.className = 'note-node-row';
      item.append(row);
      if (childNodes.length) {
        const children = document.createElement('ul');
        children.className = 'note-children';
        children.id = 'note-children-' + key.replace('/', '-');
        children.append(...childNodes);
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'note-disclosure';
        button.dataset.noteTitle = name;
        button.setAttribute('aria-controls', children.id);
        button.setAttribute('aria-expanded', 'true');
        button.setAttribute('aria-label', '收起子笔记：' + name);
        button.append(icon('caret'));
        button.addEventListener('click', () => setNodeExpanded(button, button.getAttribute('aria-expanded') !== 'true'));
        row.append(button);
        item.append(children);
      } else {
        const spacer = document.createElement('span');
        spacer.className = 'note-toggle-spacer';
        spacer.setAttribute('aria-hidden', 'true');
        row.append(spacer);
      }
      const link = document.createElement(note ? 'a' : 'span');
      link.className = 'note-link';
      if (note) {
        link.href = '#notes/' + key.split('/').map(encodeURIComponent).join('/');
        link.dataset.noteKey = key;
      }
      link.title = name;
      const label = document.createElement('span');
      label.className = 'note-name';
      label.textContent = name;
      link.append(icon('note'), label);
      row.append(link);
      return item;
    }
    const tree = document.createElement('ul');
    tree.className = 'note-tree';
    const stageNodes = [];
    for (const stage of path.stages) {
      const topicNotes = stage.topics.filter(topic => notes.has('topic/' + topic.id));
      if (!notes.has('stage/' + stage.id) && !topicNotes.length) continue;
      stageNodes.push(noteNode('stage/' + stage.id, topicNotes.map(topic => noteNode('topic/' + topic.id))));
    }
    tree.append(noteNode('scope/' + scope.id, stageNodes));
    list.append(tree);
  }

  async function open(noteKey = null) {
    const request = ++requestNumber;
    error.hidden = true;
    document.getElementById('notes-panel').setAttribute('aria-busy', 'false');
    if (!notes.size) {
      if (noteKey) { error.textContent = '没有找到这篇学习笔记。'; error.hidden = false; }
      return;
    }
    const key = noteKey || notes.keys().next().value;
    const note = notes.get(key);
    body.replaceChildren();
    title.textContent = '';
    date.textContent = '';
    if (!note) { error.textContent = '没有找到这篇学习笔记。'; error.hidden = false; return; }
    for (const link of list.querySelectorAll('a')) {
      if (link.dataset.noteKey === key) {
        link.setAttribute('aria-current', 'page');
        link.parentElement.classList.add('selected');
        for (let ancestor = link.parentElement; ancestor && ancestor !== list; ancestor = ancestor.parentElement) {
          if (ancestor.classList.contains('note-children')) setNodeExpanded(ancestor.previousElementSibling.querySelector('.note-disclosure'), true);
        }
      }
      else {
        link.removeAttribute('aria-current');
        link.parentElement.classList.remove('selected');
      }
    }
    title.textContent = note.title || targets.get(key);
    document.getElementById('note-context').textContent = { scope: 'Scope 笔记', stage: 'Stage 笔记', topic: 'Topic 笔记' }[note.level] + ' · ' + targets.get(key);
    date.hidden = !note.updated_at;
    if (note.updated_at) { date.dateTime = note.updated_at; date.textContent = '更新于 ' + note.updated_at; }
    const url = new URL(scope.path + '/notes/' + note.file, catalogUrl);
    document.getElementById('notes-panel').setAttribute('aria-busy', 'true');
    try {
      const response = await fetch(url, { cache: 'no-store' });
      if (!response.ok) throw new Error('笔记文件暂时无法读取');
      const markdown = await response.text();
      if (request !== requestNumber) return;
      renderMarkdown(body, markdown, url, title.textContent);
    } catch (problem) {
      if (request !== requestNumber) return;
      error.textContent = problem.message;
      error.hidden = false;
    } finally {
      if (request === requestNumber) document.getElementById('notes-panel').setAttribute('aria-busy', 'false');
    }
  }

  return { setScope, open, has: (level, id) => notes.has(level + '/' + id) };
}
