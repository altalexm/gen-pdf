"""Server-side PDF rendering from a block list (fpdf2, no system deps)."""
from __future__ import annotations

import unicodedata

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from .models import Align, Block, BlockType, Document

_NL = {"new_x": XPos.LMARGIN, "new_y": YPos.NEXT}
_HEADING_SIZE = {1: 18, 2: 13, 3: 11}
_ALIGN = {Align.left: "L", Align.center: "C", Align.right: "R"}


def safe_text(text: object) -> str:
    """Normalize to latin-1 (fpdf2 core fonts) without crashing on accents/emoji."""
    if text is None:
        return ""
    s = str(text)
    for k, v in {
        "\u2013": "-", "\u2014": "-", "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"', "\u2022": "-", "\u2023": "-",
        "\u25aa": "-", "\u25cf": "-", "\u00a0": " ",
    }.items():
        s = s.replace(k, v)
    s = unicodedata.normalize("NFKD", s)
    return s.encode("latin-1", errors="replace").decode("latin-1")


class _PDF(FPDF):
    def __init__(self, company_name: str, show_page_numbers: bool):
        super().__init__()
        self._company = safe_text(company_name)
        self._numbers = show_page_numbers
        self.set_margins(20, 20, 20)

    def footer(self):
        self.set_y(-20)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, self._company, border=0, new_x=XPos.RIGHT, new_y=YPos.TOP)
        if self._numbers:
            self.cell(0, 10, f"Page {self.page_no()}", border=0, align="R")


def _width(pdf: _PDF) -> float:
    return float(pdf.w) - float(pdf.l_margin) - float(pdf.r_margin)


def _render_block(pdf: _PDF, b: Block) -> None:
    align = _ALIGN.get(b.align, "L")
    if b.type == BlockType.heading:
        pdf.ln(4)
        pdf.set_font("Arial", "B", _HEADING_SIZE.get(b.level, 13))
        pdf.set_text_color(40, 40, 40)
        if b.text.strip():
            pdf.multi_cell(_width(pdf), 10, safe_text(b.text), border=0, align=align, **_NL)
        pdf.ln(2)
    elif b.type == BlockType.paragraph:
        if not b.text.strip():
            return
        pdf.set_font("Arial", "", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(_width(pdf), 7, safe_text(b.text), border=0, align=align, **_NL)
        pdf.ln(2)
    elif b.type == BlockType.keyvalue:
        rows = [(r.label.strip(), r.value.strip()) for r in b.rows]
        rows = [(lb, v) for lb, v in rows if lb or v]
        if not rows:
            return
        for label, value in rows:
            y = pdf.get_y()
            pdf.set_font("Arial", "B", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(42, 8, safe_text(f"{label}:" if label else ""), border=0)
            pdf.set_font("Arial", "", 10)
            w = _width(pdf) - 42
            pdf.set_xy(float(pdf.l_margin) + 42, y)
            pdf.multi_cell(w, 8, safe_text(value), border=0, **_NL)
            pdf.ln(1)
        pdf.ln(2)
    elif b.type == BlockType.bullets:
        items = [s for s in (i.strip() for i in b.items) if s]
        if not items:
            return
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(0, 0, 0)
        for item in items:
            pdf.multi_cell(_width(pdf), 6, f"- {safe_text(item)}", border=0, **_NL)
            pdf.ln(1)
        pdf.ln(2)
    elif b.type == BlockType.sections:
        entries = [(e.title.strip(), e.text.strip()) for e in b.entries]
        entries = [(t, d) for t, d in entries if t or d]
        if not entries:
            return
        for i, (title, text) in enumerate(entries, 1):
            pdf.set_font("Arial", "B", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 7, safe_text(f"{i}. {title}" if title else f"{i}."), border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if text:
                pdf.set_font("Arial", "", 10)
                pdf.set_x(float(pdf.l_margin) + 5)
                pdf.multi_cell(_width(pdf) - 5, 6, safe_text(text), border=0, **_NL)
            pdf.ln(1)
        pdf.ln(2)
    elif b.type == BlockType.signatures:
        if float(pdf.h) - float(pdf.get_y()) < 60:
            pdf.add_page()
        w, gap = _width(pdf), 10.0
        col = (w - gap) / 2.0
        y0 = pdf.get_y()
        for j, side in enumerate((b.left, b.right)):
            x = float(pdf.l_margin) + j * (col + gap)
            pdf.set_xy(x, y0)
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(col, 7, safe_text(f"\n\n\n{side.name}\n{side.role}"), border=0, align="C")
            y_line = y0 + 22
            pdf.line(x, y_line, x + col, y_line)
        pdf.set_y(y_line + 6)


def render_pdf(doc: Document) -> bytes:
    pdf = _PDF(doc.company_name, doc.show_page_numbers)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)
    for b in doc.blocks:
        _render_block(pdf, b)
    out = pdf.output()
    return bytes(out) if isinstance(out, (bytes, bytearray)) else out.encode("latin-1")
