"""Best-effort PDF -> blocks import (text layer only, heuristic structure)."""
from __future__ import annotations

import io
import re
import uuid

from pypdf import PdfReader

from .models import Block, BlockType, Document

MAX_PAGES = 200


def _id() -> str:
    return uuid.uuid4().hex[:12]


def _classify(line: str) -> tuple[str, str]:
    """Return (kind, text): headingN, bullet, para."""
    s = line.strip()
    m = re.match(r"^(#{1,3})\s+(.*)$", s)
    if m:
        return f"heading{len(m.group(1))}", m.group(2)
    m = re.match(r"^(\d+)[.)]\s+(.*)$", s)
    if m and len(s) < 120:
        return "heading2", m.group(2)
    if re.match(r"^[-*•]\s+", s):
        return "bullet", re.sub(r"^[-*•]\s+", "", s)
    if s and len(s) < 90 and (s.isupper() or s.istitle()) and not s.endswith((".", ",", ";", ":")):
        return "heading2", s
    return "para", s


def pdf_to_document(data: bytes, title: str = "Imported PDF"):
    """Parse a PDF's text layer into a Document. Raises ValueError on failure."""

    if len(data) > 20 * 1024 * 1024:
        raise ValueError("PDF too large")
    try:
        reader = PdfReader(io.BytesIO(data))
    except Exception as e:
        raise ValueError(f"not a readable PDF: {e}") from e
    if reader.is_encrypted:
        raise ValueError("encrypted PDFs are not supported")
    if len(reader.pages) > MAX_PAGES:
        raise ValueError(f"too many pages (max {MAX_PAGES})")

    doc = Document(title=title or "Imported PDF")
    bullets: list[str] = []

    def flush_bullets():
        if bullets:
            doc.blocks.append(Block(id=_id(), type=BlockType.bullets, items=list(bullets)))
            bullets.clear()

    for i, page in enumerate(reader.pages):
        if i > 0:
            flush_bullets()
            doc.blocks.append(Block(id=_id(), type=BlockType.pagebreak))
        try:
            text = page.extract_text() or ""
        except Exception:
            continue
        para: list[str] = []
        for raw in text.splitlines():
            s = raw.strip()
            if not s:
                if para:
                    doc.blocks.append(Block(id=_id(), type=BlockType.paragraph, text=" ".join(para)))
                    para = []
                continue
            kind, clean = _classify(s)
            if kind == "bullet":
                if para:
                    doc.blocks.append(Block(id=_id(), type=BlockType.paragraph, text=" ".join(para)))
                    para = []
                bullets.append(clean)
            elif kind.startswith("heading"):
                if para:
                    doc.blocks.append(Block(id=_id(), type=BlockType.paragraph, text=" ".join(para)))
                    para = []
                flush_bullets()
                level = 1 if kind == "heading1" else 2
                doc.blocks.append(Block(id=_id(), type=BlockType.heading, level=level, text=clean))
            else:
                para.append(s)
        if para:
            doc.blocks.append(Block(id=_id(), type=BlockType.paragraph, text=" ".join(para)))
        flush_bullets()
    if not doc.blocks:
        raise ValueError("no extractable text found")
    return doc


__all__ = ["pdf_to_document", "MAX_PAGES"]
