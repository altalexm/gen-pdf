# Changelog — gen-pdf

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Changed

- Full visual redesign: workspace sidebar (search, recents, templates, trash), slim blurred topbar, collapsible inspector, warm-paper canvas, Inter type, refined dark mode, loading skeletons, print-safe chrome.

### Added

- New blocks: `columns` (up to 3), `pagebreak`, `toc` (auto entries with real page numbers, two-pass render).
- Hand-drawn signatures: canvas pad (mouse + touch) embedded as PNG in the PDF.
- Version history: auto-snapshots on save, timeline, unified diff vs current, one-click restore.
- Trash (soft-delete/restore/purge), tags, favorites, review status (`draft/in_review/approved`).
- FTS5 full-text search across the library (title + content), tag filters.
- Per-block comments: threads, resolve/reopen, badges in the editor gutter.
- User templates + `{{variables}}` wizard with live `/fill` substitution.
- JSON export/import, browser print stylesheet, block converter, Alt+↑/↓ to move blocks.
- Playwright E2E smoke (home, edit→PDF download, slash→table, library round-trip) + CI job.
- Inline rich text: `**bold**`, `*italic*`, `` `code` `` in preview, server HTML and PDF (Ctrl+B / Ctrl+I shortcuts, toolbar buttons).
- True A4 pagination: `POST /api/documents/layout` reports the real page of every block; the preview shows page separators.
- PDF pro: embedded DejaVu Unicode fonts (no more `?` degradation), page size/orientation/margins, block colors.
- Document library (SQLite): save/search/duplicate/delete + frontend overlay.
- Markdown and DOCX import/export (both directions).
- Frontend i18n (EN/ES), image upload as data-URL, table grid editor.
- Open-source pack: `CONTRIBUTING.md`, issue/PR templates, `Dockerfile` + compose, expanded `README`.
- UX overhaul: app shell (icon rail, views, status bar), slash menu, command palette (Ctrl+K), hover gutter actions, canvas zoom, dark mode, shortcuts dialog, stacked toasts, onboarding hint, library as a full view with sort.

## [0.1.0] - 2026-09-16

### Added

- Open-source reboot as **gen-pdf** (MIT): visual block editor over FastAPI.
- Block model (`heading`, `paragraph`, `keyvalue`, `bullets`, `sections`, `signatures`) with server-side PDF rendering from the same block list shown in the preview.
- Inline editing + drag & drop reorder directly in the preview, property panel, undo/redo, duplicate, autosave.
- Templates: meeting minutes, NDA, blank.
- REST API: health, templates, validate, preview, pdf. Test suite + GitHub Actions CI.
