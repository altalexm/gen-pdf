/* gen-pdf editor: shell, slash-menu, palette, library, history, comments, i18n. */
const $ = (s, r = document) => r.querySelector(s);
const sheet = $('#sheet'), panel = $('#panel');
const docTitle = $('#docTitle'), tplSelect = $('#tplSelect');

/* ================= i18n ================= */
const I18N = {
  en: { docTitlePh: 'Document title', newBtn: 'New', saveBtn: 'Save', exportPdf: 'Export PDF', vEditor: 'Edit', vLibrary: 'Docs', addLabel: 'Add:', bText: 'Text', bKv: 'Key-values', bBullets: 'Bullets', formatLabel: 'Format:', zoomLabel: 'Zoom:', hint: 'Click any text to edit it · type / for blocks · drag ⠿ to move · Ctrl+K for actions', emptyDoc: 'Empty document — add your first block above, or pick a template.', libraryTitle: 'Library', searchPh: 'Search…', newDoc: '+ New document', tplGallery: 'Templates', docsTitle: 'Documents', blockDoc: 'Document', company: 'Company (header/footer)', options: 'Options', pageNumbers: 'Page numbers', size: 'Size', orientation: 'Orientation', portrait: 'Portrait', landscape: 'Landscape', margin: 'Margin (mm)', tags: 'Tags (comma separated)', favorite: 'Favorite', status: 'Status', selHint: 'Select a block in the preview to edit its properties. Drag ⠿ to reorder.', block: 'Block', convertTo: 'Convert to', alignment: 'Alignment', level: 'Level', text: 'Text', addRow: '+ Add row', addItem: '+ Add item', addEntry: '+ Add entry', addCol: '+ Column', removeEntry: 'Remove entry', up: '↑ Up', down: '↓ Down', dup: '⧉ Duplicate', del: '✕ Delete', color: 'Color', headers: 'Headers (| separated)', addRowT: '+ Row', src: 'Image URL (or upload below)', upload: 'Upload image…', width: 'Width %', caption: 'Caption', open: 'Open', duplicate: 'Duplicate', delete: 'Delete', restore: 'Restore', purge: 'Delete forever', saved: 'Saved to library', savedAt: 'Saved', editing: 'Editing…', loaded: 'Document loaded', exported: 'Downloaded', fixFirst: 'Fix errors before exporting', noDocs: 'No documents here.', blocksN: 'blocks', wordsN: 'words', pagesN: 'pages', templateLoaded: 'Template loaded', imported: 'Imported', confirmDel: 'Move to trash?', confirmPurge: 'Delete forever? This cannot be undone.', palettePh: 'Type a command…', theme: 'Theme', language: 'Language', undo: 'Undo', redo: 'Redo', save: 'Save to library', export: 'Export', goEditor: 'Go to editor', goLibrary: 'Go to library', validate: 'Validate now', zoomIn: 'Zoom in', zoomOut: 'Zoom out', zoomReset: 'Reset zoom', newFrom: 'New from template', shortcuts: 'Keyboard shortcuts', close: 'Close', history: 'History', comments: 'Comments', addComment: 'Add comment', yourName: 'Your name', writeComment: 'Write a comment…', resolve: 'Resolve', reopen: 'Reopen', noComments: 'No comments yet.', needSave: 'Save the document to the library first to use comments.', signHere: 'Sign here', drawLeft: 'Draw left signature', drawRight: 'Draw right signature', clearDrawing: 'Remove drawing', tplNamePh: 'Template name…', tplDescPh: 'Description…', saveTpl: 'Save current as template', tplSaved: 'Template saved', tplDeleted: 'Template deleted', confirmTplDel: 'Delete this template?', varsTitle: 'Fill in the values', createDoc: 'Create document', trashTitle: 'Trash', backToDocs: 'Back to documents', print: 'Print (browser)', findVersions: 'Versions', diffVsCurrent: 'Diff vs current', restoreVersion: 'Restore this version', restored: 'Version restored', depth: 'Depth', allTags: '🏷 All tags', allStates: 'All states', draft: 'Draft', in_review: 'In review', approved: 'Approved', favOnly: 'Favorites only', emptyTrash: 'Trash is empty.' },
  es: { docTitlePh: 'Título del documento', newBtn: 'Nuevo', saveBtn: 'Guardar', exportPdf: 'Exportar PDF', vEditor: 'Editar', vLibrary: 'Docs', addLabel: 'Añadir:', bText: 'Texto', bKv: 'Claves', bBullets: 'Viñetas', formatLabel: 'Formato:', zoomLabel: 'Zoom:', hint: 'Clic en cualquier texto para editar · escribe / para bloques · arrastra ⠿ para mover · Ctrl+K para acciones', emptyDoc: 'Documento vacío — añade tu primer bloque arriba o elige una plantilla.', libraryTitle: 'Biblioteca', searchPh: 'Buscar…', newDoc: '+ Nuevo documento', tplGallery: 'Plantillas', docsTitle: 'Documentos', blockDoc: 'Documento', company: 'Organización (cabecera/pie)', options: 'Opciones', pageNumbers: 'Números de página', size: 'Tamaño', orientation: 'Orientación', portrait: 'Vertical', landscape: 'Horizontal', margin: 'Margen (mm)', tags: 'Etiquetas (separadas por comas)', favorite: 'Favorito', status: 'Estado', selHint: 'Selecciona un bloque en la vista previa. Arrastra ⠿ para reordenar.', block: 'Bloque', convertTo: 'Convertir a', alignment: 'Alineación', level: 'Nivel', text: 'Texto', addRow: '+ Añadir fila', addItem: '+ Añadir punto', addEntry: '+ Añadir entrada', addCol: '+ Columna', removeEntry: 'Quitar entrada', up: '↑ Subir', down: '↓ Bajar', dup: '⧉ Duplicar', del: '✕ Borrar', color: 'Color', headers: 'Cabeceras (| separadas)', addRowT: '+ Fila', src: 'URL de imagen (o sube abajo)', upload: 'Subir imagen…', width: 'Ancho %', caption: 'Pie', open: 'Abrir', duplicate: 'Duplicar', delete: 'Borrar', restore: 'Restaurar', purge: 'Borrar para siempre', saved: 'Guardado en biblioteca', savedAt: 'Guardado', editing: 'Editando…', loaded: 'Documento cargado', exported: 'Descargado', fixFirst: 'Corrige los errores antes de exportar', noDocs: 'Nada por aquí.', blocksN: 'bloques', wordsN: 'palabras', pagesN: 'páginas', templateLoaded: 'Plantilla cargada', imported: 'Importado', confirmDel: '¿Mover a la papelera?', confirmPurge: '¿Borrar para siempre? No se puede deshacer.', palettePh: 'Escribe un comando…', theme: 'Tema', language: 'Idioma', undo: 'Deshacer', redo: 'Rehacer', save: 'Guardar en biblioteca', export: 'Exportar', goEditor: 'Ir al editor', goLibrary: 'Ir a la biblioteca', validate: 'Validar ahora', zoomIn: 'Acercar', zoomOut: 'Alejar', zoomReset: 'Zoom 100%', newFrom: 'Nuevo desde plantilla', shortcuts: 'Atajos de teclado', close: 'Cerrar', history: 'Historial', comments: 'Comentarios', addComment: 'Comentar', yourName: 'Tu nombre', writeComment: 'Escribe un comentario…', resolve: 'Resolver', reopen: 'Reabrir', noComments: 'Sin comentarios.', needSave: 'Guarda el documento en la biblioteca para comentar.', signHere: 'Firma aquí', drawLeft: 'Dibujar firma izquierda', drawRight: 'Dibujar firma derecha', clearDrawing: 'Quitar dibujo', tplNamePh: 'Nombre de plantilla…', tplDescPh: 'Descripción…', saveTpl: 'Guardar actual como plantilla', tplSaved: 'Plantilla guardada', tplDeleted: 'Plantilla borrada', confirmTplDel: '¿Borrar esta plantilla?', varsTitle: 'Rellena los valores', createDoc: 'Crear documento', trashTitle: 'Papelera', backToDocs: 'Volver a documentos', print: 'Imprimir (navegador)', findVersions: 'Versiones', diffVsCurrent: 'Diff vs actual', restoreVersion: 'Restaurar esta versión', restored: 'Versión restaurada', depth: 'Profundidad', allTags: '🏷 Todas', allStates: 'Todos los estados', draft: 'Borrador', in_review: 'En revisión', approved: 'Aprobado', favOnly: 'Solo favoritos', emptyTrash: 'Papelera vacía.' },
};
let lang = localStorage.getItem('genpdf.lang') || 'en';
const t = (k) => (I18N[lang] && I18N[lang][k]) || I18N.en[k] || k;

/* ================= state ================= */
let doc = null, libraryId = null, selectedId = null;
let history = [], future = [], focusSnapshot = null, layoutCache = null;
let templates = [], userTemplates = [], libTrash = false, libFav = false;
let commentsCache = [];
let theme = localStorage.getItem('genpdf.theme') || 'light', zoom = +(localStorage.getItem('genpdf.zoom') || 1);

const uid = () => (crypto.randomUUID ? crypto.randomUUID().slice(0, 12) : String(Date.now() + Math.random()));
const snap = () => JSON.stringify(doc);
function markDirty() { const s = $('#saveState'); s.textContent = '○ ' + t('editing'); s.className = 'dirty'; }
const saveLocal = (() => {
  let h;
  return () => {
    clearTimeout(h);
    h = setTimeout(() => {
      try {
        localStorage.setItem('genpdf.doc.v1', snap());
        localStorage.setItem('genpdf.libid', libraryId || '');
        const s = $('#saveState');
        s.textContent = '● ' + t('savedAt') + ' ' + new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        s.className = 'clean';
      } catch { /* private mode */ }
    }, 400);
  };
})();
function pushHistory(s) { history.push(s ?? snap()); if (history.length > 100) history.shift(); future = []; syncUndoBtns(); }
function syncUndoBtns() { $('#btnUndo').disabled = !history.length; $('#btnRedo').disabled = !future.length; }
function toastMsg(m, kind) {
  const box = $('#toasts');
  const d = document.createElement('div');
  d.className = 'toast' + (kind ? ' ' + kind : ''); d.textContent = m;
  d.onclick = () => d.remove();
  box.appendChild(d);
  setTimeout(() => d.remove(), 2600);
  while (box.children.length > 4) box.firstChild.remove();
}
async function api(path, body) {
  const r = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body ?? doc) });
  if (!r.ok) { let d = {}; try { d = await r.json(); } catch { /* text */ } throw new Error(d.detail || r.statusText); }
  return r;
}

/* ================= markdown subset ================= */
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
function mdToHtml(s) {
  return esc(s).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/\*(.+?)\*/g, '<em>$1</em>').replace(/`(.+?)`/g, '<code>$1</code>');
}

/* ================= theme / zoom / views ================= */
function applyTheme() {
  document.documentElement.dataset.theme = theme;
  $('#btnTheme').textContent = theme === 'light' ? '🌙' : '☀️';
  localStorage.setItem('genpdf.theme', theme);
}
function applyZoom() {
  zoom = Math.max(0.6, Math.min(1.5, zoom));
  document.documentElement.style.setProperty('--sheetw', Math.round(794 * zoom) + 'px');
  document.documentElement.style.setProperty('--sheetfs', (15 * zoom).toFixed(1) + 'px');
  $('#zoomVal').textContent = Math.round(zoom * 100) + '%';
  localStorage.setItem('genpdf.zoom', zoom);
}
function switchView(name) {
  document.querySelectorAll('#rail [data-view]').forEach(b => b.classList.toggle('active', b.dataset.view === name));
  $('#viewEditor').hidden = name !== 'editor';
  $('#viewLibrary').hidden = name !== 'library';
  $('#panel').style.display = name === 'editor' ? '' : 'none';
  if (name === 'library') renderLib();
}

/* ================= edit widgets ================= */
function beginSession() { if (focusSnapshot === null) focusSnapshot = snap(); }
function endSession() { setTimeout(() => { if (focusSnapshot && focusSnapshot !== snap()) pushHistory(focusSnapshot); focusSnapshot = null; }, 0); }

function richEdit(getter, setter, ph) {
  const wrap = document.createElement('div');
  const show = () => {
    wrap.innerHTML = '';
    const d = document.createElement('div');
    d.className = 'redit'; d.title = 'Click to edit — **bold**, *italic*, `code` · / for blocks';
    const v = getter();
    d.innerHTML = v.trim() ? mdToHtml(v) : `<span class="phempty">${esc(ph)}</span>`;
    d.addEventListener('click', edit);
    wrap.appendChild(d);
  };
  const edit = () => {
    wrap.innerHTML = '';
    const ed = document.createElement('div');
    ed.className = 'editable'; ed.contentEditable = 'plaintext-only'; ed.dataset.ph = ph;
    ed.textContent = getter();
    ed.addEventListener('input', () => { setter(ed.textContent); markDirty(); saveLocal(); onSlashInput(ed); });
    ed.addEventListener('blur', () => { setter(ed.textContent); saveLocal(); show(); endSession(); closeSlash(); });
    ed.addEventListener('keydown', (e) => {
      // Global shortcuts (palette, save, bold/italic) live on document:
      // let Ctrl/Cmd combos bubble instead of swallowing them here.
      if ((e.ctrlKey || e.metaKey) && ['k', 's', 'b', 'i'].includes(e.key.toLowerCase())) return;
      e.stopPropagation();
      if (e.key === 'Escape') { if (slash.open) closeSlash(); else ed.blur(); return; }
      if (!slash.open) return;
      const items = filterItems(BLOCK_DEFS, slash.filter);
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        const d = e.key === 'ArrowDown' ? 1 : -1;
        slash.active = (slash.active + d + Math.max(1, items.length)) % Math.max(1, items.length);
        renderFloatMenu(items, pickSlash);
      } else if ((e.key === 'Enter' || e.key === 'Tab') && items.length) {
        e.preventDefault();
        pickSlash(items[slash.active] || items[0]);
      }
    });
    ed.addEventListener('focus', beginSession);
    wrap.appendChild(ed); ed.focus();
  };
  show();
  return wrap;
}
function plainEdit(getter, setter, ph, bold) {
  const s = document.createElement('span');
  s.className = 'editable'; s.contentEditable = 'plaintext-only'; s.dataset.ph = ph || '';
  if (bold) s.style.fontWeight = '700';
  s.textContent = getter() || '';
  s.addEventListener('input', () => { setter(s.textContent); markDirty(); saveLocal(); });
  s.addEventListener('focus', beginSession);
  s.addEventListener('blur', () => { setter(s.textContent); saveLocal(); endSession(); });
  s.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && ['k', 's', 'b', 'i'].includes(e.key.toLowerCase())) return;
    e.stopPropagation();
  });
  return s;
}
function surround(pre, post) {
  const a = document.activeElement;
  if (!a || !a.classList || !a.classList.contains('editable') || !sheet.contains(a)) { toastMsg('Click a text first'); return; }
  const sel = window.getSelection();
  if (!sel.rangeCount) return;
  const range = sel.getRangeAt(0);
  if (!a.contains(range.commonAncestorContainer)) return;
  range.deleteContents();
  range.insertNode(document.createTextNode(pre + range.toString() + post));
  a.dispatchEvent(new Event('input', { bubbles: true }));
  a.focus();
}

/* ================= preview ================= */
const byId = (id) => doc.blocks.find(b => b.id === id);
const idxOf = (id) => doc.blocks.findIndex(b => b.id === id);

function renderPreview() {
  sheet.innerHTML = '';
  const comp = document.createElement('div');
  comp.className = 'companyline';
  comp.appendChild(plainEdit(() => doc.company_name, v => { doc.company_name = v; }, 'Organization (optional)'));
  sheet.appendChild(comp);
  doc.blocks.forEach((b, i) => {
    const pg = layoutCache && layoutCache.blocks ? layoutCache.blocks[b.id] : null;
    if (pg && pg > 1 && i > 0) {
      const prevPg = layoutCache.blocks[doc.blocks[i - 1].id];
      if (prevPg !== pg) {
        const sep = document.createElement('div');
        sep.className = 'pagebreak'; sep.textContent = `${t('page')} ${pg}`;
        sheet.appendChild(sep);
      }
    }
    sheet.appendChild(blockEl(b));
  });
  $('#dropHint').hidden = doc.blocks.length > 0;
  updateStatus();
}

const BLOCK_DEFS = [
  { type: 'heading', icon: 'H', hint: 'Title / subtitle' },
  { type: 'paragraph', icon: '¶', hint: 'Rich text block' },
  { type: 'keyvalue', icon: '⊞', hint: 'Label : value rows' },
  { type: 'bullets', icon: '•', hint: 'Bullet list' },
  { type: 'checklist', icon: '☑', hint: 'Tasks with checkboxes' },
  { type: 'sections', icon: '1.', hint: 'Numbered sections' },
  { type: 'table', icon: '▦', hint: 'Grid table' },
  { type: 'columns', icon: '▥', hint: 'Side-by-side columns' },
  { type: 'image', icon: '🖼', hint: 'Image + caption' },
  { type: 'quote', icon: '❝', hint: 'Highlighted quote' },
  { type: 'code', icon: '</>', hint: 'Monospace block' },
  { type: 'toc', icon: '☰', hint: 'Auto table of contents' },
  { type: 'pagebreak', icon: '⤓', hint: 'Force new page' },
  { type: 'divider', icon: '―', hint: 'Horizontal rule' },
  { type: 'signatures', icon: '✒', hint: 'Two signature columns' },
];
const CONVERTIBLE = ['heading', 'paragraph', 'quote', 'code', 'bullets'];

function blockEl(b) {
  const w = document.createElement('div');
  w.className = 'block' + (b.id === selectedId ? ' selected' : '');
  w.dataset.id = b.id;
  const gut = document.createElement('span');
  gut.className = 'gutter';
  const grip = document.createElement('button');
  grip.className = 'grip'; grip.textContent = '⠿'; grip.title = 'Drag to move'; grip.draggable = true; grip.tabIndex = -1;
  grip.addEventListener('dragstart', e => { e.dataTransfer.setData('text/plain', b.id); e.dataTransfer.effectAllowed = 'move'; w.classList.add('dragging'); });
  grip.addEventListener('dragend', () => w.classList.remove('dragging'));
  const plus = document.createElement('button');
  plus.textContent = '+'; plus.title = 'Insert block below'; plus.tabIndex = -1;
  plus.addEventListener('click', e => { e.stopPropagation(); openInsertMenu(plus, b.id); });
  gut.append(grip, plus);
  const nComments = commentsCache.filter(c => c.block_id === b.id && !c.resolved).length;
  if (nComments) {
    const cb = document.createElement('button');
    cb.className = 'cbadge'; cb.textContent = '💬' + nComments; cb.tabIndex = -1;
    cb.onclick = (e) => { e.stopPropagation(); selectBlock(b.id); setTimeout(() => $('#cmtText')?.focus(), 50); };
    gut.appendChild(cb);
  }
  w.appendChild(gut);
  const body = document.createElement('div');
  body.style.textAlign = b.align || 'left';
  const col = b.color || '';
  const paint = (el) => { if (col) el.style.color = col; return el; };

  if (b.type === 'heading') {
    const h = document.createElement('h' + (b.level || 2)); h.className = 'ph';
    h.appendChild(paint(richEdit(() => b.text, v => { b.text = v; }, 'Heading')));
    body.appendChild(h);
  } else if (b.type === 'paragraph') {
    const p = document.createElement('p'); p.className = 'ph';
    p.appendChild(paint(richEdit(() => b.text, v => { b.text = v; }, 'Write here…  **bold**  *italic*  `code`  / blocks')));
    body.appendChild(p);
  } else if (b.type === 'quote') {
    const q = document.createElement('div'); q.className = 'quotef';
    q.appendChild(richEdit(() => b.text, v => { b.text = v; }, 'Quote'));
    body.appendChild(q);
  } else if (b.type === 'code') {
    const c = document.createElement('div'); c.className = 'codef';
    c.appendChild(plainEdit(() => b.text, v => { b.text = v; }, 'code…'));
    body.appendChild(c);
  } else if (b.type === 'divider') {
    body.appendChild(document.createElement('hr'));
  } else if (b.type === 'pagebreak') {
    const d = document.createElement('div'); d.className = 'pbrk'; d.textContent = '⤓ Page break';
    body.appendChild(d);
  } else if (b.type === 'toc') {
    const d = document.createElement('div'); d.className = 'toclist';
    d.textContent = '☰ Table of contents (auto, depth ' + (b.toc_depth || 2) + ')';
    body.appendChild(d);
  } else if (b.type === 'keyvalue') {
    const kv = document.createElement('div'); kv.className = 'kv';
    (b.rows || []).forEach(r => {
      kv.appendChild(plainEdit(() => r.label, v => { r.label = v; }, 'Label', true));
      kv.appendChild(plainEdit(() => r.value, v => { r.value = v; }, 'Value — **bold** ok'));
    });
    body.appendChild(kv);
  } else if (b.type === 'bullets') {
    const ul = document.createElement('ul'); ul.className = 'bullets';
    if (col) ul.style.color = col;
    (b.items || []).forEach((it, i) => {
      const li = document.createElement('li');
      li.appendChild(richEdit(() => b.items[i], v => { b.items[i] = v; }, 'Item'));
      ul.appendChild(li);
    });
    body.appendChild(ul);
  } else if (b.type === 'checklist') {
    const ul = document.createElement('ul'); ul.className = 'chk';
    (b.checklist || []).forEach((it, i) => {
      const li = document.createElement('li');
      const cb = document.createElement('input'); cb.type = 'checkbox'; cb.checked = !!it.checked;
      cb.addEventListener('change', () => { pushHistory(); it.checked = cb.checked; markDirty(); saveLocal(); });
      li.appendChild(cb);
      li.appendChild(richEdit(() => b.checklist[i].text, v => { b.checklist[i].text = v; }, 'Task'));
      ul.appendChild(li);
    });
    body.appendChild(ul);
  } else if (b.type === 'sections') {
    let num = 0;
    doc.blocks.slice(0, idxOf(b.id)).forEach(x => { if (x.type === 'sections') num += x.entries.length; });
    (b.entries || []).forEach((e, i) => {
      const d = document.createElement('div'); d.className = 'secentry';
      d.append(String(num + i + 1) + '. ');
      const tt = richEdit(() => b.entries[i].title, v => { b.entries[i].title = v; }, 'Section title');
      tt.style.fontWeight = '700';
      d.append(tt, document.createElement('br'));
      d.appendChild(richEdit(() => b.entries[i].text, v => { b.entries[i].text = v; }, 'Description'));
      body.appendChild(d);
    });
  } else if (b.type === 'table') {
    const tb = document.createElement('table'); tb.className = 'ed';
    const th = document.createElement('tr');
    (b.table.headers || []).forEach((h, j) => {
      const c = document.createElement('th');
      c.appendChild(plainEdit(() => b.table.headers[j], v => { b.table.headers[j] = v; }, 'Header'));
      th.appendChild(c);
    });
    tb.appendChild(th);
    (b.table.rows || []).forEach((row, i) => {
      const tr = document.createElement('tr');
      row.forEach((cell, j) => {
        const c = document.createElement('td');
        c.appendChild(plainEdit(() => b.table.rows[i][j], v => { b.table.rows[i][j] = v; }, ''));
        tr.appendChild(c);
      });
      tb.appendChild(tr);
    });
    body.appendChild(tb);
  } else if (b.type === 'columns') {
    const g = document.createElement('div'); g.className = 'cols2';
    (b.columns || []).forEach((c, i) => {
      const d = document.createElement('div'); d.className = 'col';
      const h = document.createElement('h4');
      h.appendChild(richEdit(() => b.columns[i].title, v => { b.columns[i].title = v; }, 'Column title'));
      d.appendChild(h);
      d.appendChild(richEdit(() => b.columns[i].text, v => { b.columns[i].text = v; }, 'Column text'));
      g.appendChild(d);
    });
    body.appendChild(g);
  } else if (b.type === 'image') {
    const d = document.createElement('div'); d.className = 'imgf'; d.style.textAlign = 'center';
    if (b.image.src) {
      const img = document.createElement('img');
      img.src = b.image.src; img.style.maxWidth = (b.image.width_pct || 80) + '%'; img.alt = '';
      d.appendChild(img); d.appendChild(document.createElement('br'));
    }
    const cap = document.createElement('div'); cap.className = 'cap';
    cap.appendChild(plainEdit(() => b.image.caption, v => { b.image.caption = v; }, 'Caption — set image in the panel →'));
    d.appendChild(cap); body.appendChild(d);
  } else if (b.type === 'signatures') {
    const g = document.createElement('div'); g.className = 'sig';
    [['left', b.left], ['right', b.right]].forEach(([k, side]) => {
      const c = document.createElement('div');
      if (side.drawing) {
        const img = document.createElement('img');
        img.src = side.drawing; img.style.maxHeight = '54px'; img.alt = 'signature';
        c.appendChild(img); c.appendChild(document.createElement('br'));
      } else {
        c.appendChild(Object.assign(document.createElement('div'), { className: 'line' }));
      }
      const nm = plainEdit(() => side.name, v => { side.name = v; }, 'Name');
      const rl = plainEdit(() => side.role, v => { side.role = v; }, 'Role'); rl.classList.add('role');
      c.append(nm, document.createElement('br'), rl);
      g.appendChild(c); void k;
    });
    body.appendChild(g);
  }
  w.appendChild(body);

  w.addEventListener('click', e => { if (!e.target.closest('.editable') && !e.target.closest('.redit')) selectBlock(b.id); });
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
function selectBlock(id) {
  selectedId = id; selectVisual(id); renderPanel();
  if (matchMedia('(max-width:1080px)').matches) panel.classList.remove('hidden');
}
function moveBlock(id, targetId, before) {
  const from = idxOf(id); if (from < 0) return;
  pushHistory();
  const [b] = doc.blocks.splice(from, 1);
  doc.blocks.splice(idxOf(targetId) + (before ? 0 : 1), 0, b);
  selectedId = id; markDirty(); renderAll(); saveLocal(); refreshLayout();
}

/* ================= slash menu + insert menu ================= */
const slash = { open: false, blockId: null, filter: '', active: 0 };
function openSlash(blockId, filter) {
  slash.open = true; slash.blockId = blockId; slash.filter = filter || ''; slash.active = 0;
  renderFloatMenu(filterItems(BLOCK_DEFS, slash.filter), pickSlash);
}
function closeSlash() { slash.open = false; $('#floatMenu').hidden = true; }
function filterItems(items, q) {
  q = (q || '').toLowerCase();
  return items.filter(x => !q || x.type.includes(q) || x.hint.toLowerCase().includes(q));
}
function onSlashInput(ed) {
  const txt = ed.textContent || '';
  const m = txt.match(/\/([a-z]*)$/i);
  if (m) {
    const b = ed.closest('.block');
    openSlash(b ? b.dataset.id : null, m[1]);
    positionFloat(ed);
  } else if (slash.open) closeSlash();
}
function pickSlash(def) {
  const host = byId(slash.blockId);
  closeSlash();
  if (!host) return;
  const el = sheet.querySelector(`[data-id="${host.id}"] .editable`);
  if (el) {
    const txt = el.textContent || '';
    el.textContent = txt.replace(/\/[a-z]*$/i, '').trimEnd();
    syncSlashEdit(host, el.textContent);
  }
  insertAfter(host.id, def.type);
}
function syncSlashEdit(b, text) {
  if (['heading', 'paragraph', 'quote', 'code'].includes(b.type)) b.text = text;
  markDirty(); saveLocal();
}
function positionFloat(anchorEl) {
  const m = $('#floatMenu');
  const r = anchorEl.getBoundingClientRect();
  m.style.left = Math.min(window.innerWidth - 260, Math.max(8, r.left)) + 'px';
  m.style.top = (r.bottom + 6) + 'px'; // rect is viewport-relative; menu is fixed
  m.hidden = false;
}
function renderFloatMenu(items, onPick) {
  const m = $('#floatMenu');
  m.innerHTML = '';
  if (!items.length) { const d = document.createElement('div'); d.style.padding = '8px 10px'; d.style.color = 'var(--muted)'; d.textContent = 'No matches'; m.appendChild(d); }
  items.forEach((def, i) => {
    const b = document.createElement('button');
    b.className = i === slash.active ? 'active' : '';
    b.innerHTML = `<b style="width:26px;display:inline-block">${esc(def.icon)}</b> ${esc(def.type)} <small style="color:var(--muted)">${esc(def.hint)}</small>`;
    b.onmousedown = (e) => { e.preventDefault(); onPick(def); };
    b.onmouseenter = () => { slash.active = i; m.querySelectorAll('button').forEach((x, j) => x.classList.toggle('active', j === i)); };
    m.appendChild(b);
  });
  m.hidden = false;
}
function openInsertMenu(anchorBtn, afterId) {
  slash.open = false; slash.active = 0;
  const r = anchorBtn.getBoundingClientRect();
  const m = $('#floatMenu');
  m.style.left = Math.min(window.innerWidth - 260, r.left) + 'px';
  m.style.top = (r.bottom + 6) + 'px';
  const f = document.createElement('input');
  f.type = 'text'; f.placeholder = t('searchPh'); f.style.margin = '4px';
  m.innerHTML = ''; m.appendChild(f);
  const list = document.createElement('div'); m.appendChild(list);
  const draw = () => {
    list.innerHTML = '';
    filterItems(BLOCK_DEFS, f.value).forEach(def => {
      const b = document.createElement('button');
      b.innerHTML = `<b style="width:26px;display:inline-block">${esc(def.icon)}</b> ${esc(def.type)} <small style="color:var(--muted)">${esc(def.hint)}</small>`;
      b.onclick = () => { m.hidden = true; insertAfter(afterId, def.type); };
      list.appendChild(b);
    });
  };
  f.oninput = draw; draw(); m.hidden = false; f.focus();
}
function insertAfter(afterId, type) {
  pushHistory();
  const b = blankBlock(type);
  const i = afterId ? idxOf(afterId) : doc.blocks.length - 1;
  doc.blocks.splice(i + 1, 0, b);
  selectedId = b.id; markDirty(); renderAll(); saveLocal(); refreshLayout();
  requestAnimationFrame(() => {
    const el = sheet.querySelector(`[data-id="${b.id}"] .editable`);
    if (el) el.focus();
  });
  closeSlash();
}
document.addEventListener('click', e => {
  if (!e.target.closest('#floatMenu') && !e.target.closest('.gutter')) closeSlash();
  if (!e.target.closest('.split')) $('#exportMenu').hidden = true;
});

/* ================= property panel ================= */
function h3(s) { const h = document.createElement('h3'); h.textContent = s; panel.appendChild(h); }
function field(label, value, onInput, type) {
  const l = document.createElement('label'); l.textContent = label;
  const i = document.createElement('input'); i.type = type || 'text'; i.value = value ?? '';
  i.addEventListener('input', () => { onInput(i.value); markDirty(); });
  panel.append(l, i); return i;
}
function miniBtns(items) {
  const d = document.createElement('div'); d.className = 'mini';
  items.forEach(([label, fn, danger]) => { const b = document.createElement('button'); b.textContent = label; if (danger) b.className = 'danger'; b.onclick = fn; d.appendChild(b); });
  panel.appendChild(d);
}
function colorField(b) {
  const l = document.createElement('label'); l.textContent = t('color');
  const row = document.createElement('div'); row.className = 'row';
  const c = document.createElement('input'); c.type = 'color'; c.value = /^#[0-9a-f]{6}$/i.test(b.color || '') ? b.color : '#000000'; c.style.flex = '0 0 52px';
  const tx = document.createElement('input'); tx.type = 'text'; tx.placeholder = '#rrggbb'; tx.value = b.color || '';
  let pushed = false;
  const sync = (v) => { if (!pushed) { pushHistory(); pushed = true; } b.color = v; renderPreview(); selectVisual(b.id); markDirty(); saveLocal(); };
  c.addEventListener('input', () => { tx.value = c.value; sync(c.value); });
  tx.addEventListener('input', () => sync(tx.value));
  const cl = document.createElement('button'); cl.textContent = '✕'; cl.style.flex = '0 0 40px'; cl.title = 'Clear';
  cl.onclick = () => { pushHistory(); b.color = ''; markDirty(); renderAll(); saveLocal(); };
  row.append(c, tx, cl); panel.append(l, row);
}
function panelCloseBtn() {
  const x = document.createElement('button');
  x.textContent = '✕'; x.className = 'ghost'; x.style.cssText = 'position:absolute;top:8px;right:8px';
  x.style.display = matchMedia('(max-width:1080px)').matches ? '' : 'none';
  x.onclick = () => panel.classList.add('hidden');
  panel.appendChild(x);
}
function msgBox() { let m = $('#msgs'); if (!m) { m = document.createElement('div'); m.id = 'msgs'; panel.appendChild(m); } return m; }

function convertBlock(b, to) {
  const text = b.text || b.entries?.map(e => `${e.title}\n${e.text}`).join('\n') || (b.items || []).join('\n') || '';
  pushHistory();
  b.type = to;
  if (CONVERTIBLE.includes(to)) b.text = text;
  if (to === 'heading' && !b.level) b.level = 2;
  markDirty(); renderAll(); saveLocal(); refreshLayout();
}

function renderPanel() {
  panel.innerHTML = '';
  panelCloseBtn();
  h3(t('blockDoc'));
  field(t('company'), doc.company_name, v => { doc.company_name = v; renderPreview(); saveLocal(); });
  const lab = document.createElement('label'); lab.textContent = t('options');
  const chk = document.createElement('div');
  chk.innerHTML = `<label style="display:flex;gap:6px;align-items:center"><input type="checkbox" ${doc.show_page_numbers ? 'checked' : ''} style="width:auto"> ${t('pageNumbers')}</label>`;
  panel.append(lab, chk);
  chk.querySelector('input').addEventListener('change', e => { pushHistory(); doc.show_page_numbers = e.target.checked; markDirty(); saveLocal(); });

  const favRow = document.createElement('div');
  favRow.innerHTML = `<label style="display:flex;gap:6px;align-items:center"><input type="checkbox" ${doc.favorite ? 'checked' : ''} style="width:auto"> ★ ${t('favorite')}</label>`;
  panel.appendChild(favRow);
  favRow.querySelector('input').addEventListener('change', e => { pushHistory(); doc.favorite = e.target.checked; markDirty(); saveLocal(); });
  field(t('tags'), (doc.tags || []).join(', '), v => { doc.tags = v.split(',').map(s => s.trim().toLowerCase()).filter(Boolean); saveLocal(); });
  const sl = document.createElement('label'); sl.textContent = t('status');
  const ss = document.createElement('select');
  [['draft', t('draft')], ['in_review', t('in_review')], ['approved', t('approved')]].forEach(([v, s]) => {
    const o = document.createElement('option'); o.value = v; o.textContent = s; if (doc.status === v) o.selected = true; ss.appendChild(o);
  });
  ss.onchange = () => { pushHistory(); doc.status = ss.value; markDirty(); saveLocal(); persistStatus(); };
  panel.append(sl, ss);

  const pl = document.createElement('label'); pl.textContent = `${t('size')} / ${t('orientation')} / ${t('margin')}`;
  const pr = document.createElement('div'); pr.className = 'row';
  const ssize = document.createElement('select');
  ['A4', 'Letter'].forEach(s => { const o = document.createElement('option'); o.value = s; o.textContent = s; if (doc.page.size === s) o.selected = true; ssize.appendChild(o); });
  const sori = document.createElement('select');
  [['P', t('portrait')], ['L', t('landscape')]].forEach(([v, s]) => { const o = document.createElement('option'); o.value = v; o.textContent = s; if (doc.page.orientation === v) o.selected = true; sori.appendChild(o); });
  const sm = document.createElement('input'); sm.type = 'text'; sm.value = doc.page.margin_mm;
  const applyPage = () => { pushHistory(); doc.page.size = ssize.value; doc.page.orientation = sori.value; doc.page.margin_mm = Math.max(10, Math.min(40, +sm.value || 20)); markDirty(); renderAll(); saveLocal(); refreshLayout(); };
  ssize.onchange = applyPage; sori.onchange = applyPage; sm.onchange = applyPage;
  pr.append(ssize, sori, sm); panel.append(pl, pr);

  miniBtns([[t('exportPdf'), exportPdf], ['Markdown ↓', exportMd], ['DOCX ↓', exportDocx], ['JSON ↓', exportJson], [t('history'), openHistory]]);
  panel.appendChild(document.createElement('hr'));

  const b = byId(selectedId);
  if (!b) { const p = document.createElement('p'); p.className = 'meta'; p.textContent = t('selHint'); panel.appendChild(p); msgBox(); return; }
  h3(t('block') + ': ' + b.type);

  if (CONVERTIBLE.includes(b.type)) {
    const cl = document.createElement('label'); cl.textContent = t('convertTo');
    const cs = document.createElement('select');
    CONVERTIBLE.forEach(x => { const o = document.createElement('option'); o.value = x; o.textContent = x; if (b.type === x) o.selected = true; cs.appendChild(o); });
    cs.onchange = () => convertBlock(b, cs.value);
    panel.append(cl, cs);
  }
  const al = document.createElement('label'); al.textContent = t('alignment');
  const as = document.createElement('select');
  ['left', 'center', 'right'].forEach(a => { const o = document.createElement('option'); o.value = a; o.textContent = a; if (b.align === a) o.selected = true; as.appendChild(o); });
  as.addEventListener('change', () => { pushHistory(); b.align = as.value; markDirty(); renderAll(); saveLocal(); });
  panel.append(al, as);

  if (['heading', 'paragraph', 'bullets'].includes(b.type)) colorField(b);
  if (b.type === 'heading') {
    const ll = document.createElement('label'); ll.textContent = t('level');
    const ls = document.createElement('select');
    [1, 2, 3].forEach(n => { const o = document.createElement('option'); o.value = n; o.textContent = 'H' + n; if (b.level === n) o.selected = true; ls.appendChild(o); });
    ls.addEventListener('change', () => { pushHistory(); b.level = +ls.value; markDirty(); renderAll(); saveLocal(); refreshLayout(); });
    panel.append(ll, ls);
    field(t('text'), b.text, v => { b.text = v; renderPreview(); selectVisual(b.id); saveLocal(); });
  } else if (['paragraph', 'quote', 'code'].includes(b.type)) {
    const ll = document.createElement('label'); ll.textContent = t('text');
    const ta = document.createElement('textarea'); ta.rows = 4; ta.value = b.text || '';
    ta.addEventListener('input', () => { b.text = ta.value; renderPreview(); selectVisual(b.id); saveLocal(); });
    panel.append(ll, ta);
  } else if (b.type === 'keyvalue') {
    b.rows.forEach((r, i) => {
      const row = document.createElement('div'); row.className = 'row';
      const a = document.createElement('input'); a.type = 'text'; a.placeholder = 'Label'; a.value = r.label || '';
      const c = document.createElement('input'); c.type = 'text'; c.placeholder = 'Value'; c.value = r.value || '';
      const x = document.createElement('button'); x.textContent = '✕';
      x.onclick = () => { pushHistory(); b.rows.splice(i, 1); markDirty(); renderAll(); saveLocal(); };
      a.addEventListener('input', () => { r.label = a.value; renderPreview(); selectVisual(b.id); saveLocal(); });
      c.addEventListener('input', () => { r.value = c.value; renderPreview(); selectVisual(b.id); saveLocal(); });
      row.append(a, c, x); panel.appendChild(row);
    });
    miniBtns([[t('addRow'), () => { pushHistory(); b.rows.push({ label: '', value: '' }); markDirty(); renderAll(); saveLocal(); }]]);
  } else if (b.type === 'bullets') {
    b.items.forEach((it, i) => {
      const row = document.createElement('div'); row.className = 'row';
      const a = document.createElement('input'); a.type = 'text'; a.value = it || '';
      const x = document.createElement('button'); x.textContent = '✕';
      x.onclick = () => { pushHistory(); b.items.splice(i, 1); markDirty(); renderAll(); saveLocal(); refreshLayout(); };
      a.addEventListener('input', () => { b.items[i] = a.value; renderPreview(); selectVisual(b.id); saveLocal(); });
      row.append(a, x); panel.appendChild(row);
    });
    miniBtns([[t('addItem'), () => { pushHistory(); b.items.push(''); markDirty(); renderAll(); saveLocal(); }]]);
  } else if (b.type === 'checklist') {
    b.checklist.forEach((it, i) => {
      const row = document.createElement('div'); row.className = 'row';
      const cb = document.createElement('input'); cb.type = 'checkbox'; cb.checked = !!it.checked; cb.style.flex = '0 0 30px';
      cb.onchange = () => { pushHistory(); it.checked = cb.checked; markDirty(); saveLocal(); };
      const a = document.createElement('input'); a.type = 'text'; a.value = it.text || '';
      const x = document.createElement('button'); x.textContent = '✕';
      x.onclick = () => { pushHistory(); b.checklist.splice(i, 1); markDirty(); renderAll(); saveLocal(); refreshLayout(); };
      a.addEventListener('input', () => { it.text = a.value; renderPreview(); selectVisual(b.id); saveLocal(); });
      row.append(cb, a, x); panel.appendChild(row);
    });
    miniBtns([[t('addItem'), () => { pushHistory(); b.checklist.push({ text: '', checked: false }); markDirty(); renderAll(); saveLocal(); }]]);
  } else if (b.type === 'sections') {
    b.entries.forEach((e, i) => {
      field(`Entry ${i + 1} title`, e.title, v => { e.title = v; renderPreview(); selectVisual(b.id); saveLocal(); });
      const ta = document.createElement('textarea'); ta.rows = 2; ta.value = e.text || '';
      ta.addEventListener('input', () => { e.text = ta.value; renderPreview(); selectVisual(b.id); saveLocal(); });
      panel.appendChild(ta);
      miniBtns([[`${t('removeEntry')} ${i + 1}`, () => { pushHistory(); b.entries.splice(i, 1); markDirty(); renderAll(); saveLocal(); refreshLayout(); }, true]]);
    });
    miniBtns([[t('addEntry'), () => { pushHistory(); b.entries.push({ title: '', text: '' }); markDirty(); renderAll(); saveLocal(); }]]);
  } else if (b.type === 'table') {
    field(t('headers'), (b.table.headers || []).join(' | '), v => {
      b.table.headers = v.split('|').map(s => s.trim());
      const n = b.table.headers.length;
      b.table.rows = b.table.rows.map(r => Object.assign(Array(n).fill(''), r.slice(0, n)));
      renderPreview(); selectVisual(b.id); saveLocal();
    });
    miniBtns([
      [t('addCol'), () => { pushHistory(); b.table.headers.push(''); b.table.rows.forEach(r => r.push('')); markDirty(); renderAll(); saveLocal(); }],
      [t('addRowT'), () => { pushHistory(); b.table.rows.push(Array(Math.max(1, b.table.headers.length)).fill('')); markDirty(); renderAll(); saveLocal(); refreshLayout(); }],
    ]);
  } else if (b.type === 'columns') {
    (b.columns || []).forEach((c, i) => {
      field(`Column ${i + 1} title`, c.title, v => { c.title = v; renderPreview(); selectVisual(b.id); saveLocal(); });
      const ta = document.createElement('textarea'); ta.rows = 2; ta.value = c.text || '';
      ta.addEventListener('input', () => { c.text = ta.value; renderPreview(); selectVisual(b.id); saveLocal(); });
      panel.appendChild(ta);
      if (b.columns.length > 1) miniBtns([[`Remove column ${i + 1}`, () => { pushHistory(); b.columns.splice(i, 1); markDirty(); renderAll(); saveLocal(); refreshLayout(); }, true]]);
    });
    if ((b.columns || []).length < 3) miniBtns([[t('addCol'), () => { pushHistory(); b.columns.push({ title: '', text: '' }); markDirty(); renderAll(); saveLocal(); refreshLayout(); }]]);
  } else if (b.type === 'toc') {
    const ll = document.createElement('label'); ll.textContent = t('depth');
    const ls = document.createElement('select');
    [1, 2, 3].forEach(n => { const o = document.createElement('option'); o.value = n; o.textContent = 'H1–H' + n; if ((b.toc_depth || 2) === n) o.selected = true; ls.appendChild(o); });
    ls.onchange = () => { pushHistory(); b.toc_depth = +ls.value; markDirty(); renderAll(); saveLocal(); };
    panel.append(ll, ls);
  } else if (b.type === 'image') {
    field(t('src'), b.image.src && !b.image.src.startsWith('data:') ? b.image.src : '', v => { b.image.src = v; renderPreview(); selectVisual(b.id); saveLocal(); });
    const up = document.createElement('input'); up.type = 'file'; up.accept = 'image/*';
    const ul = document.createElement('label'); ul.textContent = t('upload');
    up.addEventListener('change', () => {
      const f = up.files[0]; if (!f) return;
      const rd = new FileReader();
      rd.onload = () => { pushHistory(); b.image.src = rd.result; if (!b.image.caption) b.image.caption = f.name; markDirty(); renderAll(); saveLocal(); };
      rd.readAsDataURL(f);
    });
    panel.append(ul, up);
    field(t('width'), String(b.image.width_pct || 80), v => { b.image.width_pct = Math.max(10, Math.min(100, +v || 80)); renderPreview(); selectVisual(b.id); saveLocal(); });
    field(t('caption'), b.image.caption, v => { b.image.caption = v; renderPreview(); selectVisual(b.id); saveLocal(); });
  } else if (b.type === 'signatures') {
    [['left', b.left, t('drawLeft')], ['right', b.right, t('drawRight')]].forEach(([k, side, drawLabel]) => {
      field(k === 'left' ? 'Left name' : 'Right name', side.name, v => { side.name = v; renderPreview(); selectVisual(b.id); saveLocal(); });
      field(k === 'left' ? 'Left role' : 'Right role', side.role, v => { side.role = v; renderPreview(); selectVisual(b.id); saveLocal(); });
      miniBtns(side.drawing
        ? [[t('clearDrawing'), () => { pushHistory(); side.drawing = ''; markDirty(); renderAll(); saveLocal(); }, true]]
        : [[drawLabel, () => openSigPad(side)]]);
      void k;
    });
  }
  panel.appendChild(document.createElement('hr'));
  miniBtns([[t('up'), () => shiftBlock(b.id, -1)], [t('down'), () => shiftBlock(b.id, 1)], [t('dup'), () => duplicateBlock(b.id)], [t('del'), () => deleteBlock(b.id), true]]);
  renderComments(b);
  msgBox();
}

async function persistStatus() {
  if (!libraryId) return;
  try { await fetch(`/api/library/${libraryId}/status`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status: doc.status }) }); } catch { /* draft-only */ }
}

/* ================= comments ================= */
async function loadComments() {
  commentsCache = [];
  if (!libraryId) return;
  try { commentsCache = await (await fetch(`/api/library/${libraryId}/comments`)).json(); } catch { /* ignore */ }
}
function authorName() {
  let a = localStorage.getItem('genpdf.author') || '';
  if (!a) { a = prompt(t('yourName')) || 'anon'; localStorage.setItem('genpdf.author', a); }
  return a;
}
function renderComments(b) {
  const h = document.createElement('h3'); h.textContent = `${t('comments')} (${commentsCache.filter(c => c.block_id === b.id && !c.resolved).length})`;
  panel.appendChild(h);
  if (!libraryId) { const p = document.createElement('p'); p.className = 'meta'; p.textContent = t('needSave'); panel.appendChild(p); return; }
  const list = commentsCache.filter(c => c.block_id === b.id);
  if (!list.length) { const p = document.createElement('p'); p.className = 'meta'; p.textContent = t('noComments'); panel.appendChild(p); }
  list.forEach(c => {
    const d = document.createElement('div'); d.className = 'cmt' + (c.resolved ? ' resolved' : '');
    const who = document.createElement('div'); who.className = 'who';
    who.textContent = `${c.author} · ${new Date(c.created_at * 1000).toLocaleString()}`;
    const tx = document.createElement('div'); tx.textContent = c.text;
    const acts = document.createElement('div'); acts.className = 'mini';
    const rs = document.createElement('button'); rs.textContent = c.resolved ? t('reopen') : t('resolve');
    rs.onclick = async () => {
      await fetch(`/api/library/${libraryId}/comments/${c.id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ resolved: !c.resolved }) });
      await loadComments(); renderAll();
    };
    const del = document.createElement('button'); del.textContent = '✕'; del.className = 'danger';
    del.onclick = async () => {
      await fetch(`/api/library/${libraryId}/comments/${c.id}`, { method: 'DELETE' });
      await loadComments(); renderAll();
    };
    acts.append(rs, del); d.append(who, tx, acts); panel.appendChild(d);
  });
  const ta = document.createElement('textarea'); ta.rows = 2; ta.id = 'cmtText'; ta.placeholder = t('writeComment');
  const add = document.createElement('button'); add.textContent = t('addComment');
  add.onclick = async () => {
    if (!ta.value.trim()) return;
    await fetch(`/api/library/${libraryId}/comments`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ block_id: b.id, author: authorName(), text: ta.value.trim() }) });
    await loadComments(); renderAll(); toastMsg(t('addComment'), 'ok');
  };
  panel.append(ta, add);
}

/* ================= signature pad ================= */
let sigTarget = null, sigDrawing = false;
function openSigPad(side) {
  sigTarget = side;
  $('#sigModal').hidden = false;
  const cv = $('#sigCanvas'), ctx = cv.getContext('2d');
  ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, cv.width, cv.height);
  ctx.strokeStyle = '#111'; ctx.lineWidth = 2.5; ctx.lineCap = 'round';
  if (side.drawing) { const img = new Image(); img.onload = () => ctx.drawImage(img, 0, 0); img.src = side.drawing; }
  const pos = (e) => { const r = cv.getBoundingClientRect(); const p = e.touches ? e.touches[0] : e; return [(p.clientX - r.left) * cv.width / r.width, (p.clientY - r.top) * cv.height / r.height]; };
  let last = null;
  const start = (e) => { e.preventDefault(); sigDrawing = true; last = pos(e); };
  const move = (e) => {
    if (!sigDrawing) return;
    e.preventDefault();
    const [x, y] = pos(e);
    ctx.beginPath(); ctx.moveTo(last[0], last[1]); ctx.lineTo(x, y); ctx.stroke();
    last = [x, y];
  };
  const stop = () => { sigDrawing = false; };
  cv.onmousedown = start; cv.onmousemove = move; window.onmouseup = stop;
  cv.ontouchstart = start; cv.ontouchmove = move; cv.ontouchend = stop;
  $('#sigClear').onclick = () => { ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, cv.width, cv.height); };
  $('#sigClose').onclick = () => { $('#sigModal').hidden = true; };
  $('#sigSave').onclick = () => {
    pushHistory();
    sigTarget.drawing = cv.toDataURL('image/png');
    $('#sigModal').hidden = true;
    markDirty(); renderAll(); saveLocal(); toastMsg(t('saved'), 'ok');
  };
}

/* ================= history ================= */
async function openHistory() {
  if (!libraryId) { toastMsg(t('needSave'), 'err'); return; }
  $('#histModal').hidden = false;
  $('#histDiff').textContent = '';
  const list = $('#histList'); list.innerHTML = '';
  const versions = await (await fetch(`/api/library/${libraryId}/versions`)).json();
  if (!versions.length) { list.innerHTML = `<p class="meta">${t('noDocs')}</p>`; return; }
  versions.forEach(v => {
    const b = document.createElement('button');
    b.innerHTML = `<span></span><small></small>`;
    b.querySelector('span').textContent = (v.label || t('findVersions')) + ' — v' + v.id.slice(0, 6);
    b.querySelector('small').textContent = new Date(v.created_at * 1000).toLocaleString();
    b.onclick = async () => {
      list.querySelectorAll('button').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      const full = await (await fetch(`/api/library/${libraryId}/versions/${v.id}`)).json();
      const r = await fetch('/api/documents/diff', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ a: full.data, b: doc }) });
      $('#histDiff').textContent = (await r.json()).diff || '(no changes)';
      $('#histDiff').dataset.vid = v.id;
      if (!$('#histRestore')) {
        const rb = document.createElement('button'); rb.id = 'histRestore'; rb.textContent = t('restoreVersion');
        rb.onclick = async () => {
          const vid = $('#histDiff').dataset.vid;
          if (!vid || !confirm(t('restoreVersion') + '?')) return;
          const restored = await (await fetch(`/api/library/${libraryId}/versions/${vid}/restore`, { method: 'POST' })).json();
          pushHistory(); doc = restored; selectedId = null;
          markDirty(); renderAll(); saveLocal(); refreshLayout();
          $('#histModal').hidden = true; toastMsg(t('restored'), 'ok');
        };
        $('#histModal .modal').insertBefore(rb, $('#histDiff').nextSibling);
      }
    };
    list.appendChild(b);
  });
}

/* ================= validation / mutations ================= */
async function showValidation() {
  const m = msgBox(); m.innerHTML = '';
  try {
    const v = await (await api('/api/documents/validate')).json();
    const d = document.createElement('div');
    d.className = v.ok ? 'ok' : 'err';
    d.textContent = (v.ok ? '✓ Valid' : '✕ ' + v.errores.join(' ')) + (v.avisos.length ? '\n! ' + v.avisos.join('\n! ') : '');
    m.appendChild(d);
    return v.ok;
  } catch (e) { m.innerHTML = '<span class="err">Validation failed: ' + esc(e.message) + '</span>'; return false; }
}
function shiftBlock(id, d) {
  const i = idxOf(id), j = i + d;
  if (i < 0 || j < 0 || j >= doc.blocks.length) return;
  pushHistory();[doc.blocks[i], doc.blocks[j]] = [doc.blocks[j], doc.blocks[i]];
  markDirty(); renderAll(); saveLocal(); refreshLayout();
}
function duplicateBlock(id) {
  const i = idxOf(id); if (i < 0) return;
  pushHistory();
  const c = JSON.parse(JSON.stringify(doc.blocks[i])); c.id = uid();
  doc.blocks.splice(i + 1, 0, c); selectedId = c.id; markDirty(); renderAll(); saveLocal(); refreshLayout();
}
function deleteBlock(id) {
  pushHistory();
  doc.blocks = doc.blocks.filter(x => x.id !== id);
  selectedId = null; markDirty(); renderAll(); saveLocal(); refreshLayout();
}
function blankBlock(type) {
  const b = { id: uid(), type, align: 'left', color: '', level: 2, text: '', rows: [], items: [], entries: [], left: { name: '', role: '', drawing: '' }, right: { name: '', role: '', drawing: '' }, table: { headers: [], rows: [] }, checklist: [], image: { src: '', caption: '', width_pct: 80 }, columns: [], toc_depth: 2, toc_entries: [] };
  if (type === 'heading') b.text = 'New heading';
  if (type === 'keyvalue') b.rows = [{ label: '', value: '' }];
  if (type === 'bullets') b.items = [''];
  if (type === 'checklist') b.checklist = [{ text: '', checked: false }];
  if (type === 'sections') b.entries = [{ title: '', text: '' }];
  if (type === 'table') { b.table.headers = ['', '']; b.table.rows = [['', '']]; }
  if (type === 'columns') b.columns = [{ title: '', text: '' }, { title: '', text: '' }];
  if (type === 'signatures') { b.left.role = 'Signer 1'; b.right.role = 'Signer 2'; }
  return b;
}

/* ================= layout + status ================= */
const refreshLayout = (() => {
  let h;
  const run = () => {
    clearTimeout(h);
    h = setTimeout(async () => {
      // Never steal the caret: while editing text, reschedule after blur.
      const a = document.activeElement;
      if (a && sheet.contains(a) && a.classList?.contains('editable')) { run(); return; }
      try {
        layoutCache = await (await api('/api/documents/layout')).json();
        const sel = selectedId;
        renderPreview(); selectVisual(sel);
      } catch { /* offline layout: skip silently */ }
    }, 900);
  };
  return run;
})();
function wordCount() {
  let n = 0;
  const push = (s) => { n += String(s || '').trim().split(/\s+/).filter(Boolean).length; };
  (doc.blocks || []).forEach(b => {
    push(b.text);
    (b.rows || []).forEach(r => { push(r.label); push(r.value); });
    (b.items || []).forEach(push);
    (b.entries || []).forEach(e => { push(e.title); push(e.text); });
    (b.checklist || []).forEach(i => push(i.text));
    (b.table.headers || []).forEach(push);
    (b.table.rows || []).forEach(r => r.forEach(push));
    (b.columns || []).forEach(c => { push(c.title); push(c.text); });
    push(b.image.caption);
  });
  return n;
}
function updateStatus() {
  $('#statWords').textContent = `${wordCount()} ${t('wordsN')}`;
  $('#statBlocks').textContent = `${(doc.blocks || []).length} ${t('blocksN')}`;
  const pg = layoutCache ? layoutCache.pages : '?';
  $('#statPages').textContent = `${pg} ${t('pagesN')} · ${doc.page.size}${doc.page.orientation === 'L' ? '-L' : ''}`;
  $('#pageInfo').textContent = layoutCache ? `${layoutCache.pages} ${t('pagesN')} · ${doc.page.size}` : '';
}

/* ================= library view ================= */
function currentFilters() {
  return { q: $('#libSearch').value || '', tag: $('#libTag').value || '', status: $('#libStatus').value || '', fav: libFav ? '1' : '', trash: libTrash ? '1' : '' };
}
async function renderLib() {
  const f = currentFilters();
  const qs = new URLSearchParams({ q: f.q, tag: f.tag, status: f.status, ...(f.fav ? { fav: '1' } : {}), ...(f.trash ? { trash: '1' } : {}) });
  const box = $('#libList'); box.innerHTML = '';
  const tpls = $('#libTemplates'); tpls.innerHTML = '';
  $('#libTrash').classList.toggle('active', libTrash);
  $('#libTrash').textContent = libTrash ? '📂' : '🗑';
  $('#libFav').classList.toggle('active', libFav);
  $('#libFav').textContent = libFav ? '★' : '☆';

  try {
    const [tags, uts] = await Promise.all([
      (await fetch('/api/library/tags')).json(),
      (await fetch('/api/templates/user')).json(),
    ]);
    const sel = $('#libTag'), cur = sel.value;
    sel.innerHTML = `<option value="">${t('allTags')}</option>`;
    tags.forEach(x => { const o = document.createElement('option'); o.value = x.tag; o.textContent = `${x.tag} (${x.count})`; sel.appendChild(o); });
    sel.value = cur;
    templates.forEach(x => tpls.appendChild(tplCard('+ ' + x.name, x.description, () => openTemplateWithVars('builtin:' + x.id, x.name))));
    uts.forEach(x => {
      const c = tplCard(x.name, x.description, () => openTemplateWithVars('user:' + x.id, x.name));
      const del = document.createElement('button'); del.textContent = t('delete'); del.className = 'danger';
      del.onclick = async (e) => { e.stopPropagation(); if (!confirm(t('confirmTplDel'))) return; await fetch('/api/templates/user/' + x.id, { method: 'DELETE' }); renderLib(); toastMsg(t('tplDeleted'), 'ok'); };
      c.appendChild(del); tpls.appendChild(c);
    });
  } catch { /* ignore */ }

  let docs = [];
  try { docs = await (await fetch('/api/library?' + qs)).json(); } catch { box.innerHTML = '<p class="meta">API unreachable</p>'; return; }
  const sort = $('#libSort').value;
  docs.sort(sort === 'title' ? (a, b) => a.title.localeCompare(b.title) : (a, b) => b.updated_at - a.updated_at);
  if (!docs.length) { box.innerHTML = `<p class="meta">${libTrash ? t('emptyTrash') : t('noDocs')}</p>`; return; }
  docs.forEach(d => {
    const c = document.createElement('div'); c.className = 'libCard' + (d.id === libraryId ? ' current' : '');
    const info = document.createElement('div');
    const fav = d.favorite ? ' <span class="fav">★</span>' : '';
    const st = `<span class="status ${d.status}">${d.status.replace('_', ' ')}</span>`;
    info.innerHTML = '<b></b><br><small></small>';
    info.querySelector('b').innerHTML = '';
    info.querySelector('b').textContent = d.title;
    info.querySelector('b').insertAdjacentHTML('beforeend', fav);
    const nb = (d.document.blocks || []).length;
    info.querySelector('small').textContent = `${nb} ${t('blocksN')} · ${new Date(d.updated_at * 1000).toLocaleString()}`;
    const tagRow = document.createElement('div');
    (d.tags || []).forEach(x => { const s = document.createElement('span'); s.className = 'tag'; s.textContent = x; tagRow.appendChild(s); });
    const acts = document.createElement('div'); acts.className = 'acts';
    if (libTrash) {
      const rs = document.createElement('button'); rs.textContent = t('restore');
      rs.onclick = async () => { await fetch('/api/library/' + d.id + '/restore', { method: 'POST' }); renderLib(); };
      const pg = document.createElement('button'); pg.textContent = t('purge'); pg.className = 'danger';
      pg.onclick = async () => { if (!confirm(t('confirmPurge'))) return; await fetch('/api/library/' + d.id + '?hard=true', { method: 'DELETE' }); renderLib(); };
      acts.append(rs, pg);
    } else {
      const open = document.createElement('button'); open.textContent = t('open'); open.className = 'primary';
      open.onclick = async () => { await openLibraryDoc(d.id); };
      const dup = document.createElement('button'); dup.textContent = t('duplicate');
      dup.onclick = async () => { await fetch('/api/library/' + d.id + '/duplicate', { method: 'POST' }); renderLib(); };
      const del = document.createElement('button'); del.textContent = t('delete'); del.className = 'danger';
      del.onclick = async () => {
        if (!confirm(t('confirmDel'))) return;
        await fetch('/api/library/' + d.id, { method: 'DELETE' });
        if (libraryId === d.id) libraryId = null;
        renderLib(); saveLocal();
      };
      acts.append(open, dup, del);
    }
    const stDiv = document.createElement('div'); stDiv.innerHTML = st;
    c.append(info, tagRow, stDiv, acts); box.appendChild(c);
  });
}
function tplCard(name, desc, onOpen) {
  const c = document.createElement('button'); c.className = 'tplCard';
  c.innerHTML = '<b></b><br><small></small>';
  c.querySelector('b').textContent = name;
  c.querySelector('small').textContent = desc || '';
  c.onclick = onOpen;
  return c;
}
function templateVars(data) {
  const found = new Set();
  const re = /\{\{\s*([\w ]+?)\s*\}\}/g;
  let m;
  const s = JSON.stringify(data);
  while ((m = re.exec(s))) found.add(m[1].trim());
  return [...found];
}
async function openTemplateWithVars(ref, name) {
  const [kind, id] = ref.split(':');
  const tpl = kind === 'builtin'
    ? await (await fetch('/api/templates/' + id)).json()
    : (await (await fetch('/api/templates/user')).json(), await (await fetch('/api/templates/user/' + id)).json());
  const data = tpl.document || tpl;
  const vars = templateVars(data);
  if (!vars.length) {
    pushHistory(); doc = data; libraryId = null; selectedId = null; layoutCache = null;
    markDirty(); renderAll(); saveLocal(); refreshLayout(); switchView('editor'); toastMsg(t('templateLoaded'), 'ok');
    return;
  }
  $('#wizTitle').textContent = name;
  const f = $('#wizFields'); f.innerHTML = '';
  const inputs = {};
  vars.forEach(v => {
    const l = document.createElement('label'); l.textContent = v;
    const i = document.createElement('input'); i.type = 'text';
    f.append(l, i); inputs[v] = i;
  });
  $('#wizModal').hidden = false;
  $('#wizClose').onclick = () => { $('#wizModal').hidden = true; };
  $('#wizStart').onclick = async () => {
    const values = {};
    Object.entries(inputs).forEach(([k, el]) => { values[k] = el.value; });
    const r = await fetch('/api/documents/fill', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ document: data, values }) });
    pushHistory(); doc = await r.json(); libraryId = null; selectedId = null; layoutCache = null;
    $('#wizModal').hidden = true;
    markDirty(); renderAll(); saveLocal(); refreshLayout(); switchView('editor'); toastMsg(t('templateLoaded'), 'ok');
  };
}
async function openLibraryDoc(id) {
  const full = await (await fetch('/api/library/' + id)).json();
  pushHistory(); doc = full; libraryId = id; selectedId = null;
  await loadComments();
  markDirty(); renderAll(); saveLocal(); refreshLayout(); switchView('editor'); toastMsg(t('loaded'), 'ok');
}
async function saveToLibrary() {
  try {
    const saved = await (await api('/api/library', doc)).json();
    doc.id = saved.id; libraryId = saved.id; saveLocal();
    await loadComments(); renderAll();
    toastMsg(t('saved'), 'ok');
  } catch (e) { toastMsg('Save failed: ' + e.message, 'err'); }
}

/* ================= import/export ================= */
function download(blob, name) {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 5000);
}
function fname(res, fallback) {
  const cd = res.headers.get('Content-Disposition') || '';
  return (cd.split('filename=')[1] || fallback).replace(/"/g, '');
}
async function exportPdf() {
  if (!(await showValidation())) { toastMsg(t('fixFirst'), 'err'); switchView('editor'); return; }
  try {
    const r = await api('/api/documents/pdf');
    download(await r.blob(), fname(r, 'document.pdf')); toastMsg(t('exported'), 'ok');
  } catch (e) { toastMsg('Export failed: ' + e.message, 'err'); }
}
async function exportMd() {
  const r = await api('/api/documents/markdown');
  download(await r.blob(), (doc.title || 'document').replace(/\s+/g, '-').slice(0, 40) + '.md');
  toastMsg(t('exported'), 'ok');
}
async function exportDocx() {
  if (!(await showValidation())) { toastMsg(t('fixFirst'), 'err'); return; }
  const r = await api('/api/documents/docx');
  download(await r.blob(), fname(r, 'document.docx')); toastMsg(t('exported'), 'ok');
}
function exportJson() {
  download(new Blob([JSON.stringify(doc, null, 2)], { type: 'application/json' }), (doc.title || 'document').replace(/\s+/g, '-').slice(0, 40) + '.json');
  toastMsg(t('exported'), 'ok');
}

/* ================= command palette ================= */
function palActions() {
  return [
    { label: t('save'), hint: 'Ctrl+S', run: saveToLibrary },
    { label: t('export') + ' PDF', hint: '', run: exportPdf },
    { label: t('export') + ' Markdown', hint: '', run: exportMd },
    { label: t('export') + ' DOCX', hint: '', run: exportDocx },
    { label: 'JSON ↓', hint: '', run: exportJson },
    { label: t('print'), hint: '', run: () => window.print() },
    { label: t('validate'), hint: '', run: () => { switchView('editor'); showValidation(); } },
    { label: t('history'), hint: '', run: () => { switchView('editor'); openHistory(); } },
    ...templates.map(x => ({ label: `${t('newFrom')}: ${x.name}`, hint: '', run: () => { openTemplateWithVars('builtin:' + x.id, x.name); switchView('editor'); } })),
    { label: t('goLibrary'), hint: '', run: () => switchView('library') },
    { label: t('goEditor'), hint: '', run: () => switchView('editor') },
    { label: `${t('theme')}: ${theme === 'light' ? 'dark' : 'light'}`, hint: '', run: () => { theme = theme === 'light' ? 'dark' : 'light'; applyTheme(); } },
    { label: `${t('language')}: ${lang === 'en' ? 'ES' : 'EN'}`, hint: '', run: () => setLang(lang === 'en' ? 'es' : 'en') },
    { label: t('undo') + ' (Ctrl+Z)', hint: '', run: undo },
    { label: t('redo') + ' (Ctrl+Y)', hint: '', run: redo },
    { label: t('zoomIn'), hint: '', run: () => { zoom += 0.1; applyZoom(); } },
    { label: t('zoomOut'), hint: '', run: () => { zoom -= 0.1; applyZoom(); } },
    { label: t('zoomReset'), hint: '', run: () => { zoom = 1; applyZoom(); } },
    ...BLOCK_DEFS.map(d => ({ label: `+ ${d.type} — ${d.hint}`, hint: '', run: () => { switchView('editor'); insertAfter(selectedId, d.type); } })),
  ];
}
let palIdx = 0;
function openPalette() {
  $('#palette').hidden = false;
  $('#palInput').value = ''; palIdx = 0; drawPalette('');
  setTimeout(() => $('#palInput').focus(), 0);
}
function closePalette() { $('#palette').hidden = true; }
function drawPalette(q) {
  const list = $('#palList'); list.innerHTML = '';
  const items = palActions().filter(a => a.label.toLowerCase().includes(q.toLowerCase()));
  palIdx = Math.max(0, Math.min(palIdx, items.length - 1));
  items.forEach((a, i) => {
    const b = document.createElement('button');
    if (i === palIdx) b.classList.add('active');
    b.innerHTML = `<span></span>${a.hint ? `<kbd>${esc(a.hint)}</kbd>` : ''}`;
    b.querySelector('span').textContent = a.label;
    b.onclick = () => { closePalette(); a.run(); };
    b.onmouseenter = () => { palIdx = i; list.querySelectorAll('button').forEach((x, j) => x.classList.toggle('active', j === i)); };
    list.appendChild(b);
  });
  list._items = items;
}

/* ================= render all / load / init ================= */
function renderAll() { docTitle.value = doc.title || ''; renderPreview(); renderPanel(); syncUndoBtns(); }
async function loadTemplate(id) {
  const d = await (await fetch('/api/templates/' + id)).json();
  if (doc) pushHistory();
  doc = d; libraryId = null; selectedId = null; layoutCache = null;
  commentsCache = [];
  markDirty(); renderAll(); saveLocal(); refreshLayout(); toastMsg(t('templateLoaded'), 'ok');
}
function setLang(l) { lang = l; localStorage.setItem('genpdf.lang', lang); applyI18n(); renderAll(); }
function applyI18n() {
  document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n); });
  document.querySelectorAll('[data-i18n-ph]').forEach(el => { el.placeholder = t(el.dataset.i18nPh); });
  $('#btnLang').textContent = lang.toUpperCase();
  $('#palInput').placeholder = t('palettePh');
  $('#tplName').placeholder = t('tplNamePh');
  $('#tplDesc').placeholder = t('tplDescPh');
  $('#libTag').options[0].textContent = t('allTags');
  if (doc) renderAll();
}
function undo() { if (!history.length) return; future.push(snap()); doc = JSON.parse(history.pop()); if (!byId(selectedId)) selectedId = null; markDirty(); renderAll(); saveLocal(); refreshLayout(); }
function redo() { if (!future.length) return; history.push(snap()); doc = JSON.parse(future.pop()); markDirty(); renderAll(); saveLocal(); refreshLayout(); }

const SHORTCUTS = [
  ['Ctrl/⌘ + K', 'Command palette'], ['Ctrl/⌘ + S', 'Save to library'], ['Ctrl/⌘ + Z', 'Undo'],
  ['Ctrl/⌘ + Y', 'Redo'], ['Ctrl/⌘ + B / I', 'Bold / italic (in text)'], ['Alt + ↑ / ↓', 'Move block'],
  ['/', 'Insert block menu'], ['?', 'This dialog'], ['Esc', 'Close dialog / menu'],
];

async function init() {
  applyTheme(); applyZoom();
  applyI18n();

  try {
    templates = await (await fetch('/api/templates')).json();
    tplSelect.innerHTML = '';
    templates.forEach(x => { const o = document.createElement('option'); o.value = x.id; o.textContent = x.name; tplSelect.appendChild(o); });
  } catch { toastMsg('Cannot reach API', 'err'); }

  const raw = localStorage.getItem('genpdf.doc.v1');
  if (raw) { try { const d = JSON.parse(raw); if (d && Array.isArray(d.blocks)) { doc = d; libraryId = localStorage.getItem('genpdf.libid') || null; } } catch { /* corrupted draft */ } }
  if (!doc) {
    try { doc = await (await fetch('/api/templates/acta')).json(); }
    catch { doc = { id: '', title: 'Untitled', company_name: '', show_page_numbers: true, page: { size: 'A4', orientation: 'P', margin_mm: 20 }, tags: [], favorite: false, status: 'draft', blocks: [] }; }
  }
  doc.page = doc.page || { size: 'A4', orientation: 'P', margin_mm: 20 };
  doc.tags = doc.tags || []; doc.status = doc.status || 'draft';
  await loadComments();
  renderAll(); refreshLayout();
  if (!localStorage.getItem('genpdf.hint')) $('#hintbar').hidden = false;
  $('#hintX').onclick = () => { $('#hintbar').hidden = true; localStorage.setItem('genpdf.hint', '1'); };

  docTitle.addEventListener('input', () => { doc.title = docTitle.value; markDirty(); saveLocal(); });
  docTitle.addEventListener('focusin', () => { focusSnapshot = snap(); });
  docTitle.addEventListener('focusout', () => { if (focusSnapshot && focusSnapshot !== snap()) pushHistory(focusSnapshot); focusSnapshot = null; });

  document.querySelectorAll('#toolbar [data-add]').forEach(btn => btn.addEventListener('click', () => insertAfter(selectedId, btn.dataset.add)));
  $('#fmtB').onclick = () => surround('**', '**');
  $('#fmtI').onclick = () => surround('*', '*');
  $('#fmtC').onclick = () => surround('`', '`');
  $('#zoomIn').onclick = () => { zoom += 0.1; applyZoom(); };
  $('#zoomOut').onclick = () => { zoom -= 0.1; applyZoom(); };

  $('#btnTpl').onclick = () => openTemplateWithVars('builtin:' + (tplSelect.value || 'blank'), tplSelect.selectedOptions[0]?.text || 'Template');
  $('#btnPdf').onclick = exportPdf;
  $('#btnSave').onclick = saveToLibrary;
  $('#btnTheme').onclick = () => { theme = theme === 'light' ? 'dark' : 'light'; applyTheme(); };
  $('#btnLang').onclick = () => setLang(lang === 'en' ? 'es' : 'en');
  $('#btnUndo').onclick = undo; $('#btnRedo').onclick = redo;
  $('#btnExportMenu').onclick = (e) => { e.stopPropagation(); $('#exportMenu').hidden = !$('#exportMenu').hidden; };
  document.querySelectorAll('#exportMenu [data-x]').forEach(b => b.onclick = () => {
    $('#exportMenu').hidden = true;
    ({ pdf: exportPdf, md: exportMd, docx: exportDocx, json: exportJson, imd: () => $('#fileMd').click(), idocx: () => $('#fileDocx').click(), ijson: () => $('#fileJson').click() })[b.dataset.x]();
  });

  document.querySelectorAll('#rail [data-view]').forEach(b => b.onclick = () => switchView(b.dataset.view));
  $('#libSearch').addEventListener('input', renderLib);
  $('#libSort').addEventListener('change', renderLib);
  $('#libTag').addEventListener('change', renderLib);
  $('#libStatus').addEventListener('change', renderLib);
  $('#libFav').onclick = () => { libFav = !libFav; renderLib(); };
  $('#libTrash').onclick = () => { libTrash = !libTrash; renderLib(); };
  $('#libNew').onclick = () => { loadTemplate('blank'); switchView('editor'); };
  $('#tplSave').onclick = async () => {
    const name = $('#tplName').value.trim() || doc.title;
    const r = await fetch('/api/templates/user', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, description: $('#tplDesc').value.trim(), document: doc }) });
    if (r.ok) { $('#tplName').value = ''; $('#tplDesc').value = ''; renderLib(); toastMsg(t('tplSaved'), 'ok'); }
  };

  const palInput = $('#palInput');
  palInput.addEventListener('input', () => { palIdx = 0; drawPalette(palInput.value); });
  palInput.addEventListener('keydown', e => {
    const items = $('#palList')._items || [];
    if (e.key === 'ArrowDown') { e.preventDefault(); palIdx = (palIdx + 1) % Math.max(1, items.length); drawPalette(palInput.value); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); palIdx = (palIdx + items.length - 1) % Math.max(1, items.length); drawPalette(palInput.value); }
    else if (e.key === 'Enter' && items[palIdx]) { closePalette(); items[palIdx].run(); }
    else if (e.key === 'Escape') closePalette();
  });
  $('#palette').addEventListener('click', e => { if (e.target.id === 'palette') closePalette(); });

  const keysList = $('#keysList');
  SHORTCUTS.forEach(([k, d]) => {
    const s = document.createElement('span'); s.textContent = d;
    const kb = document.createElement('span'); kb.innerHTML = `<kbd>${k}</kbd>`;
    keysList.append(s, kb);
  });
  const openKeys = () => { $('#keysModal').hidden = false; };
  $('#btnKeys').onclick = openKeys; $('#statusKeys').onclick = openKeys;
  $('#keysClose').onclick = () => { $('#keysModal').hidden = true; };
  $('#keysModal').addEventListener('click', e => { if (e.target.id === 'keysModal') $('#keysModal').hidden = true; });
  $('#histClose').onclick = () => { $('#histModal').hidden = true; };

  $('#fileMd').addEventListener('change', async e => {
    const f = e.target.files[0]; if (!f) return;
    const text = await f.text();
    const r = await fetch('/api/documents/import-markdown', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ markdown: text, title: f.name.replace(/\.[^.]+$/, '') }) });
    pushHistory(); doc = await r.json(); libraryId = null; selectedId = null;
    commentsCache = [];
    markDirty(); renderAll(); saveLocal(); refreshLayout(); toastMsg(t('imported'), 'ok'); e.target.value = '';
  });
  $('#fileDocx').addEventListener('change', async e => {
    const f = e.target.files[0]; if (!f) return;
    const fd = new FormData(); fd.append('file', f);
    const r = await fetch('/api/documents/import-docx', { method: 'POST', body: fd });
    if (!r.ok) { toastMsg('Import failed', 'err'); return; }
    pushHistory(); doc = await r.json(); libraryId = null; selectedId = null;
    commentsCache = [];
    markDirty(); renderAll(); saveLocal(); refreshLayout(); toastMsg(t('imported'), 'ok'); e.target.value = '';
  });
  $('#fileJson').addEventListener('change', async e => {
    const f = e.target.files[0]; if (!f) return;
    try {
      const data = JSON.parse(await f.text());
      const r = await fetch('/api/documents/validate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
      const v = await r.json();
      if (!v.ok) { toastMsg(v.errores.join(' '), 'err'); return; }
      pushHistory(); doc = data; libraryId = data.id || null; selectedId = null;
      await loadComments();
      markDirty(); renderAll(); saveLocal(); refreshLayout(); toastMsg(t('imported'), 'ok');
    } catch { toastMsg('Invalid JSON', 'err'); }
    e.target.value = '';
  });

  document.addEventListener('keydown', e => {
    const mod = e.ctrlKey || e.metaKey;
    const inText = document.activeElement?.classList?.contains('editable');
    if (mod && e.key.toLowerCase() === 'k') { e.preventDefault(); $('#palette').hidden ? openPalette() : closePalette(); return; }
    if (mod && e.key.toLowerCase() === 's') { e.preventDefault(); saveToLibrary(); return; }
    if (!$('#palette').hidden) return;
    if (e.altKey && (e.key === 'ArrowUp' || e.key === 'ArrowDown') && selectedId) {
      e.preventDefault(); shiftBlock(selectedId, e.key === 'ArrowUp' ? -1 : 1); return;
    }
    if (mod && e.key.toLowerCase() === 'b' && inText) { e.preventDefault(); surround('**', '**'); return; }
    if (mod && e.key.toLowerCase() === 'i' && inText) { e.preventDefault(); surround('*', '*'); return; }
    if (mod && e.key.toLowerCase() === 'z' && !e.shiftKey && !inText) { e.preventDefault(); undo(); return; }
    if (mod && (e.key.toLowerCase() === 'y' || (e.key.toLowerCase() === 'z' && e.shiftKey)) && !inText) { e.preventDefault(); redo(); return; }
    if (e.key === '?' && !inText && document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') openKeys();
  });
  sheet.addEventListener('dragover', e => { if (e.target === sheet) e.preventDefault(); });
  sheet.addEventListener('drop', e => {
    if (e.target !== sheet) return;
    e.preventDefault();
    const id = e.dataTransfer.getData('text/plain');
    if (id && idxOf(id) >= 0) { pushHistory(); const [b] = doc.blocks.splice(idxOf(id), 1); doc.blocks.push(b); markDirty(); renderAll(); saveLocal(); refreshLayout(); }
  });
  syncUndoBtns();
}
init();
