import { createNotebook } from './notes.js';

const layout = document.getElementById('layout');
const toggle = document.getElementById('toggle-sidebar');
const scopeList = document.getElementById('scope-list');
const graph = document.getElementById('path-graph');
const errorMessage = document.getElementById('load-error');
const version = await readJson(new URL('version.json', document.baseURI));
const catalogUrl = new URL('learning/scopes.json', document.baseURI);
const svgNamespace = 'http://www.w3.org/2000/svg';
const nodeElements = new Map();
const stageElements = new Map();
const notebook = createNotebook(catalogUrl);
const contentTabs = [...document.querySelectorAll('.content-tab')];
let pathDescription = null;
let connectionSvg = null;
let connectionPaths = null;
let loadNumber = 0;

function setCollapsed(collapsed) {
  layout.classList.toggle('collapsed', collapsed);
  toggle.setAttribute('aria-expanded', String(!collapsed));
  toggle.setAttribute('aria-label', collapsed ? '展开侧边栏' : '收起侧边栏');
  toggle.title = collapsed ? '展开侧边栏' : '收起侧边栏';
  requestAnimationFrame(drawConnections);
}

async function readJson(url) {
  const response = await fetch(url, { cache: 'no-store' });
  if (!response.ok) throw new Error('无法读取 ' + url.pathname);
  return response.json();
}

function svgElement(tag, attributes = {}) {
  const element = document.createElementNS(svgNamespace, tag);
  for (const [name, value] of Object.entries(attributes)) element.setAttribute(name, value);
  return element;
}

function createConnectionLayer() {
  connectionSvg = svgElement('svg', { class: 'connections', 'aria-hidden': 'true' });
  const defs = svgElement('defs');
  const marker = svgElement('marker', {
    id: 'arrow', viewBox: '0 0 8 8', refX: '7', refY: '4', markerWidth: '6', markerHeight: '6', orient: 'auto'
  });
  marker.append(svgElement('path', { d: 'M1 1l5 3-5 3', fill: 'none', stroke: '#bdc6d0', 'stroke-width': '1.25' }));
  defs.append(marker);
  connectionPaths = svgElement('g', { id: 'connection-paths' });
  connectionSvg.append(defs, connectionPaths);
  return connectionSvg;
}

function renderPath(description) {
  pathDescription = description;
  nodeElements.clear();
  stageElements.clear();
  const elements = [createConnectionLayer()];
  for (const [index, stage] of description.stages.entries()) {
    const group = document.createElement('section');
    group.className = 'stage-group';
    group.id = 'stage-' + stage.id;
    group.dataset.empty = String(stage.topics.length === 0);
    group.setAttribute('aria-labelledby', 'stage-title-' + stage.id);
    const heading = document.createElement('h2');
    heading.id = 'stage-title-' + stage.id;
    heading.className = 'stage-title';
    const stageTitle = 'Stage ' + (index + 1) + ' · ' + stage.title;
    if (notebook.has('stage', stage.id)) {
      const link = document.createElement('a');
      link.href = '#notes/stage/' + encodeURIComponent(stage.id);
      link.textContent = stageTitle;
      link.setAttribute('aria-label', stageTitle + '，查看阶段笔记');
      heading.append(link);
    } else heading.textContent = stageTitle;
    group.append(heading);
    const grid = document.createElement('div');
    grid.className = 'topic-grid';
    group.append(grid);
    if (!stage.topics.length) {
      const placeholder = document.createElement('p');
      placeholder.className = 'stage-empty';
      placeholder.textContent = '下个阶段 · Topic 待展开';
      grid.append(placeholder);
    }
    for (const node of stage.topics) {
      const linksToNote = node.status === 'completed' && notebook.has('topic', node.id);
      const element = document.createElement(linksToNote ? 'a' : 'article');
      if (linksToNote) {
        element.href = '#notes/topic/' + encodeURIComponent(node.id);
        element.setAttribute('aria-label', node.title + '，查看学习笔记');
      }
      element.id = 'topic-' + node.id;
      element.dataset.topicId = node.id;
      element.className = 'topic';
      if (node.status === 'completed') element.classList.add('completed');
      if (node.id === description.current_topic) {
        element.classList.add('current');
        element.setAttribute('aria-current', 'step');
        const marker = document.createElement('span');
        marker.className = 'current-marker';
        marker.textContent = '当前位置';
        element.append(marker);
      }
      const title = document.createElement('h3');
      title.textContent = node.title;
      element.append(title);
      if (node.summary?.length) {
        const summary = document.createElement('p');
        node.summary.forEach((line, index) => {
          if (index) summary.append(document.createElement('br'));
          summary.append(document.createTextNode(line));
        });
        element.append(summary);
      }
      if (node.status === 'completed') {
        const status = document.createElement('span');
        status.className = 'completion-label';
        status.textContent = '✓ 已完成';
        element.append(status);
      }
      nodeElements.set(node.id, element);
      grid.append(element);
    }
    stageElements.set(stage.id, group);
    elements.push(group);
  }
  graph.replaceChildren(...elements);
  drawConnections();
}

function drawConnections() {
  if (!pathDescription || !connectionSvg) return;
  const bounds = graph.getBoundingClientRect();
  if (!bounds.width || !bounds.height) return;
  connectionSvg.setAttribute('viewBox', '0 0 ' + bounds.width + ' ' + bounds.height);
  connectionPaths.replaceChildren();
  const edges = pathDescription.stages.flatMap(stage => stage.topics.slice(1).map((topic, index) => ({ from: stage.topics[index].id, to: topic.id })));
  for (const edge of edges) {
    const a = nodeElements.get(edge.from).getBoundingClientRect();
    const b = nodeElements.get(edge.to).getBoundingClientRect();
    const sameRow = Math.abs(a.top - b.top) < 10;
    let d;
    if (sameRow) {
      const forward = b.left > a.left;
      const x1 = (forward ? a.right : a.left) - bounds.left;
      const x2 = (forward ? b.left : b.right) - bounds.left;
      d = 'M ' + x1 + ' ' + (a.top + a.height / 2 - bounds.top) + ' L ' + x2 + ' ' + (b.top + b.height / 2 - bounds.top);
    } else {
      const down = b.top > a.top;
      const x1 = a.left + a.width / 2 - bounds.left;
      const x2 = b.left + b.width / 2 - bounds.left;
      const y1 = (down ? a.bottom : a.top) - bounds.top;
      const y2 = (down ? b.top : b.bottom) - bounds.top;
      const midY = (y1 + y2) / 2;
      d = 'M ' + x1 + ' ' + y1 + ' V ' + midY + ' H ' + x2 + ' V ' + y2;
    }
    connectionPaths.append(svgElement('path', { d, class: 'connection', 'marker-end': 'url(#arrow)', 'data-from': edge.from, 'data-to': edge.to }));
  }
  for (let index = 1; index < pathDescription.stages.length; index++) {
    const from = pathDescription.stages[index - 1].id;
    const to = pathDescription.stages[index].id;
    const a = stageElements.get(from).getBoundingClientRect();
    const b = stageElements.get(to).getBoundingClientRect();
    const x = a.left + a.width / 2 - bounds.left;
    const d = 'M ' + x + ' ' + (a.bottom - bounds.top) + ' V ' + (b.top - bounds.top);
    connectionPaths.append(svgElement('path', { d, class: 'connection stage-connection', 'marker-end': 'url(#arrow)', 'data-from': from, 'data-to': to }));
  }
}

function showContentTab(id) {
  for (const tab of contentTabs) {
    const selected = tab.id === id;
    tab.setAttribute('aria-selected', String(selected));
    tab.tabIndex = selected ? 0 : -1;
    document.getElementById(tab.getAttribute('aria-controls')).hidden = !selected;
  }
  if (id === 'path-tab') requestAnimationFrame(drawConnections);
}

function applyRoute() {
  if (!pathDescription) return;
  if (location.hash === '#notes' || location.hash.startsWith('#notes/')) {
    showContentTab('notes-tab');
    let key = null;
    try { key = location.hash.startsWith('#notes/') ? location.hash.slice(7).split('/').map(decodeURIComponent).join('/') : null; }
    catch { key = '__invalid__'; }
    notebook.open(key);
  } else showContentTab('path-tab');
}

function navigateToTab(id) {
  const hash = id === 'notes-tab' ? '#notes' : '#path';
  if (location.hash === hash) applyRoute();
  else location.hash = hash;
}

async function loadScope(scope) {
  const request = ++loadNumber;
  document.getElementById('scope-title').textContent = scope.label || scope.title;
  graph.setAttribute('aria-label', (scope.label || scope.title) + ' 学习路径');
  document.getElementById('path-panel').setAttribute('aria-busy', 'true');
  for (const button of scopeList.children) button.setAttribute('aria-current', String(button.dataset.scopeId === scope.id));
  errorMessage.hidden = true;
  try {
    const [description, notesIndex] = await Promise.all([
      readJson(new URL(scope.path + '/path.json', catalogUrl)),
      readJson(new URL(scope.path + '/notes/index.json', catalogUrl))
    ]);
    if (request !== loadNumber) return;
    notebook.setScope(scope, notesIndex, description);
    graph.hidden = false;
    renderPath(description);
    applyRoute();
  } catch (error) {
    if (request !== loadNumber) return;
    graph.hidden = true;
    errorMessage.textContent = '无法加载学习路径：' + error.message;
    errorMessage.hidden = false;
  } finally {
    if (request === loadNumber) document.getElementById('path-panel').setAttribute('aria-busy', 'false');
  }
}

async function initializeScopes() {
  const catalog = await readJson(catalogUrl);
  for (const scope of catalog.scopes) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'scope-option';
    button.dataset.scopeId = scope.id;
    const fullLabel = document.createElement('span');
    fullLabel.className = 'scope-full-label';
    fullLabel.textContent = scope.label || scope.title;
    const shortLabel = document.createElement('span');
    shortLabel.className = 'scope-short-label';
    shortLabel.textContent = scope.short_label || scope.label || scope.title;
    button.append(fullLabel, shortLabel);
    button.setAttribute('aria-label', scope.label || scope.title);
    button.title = scope.title;
    button.addEventListener('click', () => {
      history.replaceState(null, '', '#path');
      loadScope(scope);
    });
    scopeList.append(button);
  }
  const active = catalog.scopes.find(scope => scope.id === catalog.active_scope);
  await loadScope(active);
}

for (const tab of contentTabs) {
  tab.addEventListener('click', () => navigateToTab(tab.id));
  tab.addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const current = contentTabs.indexOf(tab);
    const next = event.key === 'Home' ? 0 : event.key === 'End' ? contentTabs.length - 1 :
      (current + (event.key === 'ArrowRight' ? 1 : -1) + contentTabs.length) % contentTabs.length;
    navigateToTab(contentTabs[next].id);
    contentTabs[next].focus();
  });
}
window.addEventListener('hashchange', applyRoute);
toggle.addEventListener('click', () => setCollapsed(!layout.classList.contains('collapsed')));
document.getElementById('drawer-shade').addEventListener('click', () => setCollapsed(true));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && matchMedia('(max-width: 720px)').matches) setCollapsed(true);
});
setCollapsed(matchMedia('(max-width: 720px)').matches);
document.getElementById('page-version').textContent = version.content_version.slice(0, 12);
document.getElementById('run-mode').textContent = { preview: '本地预览', local: '本地构建', 'github-pages': 'GitHub Pages' }[version.mode];
document.getElementById('content-updated').textContent = version.updated_at;
document.getElementById('source-commit').textContent = (version.commit?.slice(0, 7) || '无 Git 提交') + (version.dirty ? ' *' : '');
new ResizeObserver(drawConnections).observe(graph);
initializeScopes().catch(error => {
  errorMessage.textContent = '无法加载 Scope：' + error.message;
  errorMessage.hidden = false;
});
