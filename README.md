# gen-pdf

**Open-source visual PDF editor.** Edit absolutely everything inline, drag & drop blocks directly in the preview, and export a clean PDF. No installer, no updater, no lock-in — just a web app (or one Docker command).

![Python](https://img.shields.io/badge/python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688?logo=fastapi)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

- **Visual block editor** — 16 block types: heading, text, key-values, bullets, checklist, numbered sections, table, columns, chart, image, quote, code, toc, pagebreak, divider, signatures.
- **Edit in the preview** — click any text to edit it inline with `**bold**`, `*italic*`, `` `code` `` (Ctrl+B / Ctrl+I shortcuts); drag blocks by their ⠿ handle to reorder them; fold sections; document outline in the sidebar.
- **True A4 pagination** — the preview shows real page breaks computed by the same renderer that produces the PDF (memoized).
- **Property panel** — alignment, colors, themes, heading level, table grid editor (+CSV import), chart editor, image upload (auto-downscaled), page size/orientation/margins.
- **Library** — save, full-text search, duplicate and organize documents (SQLite FTS, zero-config); trash, tags, favorites, review states; version history with diff/restore; per-block comments with resolvable suggestions; activity log.
- **Import/export** — Markdown (frontmatter), DOCX and PDF both ways; one-click PDF/DOCX/JSON; batch ZIP; CLI (`python -m app.cli`).
- **Templates** — meeting minutes, NDA, blank + user templates with `{{variables}}` wizard. A new document type is just a template function.
- **Editor UX** — slash menu (`/`), command palette (Ctrl+K), find & replace, hover gutter actions, touch toolbar, zoom, dark mode, shortcuts dialog, live status bar (words/blocks/pages), stacked toasts, onboarding hint, PWA offline with outbox.
- **AI assist (BYOK)** — summarize, re-tone, action items, translate via any OpenAI-compatible API; your key never leaves the browser.
- **i18n** — English/Español toggle. Undo/redo, autosave draft + explicit library save.

## Quickstart

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# open http://localhost:8000
```

With Docker:

```bash
docker compose up   # library persisted in ./data
```

## API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Status + version |
| `GET` | `/api/templates` | Template catalog |
| `GET` | `/api/templates/{id}` | Default document for a template |
| `POST` | `/api/documents/validate` | `{ok, errores, avisos}` |
| `POST` | `/api/documents/preview` | Server-rendered HTML |
| `POST` | `/api/documents/pdf` | PDF file (`422` on blocking errors) |
| `POST` | `/api/documents/layout` | True pagination: page of every block |
| `GET/POST` | `/api/library[?q=&tag=&fav=&status=&trash=]` | List / save (filters, trash) |
| `GET` | `/api/library/tags` | Tags with counts |
| `GET/DELETE` | `/api/library/{id}[?hard=true]` | Get / trash / purge |
| `POST` | `/api/library/{id}/restore` | Restore from trash |
| `PATCH` | `/api/library/{id}/status` | `draft` / `in_review` / `approved` |
| `POST` | `/api/library/{id}/duplicate` | Duplicate |
| `GET` | `/api/library/{id}/versions` | Version history |
| `GET/POST` | `/api/library/{id}/versions/{vid}[/restore]` | Get / restore version |
| `POST` | `/api/documents/diff` | Unified diff of two documents |
| `GET/POST` | `/api/library/{id}/comments` | List / add comments |
| `PATCH/DELETE` | `/api/library/{id}/comments/{cid}` | Resolve-edit / delete |
| `GET` | `/api/templates/user` | User templates |
| `POST` | `/api/templates/user` | Save current doc as template |
| `POST` | `/api/documents/fill` | Substitute `{{variables}}` |
| `POST` | `/api/documents/markdown` | Export Markdown (with frontmatter) |
| `POST` | `/api/documents/import-markdown` | Parse Markdown → document |
| `POST` | `/api/documents/docx` | Export DOCX |
| `POST` | `/api/documents/import-docx` | Parse DOCX → document |
| `POST` | `/api/documents/import-pdf` | Parse PDF text layer → document |
| `POST` | `/api/documents/batch-pdf` | `{ids}` → ZIP of PDFs |
| `GET` | `/api/library/{id}/audit` | Activity log |

Library path: `data/library.db` (override with `GENPDF_DB`).
Optional API token: set `GENPDF_TOKEN` to require `Authorization: Bearer` on `/api/*` (except health).

## CLI

```bash
python -m app.cli validate doc.json
python -m app.cli pdf doc.json -o out.pdf
python -m app.cli markdown doc.json [-o out.md]
python -m app.cli docx doc.json -o out.docx
python -m app.cli layout doc.json
```

## Add a new document type

1. Add a builder in `app/documents.py` returning a `Document` (list of blocks).
2. Register it in `TEMPLATES`.
3. Add a test in `tests/test_api.py`.

No rebuild, no reinstall — reload the page and it's there. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full block-type checklist.

## Development

```bash
pip install -r requirements-dev.txt
pytest -q tests/test_api.py tests/test_genius.py tests/test_fuzz.py --cov=app --cov-fail-under=80
pytest -q tests/e2e           # browser smoke (needs: playwright install chromium)
ruff check app tests
```

Fuzz (`test_fuzz.py`) throws 100 seeded random documents (unicode, markdown,
odd sizes) at every renderer — it already caught a real Unicode crash once.

## AI assist, PWA, desktop

- **AI** is bring-your-own-key: open *✨ AI* from the palette, paste any OpenAI-compatible base URL + key + model. The key lives in `localStorage` and the browser calls the provider directly — your documents never pass through our server for this.
- **PWA**: `static/manifest.json` + `sw.js` (offline shell, API GET cache, mutation outbox replayed on reconnect).
- **Desktop**: `src-tauri/tauri.conf.json` wraps this same web app (needs the Rust toolchain).

## License

MIT — see [LICENSE](LICENSE). Contributions welcome via pull request.
