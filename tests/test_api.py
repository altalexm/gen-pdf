import os

import pytest
from fastapi.testclient import TestClient

from app import library
from app.documents import acta_template, blank_template
from app.docx_io import docx_to_document
from app.main import create_app
from app.markdown import markdown_to_document
from app.models import BlockType, Document, validate_document

client = TestClient(create_app())


@pytest.fixture(autouse=True)
def _isolated_library(tmp_path, monkeypatch):
    monkeypatch.setenv("GENPDF_DB", str(tmp_path / "lib.db"))
    yield


def _doc_dict():
    return acta_template().model_dump()


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_templates_catalog_and_get():
    catalog = client.get("/api/templates").json()
    ids = {t["id"] for t in catalog}
    assert {"acta", "nda", "blank"} <= ids
    assert client.get("/api/templates/acta").json()["blocks"]
    assert client.get("/api/templates/nda").json()["blocks"]
    assert client.get("/api/templates/nope").status_code == 404


def test_validate_ok_and_blocking():
    assert client.post("/api/documents/validate", json=_doc_dict()).json()["ok"] is True
    bad = _doc_dict()
    bad["title"] = "   "
    body = client.post("/api/documents/validate", json=bad).json()
    assert body["ok"] is False and body["errores"]


def test_preview_html_renders_blocks_and_inline_md():
    d = _doc_dict()
    d["blocks"].append({"id": "x1", "type": "paragraph", "text": "**bold** and *italic*"})
    r = client.post("/api/documents/preview", json=d)
    assert r.status_code == 200
    assert "<strong>bold</strong>" in r.text and "<em>italic</em>" in r.text


def test_pdf_unicode_and_new_blocks():
    d = blank_template().model_dump()
    d["title"] = "Reunión — café niño 日本語"
    d["blocks"] = [
        {"id": "h", "type": "heading", "level": 1, "text": "Título **fuerte** con ñ y 日本語"},
        {"id": "q", "type": "quote", "text": "Cita *cursiva*"},
        {"id": "c", "type": "code", "text": "print('hola')"},
        {"id": "d", "type": "divider"},
        {"id": "t", "type": "table", "table": {"headers": ["A", "B"], "rows": [["1", "2"], ["3", "4"]]}},
        {"id": "k", "type": "checklist", "checklist": [{"text": "Hecho", "checked": True}, {"text": "Pte", "checked": False}]},
        {"id": "i", "type": "image", "image": {"src": "", "caption": ""}},
    ]
    r = client.post("/api/documents/pdf", json=d)
    assert r.status_code == 200
    assert r.content[:5] == b"%PDF-"
    assert len(r.content) > 3000
    bad = dict(d)
    bad["title"] = ""
    assert client.post("/api/documents/pdf", json=bad).status_code == 422


def test_layout_reports_true_pages():
    d = _doc_dict()
    d["blocks"] = d["blocks"] + [
        {"id": f"p{i}", "type": "paragraph", "text": "Lorem ipsum dolor sit amet. " * 40} for i in range(30)
    ]
    body = client.post("/api/documents/layout", json=d).json()
    assert body["pages"] >= 2
    assert body["blocks"][d["blocks"][0]["id"]] == 1


def test_library_crud_search_duplicate():
    assert client.get("/api/library").json() == []
    saved = client.post("/api/library", json=_doc_dict()).json()
    assert saved["id"]
    assert len(client.get("/api/library").json()) == 1
    assert len(client.get("/api/library", params={"q": "Acta"}).json()) == 1
    assert client.get("/api/library", params={"q": "zzz"}).json() == []
    dup = client.post(f"/api/library/{saved['id']}/duplicate").json()
    assert dup["id"] != saved["id"] and "(copy)" in dup["title"]
    assert len(client.get("/api/library").json()) == 2
    assert client.delete(f"/api/library/{saved['id']}").json() == {"ok": True}
    assert client.delete(f"/api/library/{saved['id']}").status_code == 404


def test_markdown_roundtrip():
    md = client.post("/api/documents/markdown", json=_doc_dict()).text
    assert md.startswith("---\ntitle: Acta")
    assert "\n# Acta" in md
    back = client.post("/api/documents/import-markdown", json={"markdown": md}).json()
    types = {b["type"] for b in back["blocks"]}
    assert {"heading", "keyvalue", "bullets", "sections", "signatures"} <= types

    sample = "# Doc\n\n- [x] Done\n- [ ] Todo\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n> quote\n\n```\ncode\n```\n\n---\n"
    parsed = markdown_to_document(sample, "T")
    types = {b.type for b in parsed.blocks}
    assert {BlockType.checklist, BlockType.table, BlockType.quote, BlockType.code, BlockType.divider} <= types


def test_docx_roundtrip():
    d = _doc_dict()
    d["blocks"].append({"id": "tbl", "type": "table",
                        "table": {"headers": ["A", "B"], "rows": [["1", "2"]]}})
    blob = client.post("/api/documents/docx", json=d).content
    assert blob[:2] == b"PK"
    back = docx_to_document(blob)
    assert back.blocks, "docx import should recover blocks"
    assert any(b.type == BlockType.table for b in back.blocks)


def test_validate_model_unit():
    doc = acta_template()
    doc.blocks = []
    assert validate_document(doc).ok is False


def test_library_module_direct():
    assert library.list_documents() == []
    saved = library.save_document(Document(title="Direct").model_dump())
    assert library.get_document(saved["id"])["title"] == "Direct"
    assert os.path.exists(os.environ["GENPDF_DB"])


def test_trash_restore_purge_and_filters():
    d = _doc_dict()
    d["title"] = "Tagged doc"
    d["tags"] = ["work", "urgent"]
    d["favorite"] = True
    saved = client.post("/api/library", json=d).json()
    assert client.get("/api/library", params={"tag": "work"}).json()
    assert client.get("/api/library", params={"fav": "1"}).json()
    assert client.get("/api/library", params={"tag": "nope"}).json() == []
    assert client.delete(f"/api/library/{saved['id']}").json() == {"ok": True}
    assert client.get("/api/library").json() == []
    assert len(client.get("/api/library", params={"trash": "1"}).json()) == 1
    assert client.post(f"/api/library/{saved['id']}/restore").json() == {"ok": True}
    assert len(client.get("/api/library").json()) == 1
    assert client.get("/api/library/tags").json()[0]["tag"] == "urgent"
    assert client.delete(f"/api/library/{saved['id']}", params={"hard": "true"}).json() == {"ok": True}
    assert client.get("/api/library", params={"trash": "1"}).json() == []


def test_versions_and_diff_and_restore():
    d = _doc_dict()
    saved = client.post("/api/library", json=d).json()
    doc_id = saved["id"]
    d["id"] = doc_id
    d["title"] = "Edited title"
    client.post("/api/library", json=d)
    versions = client.get(f"/api/library/{doc_id}/versions").json()
    assert len(versions) >= 2
    oldest = versions[-1]["id"]
    body = client.post("/api/documents/diff", json={"a": client.get(f"/api/library/{doc_id}/versions/{oldest}").json()["data"], "b": d}).json()
    assert "Edited title" in body["diff"]
    restored = client.post(f"/api/library/{doc_id}/versions/{oldest}/restore").json()
    assert restored["title"] != "Edited title"


def test_comments_flow_and_status():
    saved = client.post("/api/library", json=_doc_dict()).json()
    doc_id = saved["id"]
    c = client.post(f"/api/library/{doc_id}/comments",
                    json={"block_id": "b1", "author": "QA", "text": "Check this"}).json()
    assert c["id"]
    assert len(client.get(f"/api/library/{doc_id}/comments").json()) == 1
    assert client.get(f"/api/library/{doc_id}/comments", params={"open_only": "true"}).json()
    updated = client.patch(f"/api/library/{doc_id}/comments/{c['id']}", json={"resolved": True}).json()
    assert updated["resolved"] is True
    assert client.get(f"/api/library/{doc_id}/comments", params={"open_only": "true"}).json() == []
    assert client.patch(f"/api/library/{doc_id}/status", json={"status": "approved"}).json()["document"]["status"] == "approved"
    assert client.patch(f"/api/library/{doc_id}/status", json={"status": "bogus"}).status_code == 422
    assert client.delete(f"/api/library/{doc_id}/comments/{c['id']}").json() == {"ok": True}


def test_user_templates_and_fill():
    d = _doc_dict()
    d["blocks"].append({"id": "v", "type": "paragraph", "text": "Signed by {{party}} on {{date}}."})
    meta = client.post("/api/templates/user",
                       json={"name": "Mine", "description": "d", "document": d}).json()
    assert meta["id"]
    assert any(x["id"] == meta["id"] for x in client.get("/api/templates/user").json())
    assert client.get(f"/api/templates/user/{meta['id']}").json()["title"]
    filled = client.post("/api/documents/fill",
                         json={"document": d, "values": {"party": "Acme", "date": "today"}}).json()
    assert "Signed by Acme on today." in filled["blocks"][-1]["text"]
    assert "Signed by {{party}}" in client.post(
        "/api/documents/fill", json={"document": d, "values": {}}).json()["blocks"][-1]["text"]
    assert client.delete(f"/api/templates/user/{meta['id']}").json() == {"ok": True}


def test_layout_blocks_columns_toc_pagebreak_pdf():
    d = blank_template().model_dump()
    d["title"] = "Layout"
    d["blocks"] = [
        {"id": "h1", "type": "heading", "level": 1, "text": "Start"},
        {"id": "t", "type": "toc", "toc_depth": 2},
        {"id": "c", "type": "columns", "columns": [{"title": "L", "text": "left"}, {"title": "R", "text": "right"}]},
        {"id": "pb", "type": "pagebreak"},
        {"id": "h2", "type": "heading", "level": 2, "text": "After break"},
    ]
    body = client.post("/api/documents/layout", json=d).json()
    assert body["pages"] >= 2 and body["blocks"]["h2"] >= 2
    r = client.post("/api/documents/pdf", json=d)
    assert r.status_code == 200 and r.content[:5] == b"%PDF-"
    assert "Table of contents" in client.post("/api/documents/preview", json=d).text or "Start" in client.post("/api/documents/preview", json=d).text


def test_signature_drawing_pdf_and_fts_content():
    d = _doc_dict()
    d["blocks"][0]["text"] = "Zebra stripes unique word qzxw"
    saved = client.post("/api/library", json=d).json()
    assert client.get("/api/library", params={"q": "qzxw"}).json()

    import base64
    import io as _io
    from PIL import Image
    img = Image.new("RGB", (60, 20), "white")
    buf = _io.BytesIO()
    img.save(buf, format="PNG")
    drawing = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    sig = next(b for b in d["blocks"] if b["type"] == "signatures")
    sig["left"]["drawing"] = drawing
    r = client.post("/api/documents/pdf", json=d)
    assert r.status_code == 200 and len(r.content) > 3000
    assert saved["id"]
