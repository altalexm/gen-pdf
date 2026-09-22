"""Tests for the genius round: security, audit, batch, import, cache, CLI."""
import base64
import io
import json
import zipfile

import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app import library
from app.cli import main as cli_main
from app.documents import acta_template
from app.images import (
    _host_is_public,
    load_image,
    load_raw,
    normalize,
)
from app.models import Document, migrate_document
from app.pdf import layout_cache_info, render_pdf
from app.pdf_import import pdf_to_document

client = TestClient(main_module.create_app())


@pytest.fixture(autouse=True)
def _isolated_library(tmp_path, monkeypatch):
    monkeypatch.setenv("GENPDF_DB", str(tmp_path / "lib.db"))
    yield


def _tiny_png_data_url(color=(255, 0, 0)):
    from PIL import Image
    img = Image.new("RGB", (40, 20), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# ---------- schema migration ----------

def test_migrate_v1_to_v2():
    d = {"title": "Old", "blocks": []}
    out = migrate_document(d)
    assert out["schema_version"] == 2
    doc = Document(**out)
    assert doc.theme.accent == "#4f46e5" and doc.schema_version == 2


# ---------- images: pipeline + SSRF ----------

def test_normalize_downscales_and_rejects():
    assert load_image(_tiny_png_data_url()) is not None
    assert load_image("data:image/png;base64,!!!") is None
    with pytest.raises(ValueError):
        load_raw("ftp://example.com/x.png")
    with pytest.raises(ValueError):
        load_raw("http://169.254.169.254/latest")
    with pytest.raises(ValueError):
        normalize(b"this is not an image at all" * 10)


def test_ssrf_private_hosts_rejected():
    assert _host_is_public("127.0.0.1") is False
    assert _host_is_public("localhost") is False
    assert _host_is_public("169.254.169.254") is False
    assert _host_is_public("10.0.0.5") is False
    assert _host_is_public("8.8.8.8") is True


def test_oversize_data_url_rejected():
    big = "data:image/png;base64," + "A" * (11 * 1024 * 1024)
    assert load_image(big) is None


# ---------- docx bomb guard ----------

def test_docx_zip_bomb_rejected(tmp_path):
    import struct

    from app import docx_io
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", b"<Types/>")
    raw = bytearray(buf.getvalue())
    # Spoof uncompressed sizes (local header @18, central dir @24)
    lh = raw.find(b"PK\x03\x04")
    raw[lh + 18:lh + 22] = struct.pack("<I", 500 * 1024 * 1024)
    ch = raw.find(b"PK\x01\x02")
    raw[ch + 24:ch + 28] = struct.pack("<I", 500 * 1024 * 1024)
    with pytest.raises(ValueError):
        docx_io._assert_safe_zip(bytes(raw))
    with pytest.raises(ValueError):
        docx_io.docx_to_document(b"not a zip at all")


# ---------- pdf import ----------

def test_pdf_import_roundtrip():
    pdf = render_pdf(acta_template())
    back = pdf_to_document(pdf, "Back")
    assert back.blocks
    assert any(b.type.value == "heading" for b in back.blocks)
    with pytest.raises(ValueError):
        pdf_to_document(b"garbage bytes here")


# ---------- batch zip + audit ----------

def test_batch_zip_and_audit():
    a = client.post("/api/library", json=acta_template().model_dump()).json()
    b = client.post("/api/library", json=acta_template().model_dump()).json()
    r = client.post("/api/documents/batch-pdf", json={"ids": [a["id"], b["id"]]})
    assert r.status_code == 200 and r.headers["content-type"] == "application/zip"
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        assert len(zf.namelist()) == 2
        assert zf.read(zf.namelist()[0])[:5] == b"%PDF-"
    assert client.post("/api/documents/batch-pdf", json={"ids": []}).status_code == 422
    client.patch(f"/api/library/{a['id']}/status", json={"status": "approved"})
    audit = client.get(f"/api/library/{a['id']}/audit").json()
    assert any(e["action"] == "status" for e in audit)


# ---------- token middleware ----------

def test_token_middleware(monkeypatch):
    monkeypatch.setattr(main_module, "API_TOKEN", "s3cret")
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/templates").status_code == 401
    authed = TestClient(main_module.create_app(), headers={"Authorization": "Bearer s3cret"})
    assert authed.get("/api/templates").status_code == 200


# ---------- layout cache ----------

def test_layout_cache_memoizes():
    from app import pdf as pdfmod
    pdfmod._LAYOUT_CACHE.clear()
    d = acta_template().model_dump()
    first = client.post("/api/documents/layout", json=d).json()
    assert layout_cache_info()["size"] == 1
    second = client.post("/api/documents/layout", json=d).json()
    assert first == second and layout_cache_info()["size"] == 1


# ---------- chart / toc / theme pdf ----------

def test_chart_toc_theme_pdf():
    d = acta_template().model_dump()
    d["show_header_title"] = True
    d["theme"] = {"accent": "#b91c1c", "heading_color": "#111111"}
    d["blocks"] += [
        {"id": "ch", "type": "chart", "chart": {"title": "Q", "points": [{"label": "A", "value": 5}, {"label": "B", "value": 0}]}},
        {"id": "t2", "type": "toc", "toc_depth": 1},
    ]
    r = client.post("/api/documents/pdf", json=d)
    assert r.status_code == 200 and r.content[:5] == b"%PDF-"
    assert b"/Annots" in r.content  # clickable TOC links
    html = client.post("/api/documents/preview", json=d).text
    assert "Q" in html


# ---------- CLI ----------

def test_cli_validate_pdf_markdown(tmp_path):
    src = tmp_path / "doc.json"
    src.write_text(json.dumps(acta_template().model_dump()), encoding="utf-8")
    assert cli_main(["validate", str(src)]) == 0
    assert cli_main(["pdf", str(src), "-o", str(tmp_path / "o.pdf")]) == 0
    assert (tmp_path / "o.pdf").read_bytes()[:5] == b"%PDF-"
    assert cli_main(["markdown", str(src), "-o", str(tmp_path / "o.md")]) == 0
    assert (tmp_path / "o.md").read_text().startswith("---")
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"title": "", "blocks": []}), encoding="utf-8")
    assert cli_main(["validate", str(bad)]) == 1


# ---------- migrate on read path ----------

def test_library_save_normalizes_enums():
    saved = library.save_document({"title": "E", "status": "draft", "blocks": []})
    raw = library.get_document(saved["id"])["document"]
    assert raw["status"] == "draft"
