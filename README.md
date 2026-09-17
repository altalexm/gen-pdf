# gen-pdf

**Open-source visual PDF editor.** Edit absolutely everything inline, drag & drop blocks directly in the preview, and export a clean PDF. No installer, no updater, no lock-in — just a web app (or one Docker command).

![Python](https://img.shields.io/badge/python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688?logo=fastapi)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

- **Visual block editor** — 12 block types: heading, text, key-values, bullets, checklist, numbered sections, table, image, quote, code, divider, signatures.
- **Edit in the preview** — click any text to edit it inline with `**bold**`, `*italic*`, `` `code` `` (Ctrl+B / Ctrl+I shortcuts); drag blocks by their ⠿ handle to reorder them.
- **True A4 pagination** — the preview shows real page breaks computed by the same renderer that produces the PDF.
- **Property panel** — alignment, colors, heading level, table grid editor, image upload, page size/orientation/margins.
- **Library** — save, search, duplicate and organize documents (SQLite, zero-config).
- **Import/export** — Markdown and DOCX both ways; PDF export in one click.
- **Templates** — meeting minutes, NDA, blank. A new document type is just a template function.
- **Editor UX** — slash menu (`/`), command palette (Ctrl+K), hover gutter actions, zoom, dark mode, shortcuts dialog, live status bar (words/blocks/pages), stacked toasts, onboarding hint.
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

Library path: `data/library.db` (override with `GENPDF_DB`).

## Add a new document type

1. Add a builder in `app/documents.py` returning a `Document` (list of blocks).
2. Register it in `TEMPLATES`.
3. Add a test in `tests/test_api.py`.

No rebuild, no reinstall — reload the page and it's there. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full block-type checklist.

## Development

```bash
pip install -r requirements-dev.txt
pytest -q tests/test_api.py   # fast API suite
pytest -q tests/e2e           # browser smoke (needs: playwright install chromium)
ruff check app tests
```

## License

MIT — see [LICENSE](LICENSE). Contributions welcome via pull request.
