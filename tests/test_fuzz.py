"""Property-style fuzz: random documents must never crash any renderer."""
import random

import pytest

from app.docx_io import document_to_docx
from app.markdown import document_to_markdown, markdown_to_document
from app.models import Document
from app.pdf import layout, render_pdf
from app.models import validate_document as _validate

WORDS = ["alpha", "beta", "Reunión", "café", "日本語", "**bold**", "*it*", "`code`",
         "a" * 200, "", "  ", "line1\nline2", "<b>html?</b>", "100% & <half>"]


def random_block(rng, i):
    t = rng.choice(["heading", "paragraph", "quote", "code", "divider", "keyvalue",
                    "bullets", "checklist", "sections", "signatures", "table",
                    "image", "columns", "pagebreak", "toc", "chart"])
    b = {"id": f"b{i}", "type": t}

    def w():
        return rng.choice(WORDS)

    if t == "heading":
        b.update(level=rng.randint(1, 3), text=w(), align=rng.choice(["left", "center", "right"]))
    elif t in ("paragraph", "quote", "code"):
        b.update(text=w())
    elif t == "keyvalue":
        b["rows"] = [{"label": w(), "value": w()} for _ in range(rng.randint(0, 3))]
    elif t == "bullets":
        b["items"] = [w() for _ in range(rng.randint(0, 4))]
    elif t == "checklist":
        b["checklist"] = [{"text": w(), "checked": rng.random() < 0.5} for _ in range(rng.randint(0, 3))]
    elif t == "sections":
        b["entries"] = [{"title": w(), "text": w()} for _ in range(rng.randint(0, 2))]
    elif t == "signatures":
        b.update(left={"name": w(), "role": w(), "drawing": ""},
                 right={"name": w(), "role": w(), "drawing": ""})
    elif t == "table":
        n = rng.randint(0, 4)
        b["table"] = {"headers": [w() for _ in range(n)],
                      "rows": [[w() for _ in range(n)] for _ in range(rng.randint(0, 3))]}
    elif t == "image":
        b["image"] = {"src": "", "caption": w(), "width_pct": rng.choice([10, 80, 100])}
    elif t == "columns":
        b["columns"] = [{"title": w(), "text": w()} for _ in range(rng.randint(0, 4))]
    elif t == "toc":
        b["toc_depth"] = rng.randint(1, 3)
    elif t == "chart":
        b["chart"] = {"title": w(), "points": [
            {"label": w(), "value": rng.choice([0, 5, -3, 100.5])} for _ in range(rng.randint(0, 4))]}
    return b


def random_doc(seed):
    rng = random.Random(seed)
    return {"title": rng.choice(WORDS), "company_name": rng.choice(WORDS),
            "show_page_numbers": rng.random() < 0.5,
            "page": {"size": rng.choice(["A4", "Letter"]),
                     "orientation": rng.choice(["P", "L"]),
                     "margin_mm": rng.choice([10, 20, 40])},
            "blocks": [random_block(rng, i) for i in range(rng.randint(0, 12))]}


def test_fuzz_never_crashes():
    import pydantic

    # Invalid input must fail loudly with ValidationError, never silently.
    with pytest.raises(pydantic.ValidationError):
        Document(**{**random_doc(0), "page": {"size": "A4", "orientation": "P", "margin_mm": 5}})
    for seed in range(100):
        raw = random_doc(seed)
        doc = Document(**raw)  # must validate (pydantic coerces/clamps)
        _validate(doc)
        pdf = render_pdf(doc)
        assert pdf[:5] == b"%PDF-"
        info = layout(doc)
        assert info["pages"] >= 1
        md = document_to_markdown(doc)
        assert isinstance(md, str) and md.endswith("\n")
        markdown_to_document(md)  # must not crash
        blob = document_to_docx(doc)
        assert blob[:2] == b"PK"


def test_preview_renders_every_block_type(client=None):
    import base64
    import io as _io

    from fastapi.testclient import TestClient
    from PIL import Image

    from app.main import create_app
    buf = _io.BytesIO()
    Image.new("RGB", (8, 8), "white").save(buf, format="PNG")
    tiny = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    c = TestClient(create_app())
    blocks = []
    for i, t in enumerate(["heading", "paragraph", "quote", "code", "divider", "keyvalue",
                           "bullets", "checklist", "sections", "signatures", "table",
                           "image", "columns", "pagebreak", "toc", "chart"]):
        b = {"id": f"g{i}", "type": t, "text": "T", "level": 1,
             "rows": [{"label": "L", "value": "V"}], "items": ["i"],
             "entries": [{"title": "ET", "text": "ED"}],
             "left": {"name": "N", "role": "R"}, "right": {"name": "N2", "role": "R2"},
             "table": {"headers": ["H"], "rows": [["C"]]},
             "image": {"src": tiny, "caption": "cap", "width_pct": 80},
             "columns": [{"title": "CT", "text": "CX"}], "toc_depth": 2,
             "chart": {"title": "CH", "points": [{"label": "A", "value": 3}]},
             "checklist": [{"text": "CK", "checked": True}]}
        blocks.append(b)
    html = c.post("/api/documents/preview", json={"title": "G", "blocks": blocks}).text
    for marker in ["T", "L:", "CK", "ET", "CH", "cap", "CT", 'class="toc"', "Page break"]:
        assert marker in html, marker
