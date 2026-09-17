from fastapi.testclient import TestClient

from app.documents import acta_template
from app.main import create_app
from app.models import validate_document

client = TestClient(create_app())


def _doc_dict():
    return acta_template().model_dump()


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_templates_catalog_and_get():
    catalog = client.get("/api/templates").json()
    ids = {t["id"] for t in catalog}
    assert {"acta", "nda", "blank"} <= ids
    for tid in ("acta", "nda", "blank"):
        r = client.get(f"/api/templates/{tid}")
        assert r.status_code == 200
        assert r.json()["blocks"], tid
    assert client.get("/api/templates/nope").status_code == 404


def test_validate_ok_and_blocking():
    assert client.post("/api/documents/validate", json=_doc_dict()).json()["ok"] is True
    bad = _doc_dict()
    bad["title"] = "   "
    body = client.post("/api/documents/validate", json=bad).json()
    assert body["ok"] is False and body["errores"]


def test_preview_html_renders_blocks():
    r = client.post("/api/documents/preview", json=_doc_dict())
    assert r.status_code == 200
    assert "Acta de Reuni" in r.text and "Firmas" in r.text


def test_pdf_ok_starts_with_pdf_magic_and_422():
    r = client.post("/api/documents/pdf", json=_doc_dict())
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:5] == b"%PDF-"
    bad = _doc_dict()
    bad["title"] = ""
    assert client.post("/api/documents/pdf", json=bad).status_code == 422


def test_validate_model_unit():
    doc = acta_template()
    doc.blocks = []
    result = validate_document(doc)
    assert result.ok is False
