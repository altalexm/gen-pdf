# Changelog — gen-pdf

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.1.0] - 2026-09-16

### Added

- Open-source reboot as **gen-pdf** (MIT): visual block editor over FastAPI.
- Block model (`heading`, `paragraph`, `keyvalue`, `bullets`, `sections`, `signatures`) with server-side PDF rendering from the same block list shown in the preview.
- Inline editing + drag & drop reorder directly in the preview, property panel, undo/redo, duplicate, autosave.
- Templates: meeting minutes, NDA, blank.
- REST API: health, templates, validate, preview, pdf. Test suite + GitHub Actions CI.
