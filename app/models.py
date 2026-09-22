"""Block + Document schemas. The block list is the single source of truth
for both the visual preview and the generated PDF.

Text fields support a small inline-markdown subset: **bold**, *italic*, `code`.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

SCHEMA_VERSION = 2


def migrate_document(data: dict) -> dict:
    """Forward-migrate stored documents. Pydantic fills new fields with
    defaults; the version stamp lets future migrations branch explicitly."""
    data = dict(data)
    data.setdefault("schema_version", 1)
    if data["schema_version"] < 2:
        data["schema_version"] = 2
    return data


class BlockType(str, Enum):
    heading = "heading"
    paragraph = "paragraph"
    keyvalue = "keyvalue"
    bullets = "bullets"
    sections = "sections"
    signatures = "signatures"
    table = "table"
    image = "image"
    divider = "divider"
    checklist = "checklist"
    quote = "quote"
    code = "code"
    columns = "columns"
    pagebreak = "pagebreak"
    toc = "toc"
    chart = "chart"


class Align(str, Enum):
    left = "left"
    center = "center"
    right = "right"


class PageSize(str, Enum):
    a4 = "A4"
    letter = "Letter"


class Orientation(str, Enum):
    portrait = "P"
    landscape = "L"


class KeyValueRow(BaseModel):
    label: str = ""
    value: str = ""


class SectionEntry(BaseModel):
    title: str = ""
    text: str = ""


class SignatureSide(BaseModel):
    name: str = ""
    role: str = ""
    drawing: str = ""  # optional data: URL (PNG) of a handwritten signature


class ChecklistItem(BaseModel):
    text: str = ""
    checked: bool = False


class Column(BaseModel):
    title: str = ""
    text: str = ""


class TocEntry(BaseModel):
    title: str = ""
    page: int = 1
    ref: str = ""  # heading block id, for clickable PDF links


class ChartPoint(BaseModel):
    label: str = ""
    value: float = 0.0


class ChartData(BaseModel):
    title: str = ""
    points: list[ChartPoint] = Field(default_factory=list)


class TableData(BaseModel):
    headers: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)


class ImageData(BaseModel):
    src: str = ""  # data: URL or https:// URL
    caption: str = ""
    width_pct: int = Field(default=80, ge=10, le=100)


class PageSettings(BaseModel):
    size: PageSize = PageSize.a4
    orientation: Orientation = Orientation.portrait
    margin_mm: int = Field(default=20, ge=10, le=40)


class Block(BaseModel):
    id: str
    type: BlockType
    align: Align = Align.left
    color: str = ""  # optional #rrggbb, applied to heading/paragraph/bullets text
    # heading
    level: int = Field(default=2, ge=1, le=3)
    text: str = ""
    # keyvalue
    rows: list[KeyValueRow] = Field(default_factory=list)
    # bullets
    items: list[str] = Field(default_factory=list)
    # sections
    entries: list[SectionEntry] = Field(default_factory=list)
    # signatures
    left: SignatureSide = Field(default_factory=SignatureSide)
    right: SignatureSide = Field(default_factory=SignatureSide)
    # table / checklist / image / code
    table: TableData = Field(default_factory=TableData)
    checklist: list[ChecklistItem] = Field(default_factory=list)
    image: ImageData = Field(default_factory=ImageData)
    # columns / toc
    columns: list[Column] = Field(default_factory=list)
    toc_depth: int = Field(default=2, ge=1, le=3)
    toc_entries: list[TocEntry] = Field(default_factory=list)  # filled at render time
    # chart
    chart: ChartData = Field(default_factory=ChartData)


class DocStatus(str, Enum):
    draft = "draft"
    in_review = "in_review"
    approved = "approved"


class Theme(BaseModel):
    """Visual theme applied consistently to preview and PDF."""
    accent: str = "#4f46e5"
    heading_color: str = "#1c1917"


class Document(BaseModel):
    id: str = ""
    schema_version: int = SCHEMA_VERSION
    title: str = "Untitled"
    company_name: str = ""
    show_page_numbers: bool = True
    show_header_title: bool = False
    page: PageSettings = Field(default_factory=PageSettings)
    theme: Theme = Field(default_factory=Theme)
    tags: list[str] = Field(default_factory=list)
    favorite: bool = False
    status: DocStatus = DocStatus.draft
    blocks: list[Block] = Field(default_factory=list)


class ValidationResult(BaseModel):
    ok: bool
    errores: list[str] = Field(default_factory=list)
    avisos: list[str] = Field(default_factory=list)


def _block_empty(b: Block) -> bool:
    if b.type in (BlockType.heading, BlockType.paragraph, BlockType.quote, BlockType.code):
        return not b.text.strip()
    if b.type == BlockType.keyvalue:
        return not any(r.label.strip() or r.value.strip() for r in b.rows)
    if b.type == BlockType.bullets:
        return not any(s.strip() for s in b.items)
    if b.type == BlockType.sections:
        return not any(e.title.strip() or e.text.strip() for e in b.entries)
    if b.type == BlockType.checklist:
        return not any(i.text.strip() for i in b.checklist)
    if b.type == BlockType.table:
        t = b.table
        return not (any(h.strip() for h in t.headers) or any(c.strip() for r in t.rows for c in r))
    if b.type == BlockType.image:
        return not b.image.src.strip()
    if b.type == BlockType.columns:
        return not any(c.title.strip() or c.text.strip() for c in b.columns)
    if b.type == BlockType.chart:
        return not any(p.label.strip() or p.value for p in b.chart.points)
    return False  # divider, pagebreak, toc, signatures always render


def validate_document(doc: Document) -> ValidationResult:
    errores: list[str] = []
    avisos: list[str] = []
    if not doc.title.strip():
        errores.append("The document needs a title.")
    if not doc.blocks:
        errores.append("The document has no blocks.")
    for i, b in enumerate(doc.blocks, 1):
        if _block_empty(b):
            avisos.append(f"Block {i} ({b.type.value}) is empty and will be skipped in the PDF.")
    return ValidationResult(ok=not errores, errores=errores, avisos=avisos)
