"""gen-pdf API: templates + generic document endpoints."""
from __future__ import annotations

import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import __version__ as APP_VERSION
from .documents import TEMPLATES
from .models import Document, validate_document
from .pdf import render_pdf

BASE = Path(__file__).parent
jinja = Environment(
    loader=FileSystemLoader(str(BASE / "templates")),
    autoescape=select_autoescape(["html"]),
)


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

    @app.get("/api/templates/{template_id}", response_model=Document)
    def get_template(template_id: str):
        tpl = TEMPLATES.get(template_id)
        if not tpl:
            raise HTTPException(status_code=404, detail=f"Unknown template '{template_id}'")
        return tpl["build"]()

    @app.post("/api/documents/validate")
    def validate(doc: Document):
        return validate_document(doc).model_dump()

    @app.post("/api/documents/preview", response_class=HTMLResponse)
    def preview(doc: Document):
        return jinja.get_template("preview.html").render(doc=doc)

    @app.post("/api/documents/pdf")
    def export_pdf(doc: Document):
        result = validate_document(doc)
        if not result.ok:
            raise HTTPException(status_code=422, detail=result.errores)
        pdf = render_pdf(doc)
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{_slug(doc.title)}.pdf"'},
        )

    static_dir = BASE.parent / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app


app = create_app()
