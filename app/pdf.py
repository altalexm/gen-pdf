"""Server-side PDF rendering from a block list.

Unicode embedding via bundled DejaVu fonts (OFL licensed), inline **bold** /
*italic* via fpdf2's markdown flag, and a layout() helper that reports the
real page of every block so the preview can show true page breaks.
"""
from __future__ import annotations

import re
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from .models import Align, Block, BlockType, Document, TocEntry

_FONTS = Path(__file__).parent / "fonts"
_NL = {"new_x": XPos.LMARGIN, "new_y": YPos.NEXT}
_HEADING_SIZE = {1: 18, 2: 13, 3: 11}
_ALIGN = {Align.left: "L", Align.center: "C", Align.right: "R"}
_FONT = "dejavu"


def safe_text(text: object) -> str:
    """With an embedded Unicode font there is nothing to strip; just normalize."""
    if text is None:
        return ""
    return str(text).replace("\r\n", "\n").replace("\r", "\n")


def _hex_to_rgb(value: str) -> tuple[int, int, int] | None:
    m = re.fullmatch(r"#?([0-9a-fA-F]{6})", (value or "").strip())
    if not m:
        return None
    h = m.group(1)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


class _PDF(FPDF):
    def __init__(self, doc: Document):
        super().__init__(
            orientation=doc.page.orientation.value,
            format=doc.page.size.value,
        )
        self._doc = doc
        self.set_margins(doc.page.margin_mm, doc.page.margin_mm, doc.page.margin_mm)
        self.add_font(_FONT, "", str(_FONTS / "DejaVuSans.ttf"))
        self.add_font(_FONT, "B", str(_FONTS / "DejaVuSans-Bold.ttf"))
        self.add_font(_FONT, "I", str(_FONTS / "DejaVuSans-Oblique.ttf"))
        self.add_font(_FONT, "BI", str(_FONTS / "DejaVuSans-BoldOblique.ttf"))

    def footer(self):
        self.set_y(-15)
        self.set_font(_FONT, "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, safe_text(self._doc.company_name), border=0, new_x=XPos.RIGHT, new_y=YPos.TOP)
        if self._doc.show_page_numbers:
            self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", border=0, align="R")


def _width(pdf: _PDF) -> float:
    return float(pdf.w) - float(pdf.l_margin) - float(pdf.r_margin)


def _color(pdf: _PDF, b: Block, default: tuple[int, int, int] = (0, 0, 0)) -> None:
    rgb = _hex_to_rgb(b.color) or default
    pdf.set_text_color(*rgb)


def _render_block(pdf: _PDF, b: Block, toc_entries: dict[str, list[TocEntry]] | None = None) -> None:
    align = _ALIGN.get(b.align, "L")
    if b.type == BlockType.heading:
        if not b.text.strip():
            return
        pdf.ln(4)
        pdf.set_font(_FONT, "B", _HEADING_SIZE.get(b.level, 13))
        _color(pdf, b, (40, 40, 40))
        pdf.multi_cell(_width(pdf), 10, safe_text(b.text), border=0, align=align, markdown=True, **_NL)
        pdf.ln(2)
    elif b.type == BlockType.paragraph:
        if not b.text.strip():
            return
        pdf.set_font(_FONT, "", 11)
        _color(pdf, b)
        pdf.multi_cell(_width(pdf), 7, safe_text(b.text), border=0, align=align, markdown=True, **_NL)
        pdf.ln(2)
    elif b.type == BlockType.quote:
        if not b.text.strip():
            return
        x0 = float(pdf.l_margin)
        pdf.set_draw_color(37, 99, 235)
        pdf.set_line_width(1.0)
        y0 = pdf.get_y()
        pdf.set_x(x0 + 4)
        pdf.set_font(_FONT, "I", 11)
        _color(pdf, b, (55, 65, 81))
        pdf.multi_cell(_width(pdf) - 4, 7, safe_text(b.text), border=0, markdown=True, **_NL)
        pdf.line(x0, y0, x0, pdf.get_y())
        pdf.ln(2)
    elif b.type == BlockType.code:
        if not b.text.strip():
            return
        pdf.set_font("Courier", "", 9)
        pdf.set_fill_color(243, 244, 246)
        pdf.set_text_color(17, 24, 39)
        pdf.multi_cell(_width(pdf), 6, safe_text(b.text), border=0, align="L", fill=True, **_NL)
        pdf.ln(2)
    elif b.type == BlockType.divider:
        pdf.ln(3)
        y = pdf.get_y()
        pdf.set_draw_color(180)
        pdf.set_line_width(0.4)
        pdf.line(float(pdf.l_margin), y, float(pdf.w) - float(pdf.r_margin), y)
        pdf.ln(5)
    elif b.type == BlockType.keyvalue:
        rows = [(r.label.strip(), r.value.strip()) for r in b.rows]
        rows = [(lb, v) for lb, v in rows if lb or v]
        if not rows:
            return
        for label, value in rows:
            y = pdf.get_y()
            pdf.set_font(_FONT, "B", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(42, 8, safe_text(f"{label}:" if label else ""), border=0)
            pdf.set_font(_FONT, "", 10)
            w = _width(pdf) - 42
            pdf.set_xy(float(pdf.l_margin) + 42, y)
            pdf.multi_cell(w, 8, safe_text(value), border=0, markdown=True, **_NL)
            pdf.ln(1)
        pdf.ln(2)
    elif b.type == BlockType.bullets:
        items = [s for s in (i.strip() for i in b.items) if s]
        if not items:
            return
        pdf.set_font(_FONT, "", 10)
        _color(pdf, b)
        for item in items:
            pdf.multi_cell(_width(pdf), 6, f"\u2022 {safe_text(item)}", border=0, markdown=True, **_NL)
            pdf.ln(1)
        pdf.ln(2)
    elif b.type == BlockType.checklist:
        items = [(i.text.strip(), i.checked) for i in b.checklist]
        items = [(t, c) for t, c in items if t]
        if not items:
            return
        pdf.set_font(_FONT, "", 10)
        _color(pdf, b)
        for text, checked in items:
            mark = "\u2611" if checked else "\u2610"
            pdf.multi_cell(_width(pdf), 6, f"{mark} {safe_text(text)}", border=0, markdown=True, **_NL)
            pdf.ln(1)
        pdf.ln(2)
    elif b.type == BlockType.sections:
        entries = [(e.title.strip(), e.text.strip()) for e in b.entries]
        entries = [(t, d) for t, d in entries if t or d]
        if not entries:
            return
        for i, (title, text) in enumerate(entries, 1):
            pdf.set_font(_FONT, "B", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 7, safe_text(f"{i}. {title}" if title else f"{i}."), border=0,
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT, markdown=True)
            if text:
                pdf.set_font(_FONT, "", 10)
                pdf.set_x(float(pdf.l_margin) + 5)
                pdf.multi_cell(_width(pdf) - 5, 6, safe_text(text), border=0, markdown=True, **_NL)
            pdf.ln(1)
        pdf.ln(2)
    elif b.type == BlockType.table:
        headers = [h.strip() for h in b.table.headers]
        rows = [[c.strip() for c in r] for r in b.table.rows]
        rows = [r for r in rows if any(r)]
        ncols = max([len(headers)] + [len(r) for r in rows] + [0])
        if ncols == 0:
            return
        headers += [""] * (ncols - len(headers))
        rows = [r + [""] * (ncols - len(r)) for r in rows]
        col_w = _width(pdf) / ncols
        pdf.set_font(_FONT, "B", 9)
        pdf.set_fill_color(31, 41, 55)
        pdf.set_text_color(255, 255, 255)
        for h in headers:
            pdf.cell(col_w, 8, safe_text(h), border=1, align="C", fill=True)
        pdf.ln()
        pdf.set_font(_FONT, "", 9)
        pdf.set_text_color(0, 0, 0)
        fill = False
        for r in rows:
            if fill:
                pdf.set_fill_color(243, 244, 246)
            for j, c in enumerate(r):
                last = j == len(r) - 1
                pdf.cell(col_w, 7, safe_text(c), border=1, fill=fill,
                         new_x=(XPos.LMARGIN if last else XPos.RIGHT),
                         new_y=(YPos.NEXT if last else YPos.TOP))
            fill = not fill
        pdf.ln(4)
    elif b.type == BlockType.image:
        src = (b.image.src or "").strip()
        if not src:
            return
        data = _load_image(src)
        if data is None:
            pdf.set_font(_FONT, "I", 9)
            pdf.set_text_color(150)
            pdf.multi_cell(_width(pdf), 6, "[Image could not be loaded]", border=0, align="C", **_NL)
            return
        import io
        w = _width(pdf) * max(10, min(100, b.image.width_pct)) / 100
        x = float(pdf.l_margin) + (_width(pdf) - w) / 2 if b.align == Align.center else (
            float(pdf.w) - float(pdf.r_margin) - w if b.align == Align.right else float(pdf.l_margin))
        pdf.image(io.BytesIO(data), x=x, w=w)
        pdf.ln(2)
        if b.image.caption.strip():
            pdf.set_font(_FONT, "I", 9)
            pdf.set_text_color(100)
            pdf.multi_cell(_width(pdf), 6, safe_text(b.image.caption), border=0, align="C", **_NL)
            pdf.ln(2)
    elif b.type == BlockType.signatures:
        if float(pdf.h) - float(pdf.get_y()) < 60:
            pdf.add_page()
        w, gap = _width(pdf), 10.0
        col = (w - gap) / 2.0
        y0 = pdf.get_y()
        import io as _io
        for j, side in enumerate((b.left, b.right)):
            x = float(pdf.l_margin) + j * (col + gap)
            drawing = _load_image(side.drawing) if (side.drawing or "").strip() else None
            if drawing:
                try:
                    img_w = col * 0.55
                    pdf.image(_io.BytesIO(drawing), x=x + (col - img_w) / 2, y=y0, w=img_w)
                except Exception:
                    drawing = None
            pdf.set_xy(x, y0 + (24 if drawing else 0))
            pdf.set_font(_FONT, "", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(col, 7, safe_text(f"{'' if drawing else chr(10) * 3}{side.name}\n{side.role}"), border=0, align="C", **_NL)
        y_line = y0 + 22
        for j in range(2):
            x = float(pdf.l_margin) + j * (col + gap)
            pdf.line(x, y_line, x + col, y_line)
        pdf.set_y(max(y_line + 6, pdf.get_y() + 2))
    elif b.type == BlockType.columns:
        cols = [(c.title.strip(), c.text.strip()) for c in b.columns]
        cols = [(t, d) for t, d in cols if t or d][:3]
        if not cols:
            return
        n = len(cols)
        gap = 8.0
        col_w = (_width(pdf) - gap * (n - 1)) / n
        y0 = pdf.get_y()
        y_max = y0
        for j, (title, text) in enumerate(cols):
            x = float(pdf.l_margin) + j * (col_w + gap)
            pdf.set_xy(x, y0)
            if title:
                pdf.set_font(_FONT, "B", 10)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(col_w, 7, safe_text(title), border=0, markdown=True, **_NL)
            if text:
                pdf.set_font(_FONT, "", 10)
                pdf.set_x(x)
                pdf.multi_cell(col_w, 6, safe_text(text), border=0, markdown=True, **_NL)
            y_max = max(y_max, pdf.get_y())
        pdf.set_y(y_max + 2)
        pdf.ln(2)
    elif b.type == BlockType.pagebreak:
        if float(pdf.get_y()) > float(pdf.t_margin) + 2:
            pdf.add_page()
    elif b.type == BlockType.toc:
        entries = list((toc_entries or {}).get(b.id, b.toc_entries))
        if not entries:
            return
        pdf.set_font(_FONT, "B", 11)
        pdf.set_text_color(0, 0, 0)
        for e in entries:
            y = pdf.get_y()
            pdf.set_font(_FONT, "", 10)
            pdf.cell(_width(pdf) - 14, 7, safe_text(e.title), border=0)
            pdf.cell(14, 7, str(e.page), border=0, align="R",
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_y(y + 7)
        pdf.ln(3)


def _load_image(src: str) -> bytes | None:
    try:
        if src.startswith("data:"):
            import base64
            return base64.b64decode(src.split(",", 1)[1])
        if src.startswith(("http://", "https://")):
            import urllib.request
            with urllib.request.urlopen(src, timeout=15) as r:
                return r.read()
        p = Path(src)
        return p.read_bytes() if p.is_file() else None
    except Exception:
        return None


def _new_pdf(doc: Document) -> _PDF:
    pdf = _PDF(doc)
    pdf.alias_nb_pages("{nb}")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    return pdf


def _render_all(doc: Document, toc_entries: dict[str, list[TocEntry]] | None = None,
                record: dict[str, int] | None = None) -> _PDF:
    pdf = _new_pdf(doc)
    for b in doc.blocks:
        if record is not None:
            record[b.id] = pdf.pages_count or 1
        _render_block(pdf, b, toc_entries or {})
    return pdf


def _collect_toc(doc: Document, pages: dict[str, int]) -> dict[str, list[TocEntry]]:
    out: dict[str, list[TocEntry]] = {}
    for b in doc.blocks:
        if b.type == BlockType.toc:
            out[b.id] = [
                TocEntry(title=h.text.strip(), page=pages.get(h.id, 1))
                for h in doc.blocks
                if h.type == BlockType.heading and h.level <= b.toc_depth and h.text.strip()
            ]
    return out


def render_pdf(doc: Document) -> bytes:
    toc_entries: dict[str, list[TocEntry]] = {}
    if any(b.type == BlockType.toc for b in doc.blocks):
        # Pass 1 discovers real heading pages; pass 2 prints the TOC with them.
        probe: dict[str, int] = {}
        _render_all(doc, {}, probe)
        toc_entries = _collect_toc(doc, probe)
    pdf = _render_all(doc, toc_entries)
    out = pdf.output()
    return bytes(out) if isinstance(out, (bytes, bytearray)) else out.encode("latin-1")


def layout(doc: Document) -> dict:
    """Render once, recording the real page of every block (true page breaks)."""
    record: dict[str, int] = {}
    pdf = _render_all(doc, {}, record)
    return {"pages": pdf.pages_count or 1, "blocks": record}


# Re-exported for convenience
__all__ = ["render_pdf", "layout", "safe_text", "prepare_preview"]


def prepare_preview(doc: Document) -> tuple[Document, dict[str, int]]:
    """Pass-1 pages + TOC injection, mirroring render_pdf (used by HTML preview)."""
    record: dict[str, int] = {}
    _render_all(doc, {}, record)
    toc = _collect_toc(doc, record)
    if toc:
        doc = doc.model_copy(update={
            "blocks": [b.model_copy(update={"toc_entries": toc[b.id]}) if b.id in toc else b
                       for b in doc.blocks]})
    return doc, record
