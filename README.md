# gen-pdf

**Open-source visual PDF editor.** Edit absolutely everything inline, drag & drop blocks directly in the preview, and export a clean PDF. No installer, no updater, no lock-in — just a web app.

![Python](https://img.shields.io/badge/python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688?logo=fastapi)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

- **Visual block editor** — every piece of the document is a block (heading, paragraph, key-value, bullets, numbered sections, signatures).
- **Edit in the preview** — click any text to edit it inline; drag blocks by their handle to reorder them.
- **Property panel** — alignment, heading level, add/remove rows, items and entries per block.
- **Templates** — meeting minutes, NDA, blank. A new document type is just a template function, no client rebuild.
- **One-click PDF export** — the server renders the exact block list you see.
- **Undo/redo** (Ctrl+Z / Ctrl+Y), duplicate, autosave to `localStorage`.

## Quickstart

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# open http://localhost:8000
```

## API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Status + version |
| `GET` | `/api/templates` | Template catalog |
| `GET` | `/api/templates/{id}` | Default document for a template |
| `POST` | `/api/documents/validate` | `{ok, errores}` |
| `POST` | `/api/documents/preview` | Server-rendered HTML |
| `POST` | `/api/documents/pdf` | PDF file (`422` on blocking errors) |

## Add a new document type

1. Add a builder in `app/documents.py` returning a `Document` (list of blocks).
2. Register it in `TEMPLATES`.
3. Add a test in `tests/test_api.py`.

No rebuild, no reinstall — reload the page and it's there.

## Development

```bash
pip install -r requirements-dev.txt
pytest -q
ruff check app tests static 2>/dev/null || ruff check app tests
```

## License

MIT — see [LICENSE](LICENSE). Contributions welcome via pull request.
