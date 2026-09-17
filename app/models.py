"""Block + Document schemas. The block list is the single source of truth
for both the visual preview and the generated PDF."""
from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class BlockType(str, Enum):
    heading = "heading"
    paragraph = "paragraph"
    keyvalue = "keyvalue"
    bullets = "bullets"
    sections = "sections"
    signatures = "signatures"


class Align(str, Enum):
    left = "left"
    center = "center"
    right = "right"


class KeyValueRow(BaseModel):
    label: str = ""
    value: str = ""


class SectionEntry(BaseModel):
    title: str = ""
    text: str = ""


class SignatureSide(BaseModel):
    name: str = ""
    role: str = ""


class Block(BaseModel):
    id: str
    type: BlockType
    align: Align = Align.left
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


class Document(BaseModel):
    title: str = "Sin título"
    company_name: str = ""
    show_page_numbers: bool = True
    blocks: list[Block] = Field(default_factory=list)


class ValidationResult(BaseModel):
    ok: bool
    errores: list[str] = Field(default_factory=list)
    avisos: list[str] = Field(default_factory=list)


def validate_document(doc: Document) -> ValidationResult:
    errores: list[str] = []
    avisos: list[str] = []
    if not doc.title.strip():
        errores.append("El documento necesita un título.")
    if not doc.blocks:
        errores.append("El documento no tiene bloques.")
    for i, b in enumerate(doc.blocks, 1):
        empty = (
            (b.type in (BlockType.heading, BlockType.paragraph) and not b.text.strip())
            or (b.type == BlockType.keyvalue and not any(r.label.strip() or r.value.strip() for r in b.rows))
            or (b.type == BlockType.bullets and not any(s.strip() for s in b.items))
            or (b.type == BlockType.sections and not any(e.title.strip() or e.text.strip() for e in b.entries))
        )
        if empty:
            avisos.append(f"Bloque {i} ({b.type.value}) vacío: se omitirá en el PDF.")
    return ValidationResult(ok=not errores, errores=errores, avisos=avisos)
