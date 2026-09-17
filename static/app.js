/* gen-pdf visual editor: state -> preview DOM, inline editing, drag & drop. */
const $ = (s, r = document) => r.querySelector(s);
const sheet = $('#sheet'), panel = $('#panel'), toast = $('#toast');
const docTitle = $('#docTitle'), tplSelect = $('#tplSelect');

let doc = null;
let selectedId = null;
let history = [], future = [];
let focusSnapshot = null;

const uid = () => (crypto.randomUUID ? crypto.randomUUID().slice(0, 12) : String(Date.now() + Math.random()));
const snap = () => JSON.stringify(doc);
const saveLocal = (() => { let t; return () => { clearTimeout(t); t = setTimeout(() => { try { localStorage.setItem('genpdf.doc.v1', snap()); } catch {} }, 250); }; })();

function pushHistory() { history.push(snap()); if (history.length > 100) history.shift(); future = []; }
function toastMsg(m) { toast.textContent = m; toast.style.display = 'block'; clearTimeout(toastMsg.t); toastMsg.t = setTimeout(() => toast.style.display = 'none', 2200); }

async function api(path, body) {
  const r = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body ?? doc) });
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText);
  return r;
}

/* ---------- state helpers ---------- */
const byId = (id) => doc.blocks.find(b => b.id === id);
const idxOf = (id) => doc.blocks.findIndex(b => b.id === id);

function blankBlock(type) {
  const b = { id: uid(), type, align: 'left', level: 2, text: '', rows: [], items: [], entries: [], left: { name: '', role: '' }, right: { name: '', role: '' } };
  if (type === 'heading') b.text = 'New heading';
  if (type === 'paragraph') b.text = '';
  if (type === 'keyvalue') b.rows = [{ label: '', value: '' }];
  if (type === 'bullets') b.items = [''];
  if (type === 'sections') b.entries = [{ title: '', text: '' }];
  if (type === 'signatures') { b.left.role = 'Signer 1'; b.right.role = 'Signer 2'; }
  return b;
}

/* ---------- undo/redo ---------- */
function undo() { if (!history.length) return; future.push(snap()); doc = JSON.parse(history.pop()); if (!byId(selectedId)) selectedId = null; renderAll(); saveLocal(); }
function redo() { if (!future.length) return; history.push(snap()); doc = JSON.parse(future.pop()); renderAll(); saveLocal(); }

/* ---------- preview rendering ---------- */
function ed(text, ph) {
  const s = document.createElement('span');
  s.className = 'editable'; s.contentEditable = 'plaintext-only';
  s.dataset.ph = ph || 'Click to write…';
  s.textContent = text || '';
  return s;
}

function renderPreview() {
  sheet.innerHTML = '';
  const comp = document.createElement('div');
  comp.className = 'companyline editable'; comp.contentEditable = 'plaintext-only';
  comp.dataset.ph = 'Organization (optional)'; comp.textContent = doc.company_name || '';
  comp.addEventListener('input', () => { doc.company_name = comp.textContent; saveLocal(); });
  comp.addEventListener('focusin', () => { focusSnapshot = snap(); selectVisual(null); });
  comp.addEventListener('focusout', () => { if (focusSnapshot && focusSnapshot !== snap()) pushHistoryWith(focusSnapshot); focusSnapshot = null; });
  sheet.appendChild(comp);

  doc.blocks.forEach(b => sheet.appendChild(blockEl(b)));
}

function pushHistoryWith(oldSnap) { history.push(oldSnap); if (history.length > 100) history.shift(); future = []; }

function blockEl(b) {
  const w = document.createElement('div');
  w.className = 'block' + (b.id === selectedId ? ' selected' : '');
  w.dataset.id = b.id;
  const grip = document.createElement('span');
  grip.className = 'grip'; grip.textContent = '⠿'; grip.title = 'Drag to move'; grip.draggable = true;
  grip.addEventListener('dragstart', e => { e.dataTransfer.setData('text/plain', b.id); e.dataTransfer.effectAllowed = 'move'; });
  w.appendChild(grip);

  const body = document.createElement('div');
  body.style.textAlign = b.align || 'left';
  if (b.type === 'heading') {
    const h = document.createElement('h' + (b.level || 2));
    h.className = 'ph';
    const s = ed(b.text, 'Heading'); s.addEventListener('input', () => { b.text = s.textContent; saveLocal(); });
    h.appendChild(s); body.appendChild(h);
  } else if (b.type === 'paragraph') {
    const p = document.createElement('p'); p.className = 'ph';
    const s = ed(b.text, 'Write here…'); s.addEventListener('input', () => { b.text = s.textContent; saveLocal(); });
    p.appendChild(s); body.appendChild(p);
  } else if (b.type === 'keyvalue') {
    const kv = document.createElement('div'); kv.className = 'kv';
    (b.rows || []).forEach(r => {
      const lb = ed(r.label, 'Label'), vl = ed(r.value, 'Value');
      lb.style.fontWeight = '700';
      lb.addEventListener('input', () => { r.label = lb.textContent; saveLocal(); });
      vl.addEventListener('input', () => { r.value = vl.textContent; saveLocal(); });
      kv.appendChild(lb); kv.appendChild(vl);
    });
    body.appendChild(kv);
  } else if (b.type === 'bullets') {
    const ul = document.createElement('ul'); ul.className = 'bullets';
    (b.items || []).forEach((t, i) => {
      const li = document.createElement('li');
      const s = ed(t, 'Item'); s.addEventListener('input', () => { b.items[i] = s.textContent; saveLocal(); });
      li.appendChild(s); ul.appendChild(li);
    });
    body.appendChild(ul);
  } else if (b.type === 'sections') {
    (b.entries || []).forEach((e, i) => {
      const d = document.createElement('div'); d.className = 'secentry';
      const n = idxOf(b.id);
      const num = doc.blocks.slice(0, doc.blocks.indexOf(b)).filter(x => x.type === 'sections').reduce((a, x) => a + x.entries.length, 0) + i + 1;
      const t = ed(e.title, 'Section title'); t.style.fontWeight = '700';
      const x = ed(e.text, 'Description');
      t.addEventListener('input', () => { e.title = t.textContent; saveLocal(); });
      x.addEventListener('input', () => { e.text = x.textContent; saveLocal(); });
      d.append(String(num) + '. ', t, document.createElement('br'), x);
      body.appendChild(d);
      void n;
    });
  } else if (b.type === 'signatures') {
    const g = document.createElement('div'); g.className = 'sig';
    [['left', b.left], ['right', b.right]].forEach(([k, side]) => {
      const c = document.createElement('div');
      const nm = ed(side.name, 'Name'), rl = ed(side.role, 'Role'); rl.classList.add('role');
      nm.addEventListener('input', () => { side.name = nm.textContent; saveLocal(); });
      rl.addEventListener('input', () => { side.role = rl.textContent; saveLocal(); });
      c.append(Object.assign(document.createElement('div'), { className: 'line' }), nm, document.createElement('br'), rl);
      g.appendChild(c); void k;
    });
    body.appendChild(g);
  }
  w.appendChild(body);

  w.addEventListener('click', e => { if (!e.target.classList.contains('editable')) selectBlock(b.id); });
  w.addEventListener('focusin', e => {
    if (e.target.classList && e.target.classList.contains('editable')) {
      focusSnapshot = snap(); selectVisual(b.id);
    }
  });
  w.addEventListener('focusout', () => {
    setTimeout(() => { if (focusSnapshot && focusSnapshot !== snap()) pushHistoryWith(focusSnapshot); focusSnapshot = null; }, 0);
  });
  w.addEventListener('dragover', e => {
    e.preventDefault();
    const r = w.getBoundingClientRect();
    w.classList.toggle('dragover-top', e.clientY < r.top + r.height / 2);
    w.classList.toggle('dragover-bottom', e.clientY >= r.top + r.height / 2);
  });
  w.addEventListener('dragleave', () => w.classList.remove('dragover-top', 'dragover-bottom'));
  w.addEventListener('drop', e => {
    e.preventDefault();
    const id = e.dataTransfer.getData('text/plain');
    const top = w.classList.contains('dragover-top');
    w.classList.remove('dragover-top', 'dragover-bottom');
    if (id && id !== b.id) moveBlock(id, b.id, top);
  });
  return w;
}

function selectVisual(id) {
  selectedId = id;
  sheet.querySelectorAll('.block.selected').forEach(el => el.classList.remove('selected'));
  if (id) { const el = sheet.querySelector(`[data-id="${id}"]`); if (el) el.classList.add('selected'); }
}
function selectBlock(id) { selectedId = id; selectVisual(id); renderPanel(); }

function moveBlock(id, targetId, before) {
  const from = idxOf(id); if (from < 0) return;
  pushHistory();
  const [b] = doc.blocks.splice(from, 1);
  let to = idxOf(targetId) + (before ? 0 : 1);
  doc.blocks.splice(to, 0, b);
  selectedId = id; renderAll(); saveLocal();
}

/* ---------- property panel ---------- */
function field(label, value, onInput) {
  const l = document.createElement('label'); l.textContent = label;
  const i = document.createElement('input'); i.type = 'text'; i.value = value ?? '';
  i.addEventListener('input', () => onInput(i.value));
  panel.append(l, i);
}
function miniBtns(items) {
  const d = document.createElement('div'); d.className = 'mini';
  items.forEach(([t, fn, danger]) => { const b = document.createElement('button'); b.textContent = t; if (danger) b.className = 'danger'; b.onclick = fn; d.appendChild(b); });
  panel.appendChild(d);
}

function renderPanel() {
  panel.innerHTML = '';
  const h = document.createElement('h3'); h.textContent = 'Document'; panel.appendChild(h);
  field('Company (header/footer)', doc.company_name, v => { doc.company_name = v; renderPreview(); saveLocal(); });
  const lab = document.createElement('label'); lab.textContent = 'Options';
  const chk = document.createElement('div');
  chk.innerHTML = `<label style="display:flex;gap:6px;align-items:center"><input type="checkbox" id="pgn" ${doc.show_page_numbers ? 'checked' : ''} style="width:auto"> Page numbers</label>`;
  panel.append(lab, chk);
  chk.querySelector('#pgn').addEventListener('change', e => { pushHistory(); doc.show_page_numbers = e.target.checked; saveLocal(); });
  const hr = document.createElement('hr'); panel.appendChild(hr);

  const b = byId(selectedId);
  if (!b) { const p = document.createElement('p'); p.className = 'meta'; p.textContent = 'Select a block in the preview to edit its properties. Drag ⠿ to reorder.'; panel.appendChild(p); msgBox(); return; }

  const t = document.createElement('h3'); t.textContent = 'Block: ' + b.type; panel.appendChild(t);
  const l = document.createElement('label'); l.textContent = 'Alignment';
  const sel = document.createElement('select');
  ['left', 'center', 'right'].forEach(a => { const o = document.createElement('option'); o.value = a; o.textContent = a; if (b.align === a) o.selected = true; sel.appendChild(o); });
  sel.addEventListener('change', () => { pushHistory(); b.align = sel.value; renderAll(); saveLocal(); });
  panel.append(l, sel);

  if (b.type === 'heading') {
    const ll = document.createElement('label'); ll.textContent = 'Level';
    const ls = document.createElement('select');
    [1, 2, 3].forEach(n => { const o = document.createElement('option'); o.value = n; o.textContent = 'H' + n; if (b.level === n) o.selected = true; ls.appendChild(o); });
    ls.addEventListener('change', () => { pushHistory(); b.level = +ls.value; renderAll(); saveLocal(); });
    panel.append(ll, ls);
    field('Text', b.text, v => { b.text = v; renderPreview(); selectVisual(b.id); saveLocal(); });
  } else if (b.type === 'paragraph') {
    const ll = document.createElement('label'); ll.textContent = 'Text';
    const ta = document.createElement('textarea'); ta.rows = 4; ta.value = b.text || '';
    ta.addEventListener('input', () => { b.text = ta.value; renderPreview(); selectVisual(b.id); saveLocal(); });
    panel.append(ll, ta);
  } else if (b.type === 'keyvalue') {
    b.rows.forEach((r, i) => {
      const row = document.createElement('div'); row.className = 'row';
      const a = document.createElement('input'); a.type = 'text'; a.placeholder = 'Label'; a.value = r.label || '';
      const c = document.createElement('input'); c.type = 'text'; c.placeholder = 'Value'; c.value = r.value || '';
      const x = document.createElement('button'); x.textContent = '✕'; x.title = 'Remove row';
      x.onclick = () => { pushHistory(); b.rows.splice(i, 1); renderAll(); saveLocal(); };
      a.addEventListener('input', () => { r.label = a.value; renderPreview(); selectVisual(b.id); saveLocal(); });
      c.addEventListener('input', () => { r.value = c.value; renderPreview(); selectVisual(b.id); saveLocal(); });
      row.append(a, c, x); panel.appendChild(row);
    });
    miniBtns([['+ Add row', () => { pushHistory(); b.rows.push({ label: '', value: '' }); renderAll(); saveLocal(); }]]);
  } else if (b.type === 'bullets') {
    b.items.forEach((t, i) => {
      const row = document.createElement('div'); row.className = 'row';
      const a = document.createElement('input'); a.type = 'text'; a.value = t || '';
      const x = document.createElement('button'); x.textContent = '✕';
      x.onclick = () => { pushHistory(); b.items.splice(i, 1); renderAll(); saveLocal(); };
      a.addEventListener('input', () => { b.items[i] = a.value; renderPreview(); selectVisual(b.id); saveLocal(); });
      row.append(a, x); panel.appendChild(row);
    });
    miniBtns([['+ Add item', () => { pushHistory(); b.items.push(''); renderAll(); saveLocal(); }]]);
  } else if (b.type === 'sections') {
    b.entries.forEach((e, i) => {
      field(`Entry ${i + 1} title`, e.title, v => { e.title = v; renderPreview(); selectVisual(b.id); saveLocal(); });
      const ta = document.createElement('textarea'); ta.rows = 2; ta.value = e.text || '';
      ta.addEventListener('input', () => { e.text = ta.value; renderPreview(); selectVisual(b.id); saveLocal(); });
      panel.appendChild(ta);
      miniBtns([[`Remove entry ${i + 1}`, () => { pushHistory(); b.entries.splice(i, 1); renderAll(); saveLocal(); }, true]]);
    });
    miniBtns([['+ Add entry', () => { pushHistory(); b.entries.push({ title: '', text: '' }); renderAll(); saveLocal(); }]]);
  } else if (b.type === 'signatures') {
    field('Left name', b.left.name, v => { b.left.name = v; renderPreview(); selectVisual(b.id); saveLocal(); });
    field('Left role', b.left.role, v => { b.left.role = v; renderPreview(); selectVisual(b.id); saveLocal(); });
    field('Right name', b.right.name, v => { b.right.name = v; renderPreview(); selectVisual(b.id); saveLocal(); });
    field('Right role', b.right.role, v => { b.right.role = v; renderPreview(); selectVisual(b.id); saveLocal(); });
  }

  panel.appendChild(document.createElement('hr'));
  miniBtns([
    ['↑ Up', () => shiftBlock(b.id, -1)],
    ['↓ Down', () => shiftBlock(b.id, 1)],
    ['⧉ Duplicate', () => duplicateBlock(b.id)],
    ['✕ Delete', () => deleteBlock(b.id), true],
  ]);
  msgBox();
}

function msgBox() {
  let m = $('#msgs'); if (!m) { m = document.createElement('div'); m.id = 'msgs'; panel.appendChild(m); }
  return m;
}
async function showValidation() {
  const m = msgBox(); m.innerHTML = '';
  try {
    const v = await (await api('/api/documents/validate')).json();
    const d = document.createElement('div');
    d.className = v.ok ? 'ok' : 'err';
    d.textContent = (v.ok ? '✓ Valid' : '✕ ' + v.errores.join(' ')) + (v.avisos.length ? '\n! ' + v.avisos.join('\n! ') : '');
    m.appendChild(d);
    return v.ok;
  } catch (e) { m.innerHTML = '<span class="err">Validation failed: ' + e.message + '</span>'; return false; }
}

function shiftBlock(id, d) {
  const i = idxOf(id), j = i + d;
  if (i < 0 || j < 0 || j >= doc.blocks.length) return;
  pushHistory();
  [doc.blocks[i], doc.blocks[j]] = [doc.blocks[j], doc.blocks[i]];
  renderAll(); saveLocal();
}
function duplicateBlock(id) {
  const i = idxOf(id); if (i < 0) return;
  pushHistory();
  const c = JSON.parse(JSON.stringify(doc.blocks[i])); c.id = uid();
  doc.blocks.splice(i + 1, 0, c); selectedId = c.id; renderAll(); saveLocal();
}
function deleteBlock(id) {
  pushHistory();
  doc.blocks = doc.blocks.filter(x => x.id !== id);
  selectedId = null; renderAll(); saveLocal();
}

/* ---------- render all / load ---------- */
function renderAll() { docTitle.value = doc.title || ''; renderPreview(); renderPanel(); }

async function loadTemplate(id, keepHistory) {
  const t = await (await fetch('/api/templates/' + id)).json();
  if (!keepHistory && doc) pushHistory();
  doc = t; selectedId = null; history = keepHistory ? history : []; future = [];
  renderAll(); saveLocal();
}

async function exportPdf() {
  if (!(await showValidation())) { toastMsg('Fix errors before exporting'); return; }
  try {
    const r = await api('/api/documents/pdf');
    const blob = await r.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    const cd = r.headers.get('Content-Disposition') || '';
    a.download = (cd.split('filename=')[1] || 'document.pdf').replace(/"/g, '');
    a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 5000);
    toastMsg('PDF downloaded');
  } catch (e) { toastMsg('Export failed: ' + e.message); }
}

/* ---------- init ---------- */
async function init() {
  try {
    templates = await (await fetch('/api/templates')).json();
    tplSelect.innerHTML = '';
    templates.forEach(t => { const o = document.createElement('option'); o.value = t.id; o.textContent = t.name; tplSelect.appendChild(o); });
  } catch { toastMsg('Cannot reach API'); }

  const raw = localStorage.getItem('genpdf.doc.v1');
  if (raw) { try { const d = JSON.parse(raw); if (d && Array.isArray(d.blocks)) doc = d; } catch {} }
  if (!doc) {
    try { doc = await (await fetch('/api/templates/acta')).json(); }
    catch { doc = { title: 'Untitled', company_name: '', show_page_numbers: true, blocks: [] }; }
  }
  renderAll();

  docTitle.addEventListener('input', () => { doc.title = docTitle.value; saveLocal(); });
  docTitle.addEventListener('focusin', () => { focusSnapshot = snap(); });
  docTitle.addEventListener('focusout', () => { if (focusSnapshot && focusSnapshot !== snap()) pushHistoryWith(focusSnapshot); focusSnapshot = null; });

  document.querySelectorAll('#toolbar [data-add]').forEach(btn => btn.addEventListener('click', () => {
    pushHistory();
    const b = blankBlock(btn.dataset.add);
    doc.blocks.push(b); selectedId = b.id; renderAll(); saveLocal(); toastMsg('Block added');
  }));

  $('#btnTpl').onclick = () => loadTemplate(tplSelect.value || 'blank');
  $('#btnPdf').onclick = exportPdf;
  $('#btnUndo').onclick = undo; $('#btnRedo').onclick = redo;
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z' && !e.shiftKey) { e.preventDefault(); undo(); }
    if ((e.ctrlKey || e.metaKey) && (e.key.toLowerCase() === 'y' || (e.key.toLowerCase() === 'z' && e.shiftKey))) { e.preventDefault(); redo(); }
  });
  sheet.addEventListener('dragover', e => { if (e.target === sheet) e.preventDefault(); });
  sheet.addEventListener('drop', e => {
    if (e.target !== sheet) return;
    e.preventDefault();
    const id = e.dataTransfer.getData('text/plain');
    if (id && idxOf(id) >= 0) { pushHistory(); const [b] = doc.blocks.splice(idxOf(id), 1); doc.blocks.push(b); renderAll(); saveLocal(); }
  });
}
init();
