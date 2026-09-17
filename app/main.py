"""gen-pdf API: templates, library, import/export and PDF rendering."""
from __future__ import annotations

import re
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from . import __version__ as APP_VERSION
from . import library
from .documents import TEMPLATES
from .docx_io import document_to_docx, docx_to_document
from .markdown import document_to_markdown, markdown_to_document
from .models import Document
from .models import validate_document as _validate
from .pdf import layout as _layout
from .pdf import prepare_preview as _prepare_preview
from .pdf import render_pdf

BASE = Path(__file__).parent
jinja = Environment(
    loader=FileSystemLoader(str(BASE / "templates")),
    autoescape=select_autoescape(["html"]),
)


def _inline_md(value: object) -> Markup:
    """Escape HTML, then render the **bold** / *italic* / `code` subset."""
    import html as _html

    s = _html.escape(str(value or ""))
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return Markup(s)


jinja.filters["md"] = _inline_md


def _slug(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", (text or "document").strip()).strip("-")[:40]
    return slug or "document"


def create_app() -> FastAPI:
    app = FastAPI(title="gen-pdf", version=APP_VERSION)

    @app.get("/api/health")
    def health():
        return {"status": "ok", "version": APP_VERSION}

    @app.get("/api/templates")
    def templates():
        return [{"id": t["id"], "name": t["name"], "description": t["description"]} for t in TEMPLATES.values()]

    # ---- user templates (registered BEFORE /{template_id}: FastAPI matches in order) ----
    @app.get("/api/templates/user")
    def user_templates():
        return library.list_user_templates()

    @app.get("/api/templates/user/{template_id}")
    def user_template_get(template_id: str):
        found = library.get_user_template(template_id)
        if not found:
            raise HTTPException(status_code=404, detail="Not found")
        return found["document"]

    @app.post("/api/templates/user")
    def user_template_save(body: dict):
        doc = Document(**body.get("document", {}))
        return library.save_user_template(body.get("name", doc.title),
                                          body.get("description", ""), doc.model_dump())

    @app.delete("/api/templates/user/{template_id}")
    def user_template_delete(template_id: str):
        if not library.delete_user_template(template_id):
            raise HTTPException(status_code=404, detail="Not found")
        return {"ok": True}

    @app.get("/api/templates/{template_id}", response_model=Document)
    def get_template(template_id: str):
        tpl = TEMPLATES.get(template_id)
        if not tpl:
            raise HTTPException(status_code=404, detail=f"Unknown template '{template_id}'")
        return tpl["build"]()

    @app.post("/api/documents/validate")
    def validate(doc: Document):
        return _validate(doc).model_dump()

    @app.post("/api/documents/preview", response_class=HTMLResponse)
    def preview(doc: Document):
        doc, pages = _prepare_preview(doc)
        return jinja.get_template("preview.html").render(doc=doc, pages=pages)

    @app.post("/api/documents/pdf")
    def export_pdf(doc: Document):
        result = _validate(doc)
        if not result.ok:
            raise HTTPException(status_code=422, detail=result.errores)
        return Response(
            content=render_pdf(doc),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{_slug(doc.title)}.pdf"'},
        )

    @app.post("/api/documents/layout")
    def layout(doc: Document):
        """True pagination: real page number of every block (same renderer as the PDF)."""
        return _layout(doc)

    # ---- library ----
    @app.get("/api/library")
    def library_list(q: str = Query(default=""), tag: str = Query(default=""),
                     fav: bool = Query(default=False), status: str = Query(default=""),
                     trash: bool = Query(default=False)):
        return library.list_documents(query=q, tag=tag, favorites_only=fav,
                                      status=status, include_deleted=trash)

    @app.get("/api/library/tags")
    def library_tags():
        return library.all_tags()

    @app.post("/api/library")
    def library_save(doc: Document):
        return library.save_document(doc.model_dump())

    @app.get("/api/library/{doc_id}")
    def library_get(doc_id: str):
        found = library.get_document(doc_id)
        if not found:
            raise HTTPException(status_code=404, detail="Not found")
        return found["document"]

    @app.post("/api/library/{doc_id}/duplicate")
    def library_duplicate(doc_id: str):
        dup = library.duplicate_document(doc_id)
        if not dup:
            raise HTTPException(status_code=404, detail="Not found")
        return dup

    @app.delete("/api/library/{doc_id}")
    def library_delete(doc_id: str, hard: bool = Query(default=False)):
        ok = library.purge_document(doc_id) if hard else library.soft_delete(doc_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Not found")
        return {"ok": True}

    @app.post("/api/library/{doc_id}/restore")
    def library_restore(doc_id: str):
        if not library.restore_document(doc_id):
            raise HTTPException(status_code=404, detail="Not found")
        return {"ok": True}

    @app.patch("/api/library/{doc_id}/status")
    def library_status(doc_id: str, body: dict):
        found = library.get_document(doc_id)
        if not found:
            raise HTTPException(status_code=404, detail="Not found")
        data = found["document"]
        if body.get("status") not in ("draft", "in_review", "approved"):
            raise HTTPException(status_code=422, detail="Invalid status")
        data["status"] = body["status"]
        return library.save_document(data)

    # ---- versions ----
    @app.get("/api/library/{doc_id}/versions")
    def version_list(doc_id: str):
        return library.list_versions(doc_id)

    @app.get("/api/library/{doc_id}/versions/{version_id}")
    def version_get(doc_id: str, version_id: str):
        v = library.get_version(doc_id, version_id)
        if not v:
            raise HTTPException(status_code=404, detail="Not found")
        return v

    @app.post("/api/library/{doc_id}/versions/{version_id}/restore")
    def version_restore(doc_id: str, version_id: str):
        data = library.restore_version(doc_id, version_id)
        if not data:
            raise HTTPException(status_code=404, detail="Not found")
        return data["document"]

    @app.post("/api/documents/diff")
    def diff_docs(body: dict):
        a = Document(**body.get("a", {})).model_dump()
        b = Document(**body.get("b", {})).model_dump()
        old = document_to_markdown(Document(**a))
        new = document_to_markdown(Document(**b))
        return {"diff": library.diff_texts(old, new)}

    # ---- comments ----
    @app.get("/api/library/{doc_id}/comments")
    def comment_list(doc_id: str, open_only: bool = Query(default=False)):
        return library.list_comments(doc_id, include_resolved=not open_only)

    @app.post("/api/library/{doc_id}/comments")
    def comment_add(doc_id: str, body: dict):
        if not (body.get("text") or "").strip():
            raise HTTPException(status_code=422, detail="Empty comment")
        return library.add_comment(doc_id, body.get("block_id", ""), body.get("author", ""), body["text"])

    @app.patch("/api/library/{doc_id}/comments/{comment_id}")
    def comment_update(doc_id: str, comment_id: str, body: dict):
        updated = library.update_comment(doc_id, comment_id, text=body.get("text"),
                                         resolved=body.get("resolved"))
        if not updated:
            raise HTTPException(status_code=404, detail="Not found")
        return updated

    @app.delete("/api/library/{doc_id}/comments/{comment_id}")
    def comment_delete(doc_id: str, comment_id: str):
        if not library.delete_comment(doc_id, comment_id):
            raise HTTPException(status_code=404, detail="Not found")
        return {"ok": True}

    # ---- user templates + variables ----

    @app.post("/api/documents/fill", response_model=Document)
    def fill_document(body: dict):
        """Substitute {{variables}} across every string field of the document."""
        doc = Document(**body.get("document", {}))
        values = {str(k): str(v) for k, v in (body.get("values") or {}).items()}
        import json as _json

        def _sub(node):
            if isinstance(node, str):
                def _rep(m):
                    return values.get(m.group(1).strip(), m.group(0))
                return re.sub(r"\{\{\s*([\w ]+?)\s*\}\}", _rep, node)
            if isinstance(node, list):
                return [_sub(x) for x in node]
            if isinstance(node, dict):
                return {k: _sub(v) for k, v in node.items()}
            return node

        return Document(**_sub(_json.loads(doc.model_dump_json())))

    # ---- markdown ----
    @app.post("/api/documents/markdown", response_class=PlainTextResponse)
    def export_markdown(doc: Document):
        return document_to_markdown(doc)

    @app.post("/api/documents/import-markdown", response_model=Document)
    def import_markdown(body: dict):
        return markdown_to_document(body.get("markdown", ""), body.get("title", "Imported document"))

    # ---- docx ----
    @app.post("/api/documents/docx")
    def export_docx(doc: Document):
        return Response(
            content=document_to_docx(doc),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{_slug(doc.title)}.docx"'},
        )

    @app.post("/api/documents/import-docx", response_model=Document)
    async def import_docx(file: UploadFile = File(...)):  # noqa: B008 (FastAPI idiom)
        data = await file.read()
        if len(data) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large (max 10 MB)")
        try:
            return docx_to_document(data, file.filename or "Imported document")
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Could not parse DOCX: {e}") from e

    static_dir = BASE.parent / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app


app = create_app()
