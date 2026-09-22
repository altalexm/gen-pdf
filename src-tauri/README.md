# gen-pdf desktop (Tauri stub)

This wraps the **same web app** as a native desktop shell — no rewrite.
Requires the Rust toolchain (`rustup`) and the Tauri CLI:

```bash
# 1. serve the backend (bundled alongside in production builds)
uvicorn app.main:app --port 8000

# 2. in another shell
cargo install tauri-cli
cd src-tauri
tauri dev      # dev window against http://localhost:8000
tauri build    # native installer
```

`tauri.conf.json` points `frontendDist` at `../static` and locks the
Content-Security-Policy to self + data/blob images + Google Fonts.
The Python backend is expected on localhost:8000 (bundle it with
e.g. PyInstaller sidecars or ship the server separately).
