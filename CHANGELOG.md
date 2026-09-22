# Changelog — gen-pdf

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Changed

- Full visual redesign: workspace sidebar (search, recents, templates, trash), slim blurred topbar, collapsible inspector, warm-paper canvas, Inter type, refined dark mode, loading skeletons, print-safe chrome.
- Mobile-first pass: drawer below the topbar with scrim, inspector as bottom sheet, floating touch toolbar (move/duplicate/delete/insert), stacked key-values, scrollable tables, compact status bar, 40px+ touch targets.

### Fixed

- Collapsed panels can no longer intercept pointer events (delayed `visibility`).
- Inspector no longer covers the canvas on load in narrow viewports.
- Mobile drawer and bottom sheet are mutually exclusive; drawer sits below the topbar with scrim; Export stays visible in a two-row topbar; sheet gets a grab handle.
- Code blocks no longer crash the PDF on non-latin text (DejaVu instead of core Courier) — caught by the new fuzzer.
- `save_document` normalizes through the model so `str(Enum)` values (e.g. `'DocStatus.draft'`) can never leak into storage.
- Static `/api/templates/user*` routes no longer shadowed by `/{template_id}` (registration order).

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
- Chart block (SVG preview, vector PDF), document outline + section folding, find & replace, CSV→table import, reusable snippets, comments convertible to applied suggestions.
- Themes (accent/headings), running header title, clickable TOC with dot leaders + PDF bookmarks.
- Library activity log, batch PDF→ZIP export, PDF text-layer import, `python -m app.cli`, optional `GENPDF_TOKEN` bearer auth.
- Hardening: SSRF-safe image pipeline (private-IP deny, caps, Pillow re-encode), DOCX zip-bomb guard, schema versioning with migrations, memoized layout.
- AI assist BYOK (browser-direct, key never leaves localStorage), PWA offline (shell cache + outbox), Tauri desktop stub.
- Quality: seeded fuzz over all renderers, all-blocks preview contract test, coverage gate (80%), Playwright E2E.
- UX overhaul: app shell (icon rail, views, status bar), slash menu, command palette (Ctrl+K), hover gutter actions, canvas zoom, dark mode, shortcuts dialog, stacked toasts, onboarding hint, library as a full view with sort.
- UI QA round: inspector hidden on load in narrow viewports, shortcuts work while editing, single-row scrollable toolbar, dashed empty-image placeholder, no dead Alignment control on table/toc/pagebreak/divider, inline author field for comments.

## [0.1.0] - 2026-09-16

### Added

- Open-source reboot as **gen-pdf** (MIT): visual block editor over FastAPI.
- Block model (`heading`, `paragraph`, `keyvalue`, `bullets`, `sections`, `signatures`) with server-side PDF rendering from the same block list shown in the preview.
- Inline editing + drag & drop reorder directly in the preview, property panel, undo/redo, duplicate, autosave.
- Templates: meeting minutes, NDA, blank.
- REST API: health, templates, validate, preview, pdf. Test suite + GitHub Actions CI.
