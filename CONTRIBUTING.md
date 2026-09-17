# Contributing to gen-pdf

Thanks for stopping by! This is a small, friendly open-source project. Issues and pull requests are welcome.

## Quickstart

```bash
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload   # http://localhost:8000
pytest -q
ruff check app tests
```

Or with Docker:

```bash
docker compose up   # http://localhost:8000 (library persisted in ./data)
```

## How the project is organized

- `app/models.py` — `Block` / `Document` schemas. **The block list is the single source of truth** for preview and PDF.
- `app/documents.py` — built-in templates. A new document type = one builder + one registry entry.
- `app/pdf.py` — fpdf2 rendering (DejaVu fonts bundled in `app/fonts/`). Every block type must render here.
- `app/markdown.py`, `app/docx_io.py` — lossy-but-practical format bridges.
- `app/library.py` — SQLite persistence (`GENPDF_DB` env var overrides the path).
- `static/` — vanilla-JS visual editor (no build step on purpose).

## Rules for a new block type

1. Add the variant to `BlockType` + fields to `Block` in `app/models.py`.
2. Render it in `app/pdf.py::_render_block` (keep `new_x/new_y` cursor discipline — see `_NL`).
3. Render it in `app/templates/preview.html` and in `static/app.js::blockEl` (+ property panel).
4. Map it in `app/markdown.py` both directions (or document why it can't round-trip).
5. Add tests in `tests/test_api.py`.

## Pull requests

- Keep PRs small and focused; one feature per PR.
- `pytest -q` and `ruff check app tests` must pass (CI enforces it).
- Update `CHANGELOG.md` under `Unreleased`.
