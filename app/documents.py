"""Built-in templates. A new document type is just a builder + registry entry."""
from __future__ import annotations

import uuid

from .models import Align, Block, BlockType, Document, KeyValueRow, SectionEntry, SignatureSide


def _id() -> str:
    return uuid.uuid4().hex[:12]


def _heading(text: str, level: int = 2, align: Align = Align.left) -> Block:
    return Block(id=_id(), type=BlockType.heading, level=level, align=align, text=text)


def acta_template() -> Document:
    return Document(
        title="Acta de Reunión",
        company_name="Tu Organización",
        blocks=[
            _heading("Acta de Reunión", level=1, align=Align.center),
            Block(id=_id(), type=BlockType.keyvalue, rows=[
                KeyValueRow(label="Proyecto", value=""),
                KeyValueRow(label="Fecha", value=""),
                KeyValueRow(label="Hora", value=""),
                KeyValueRow(label="Lugar", value=""),
                KeyValueRow(label="Moderador", value=""),
                KeyValueRow(label="Responsable", value=""),
            ]),
            _heading("1. Normas de la reunión"),
            Block(id=_id(), type=BlockType.bullets, items=["Puntualidad y asistencia.", "Respetar el turno de palabra."]),
            _heading("2. Orden del día"),
            Block(id=_id(), type=BlockType.sections, entries=[
                SectionEntry(title="Revisión de avances", text=""),
            ]),
            _heading("3. Acuerdos"),
            Block(id=_id(), type=BlockType.sections, entries=[]),
            _heading("4. Próxima reunión"),
            Block(id=_id(), type=BlockType.paragraph, text="Fecha:  | Hora:  | Lugar: "),
            _heading("5. Firmas"),
            Block(id=_id(), type=BlockType.signatures,
                  left=SignatureSide(name="", role="Moderador"),
                  right=SignatureSide(name="", role="Responsable")),
        ],
    )


def nda_template() -> Document:
    return Document(
        title="Acuerdo de Confidencialidad",
        company_name="Tu Organización",
        blocks=[
            _heading("Acuerdo de Confidencialidad", level=1, align=Align.center),
            Block(id=_id(), type=BlockType.keyvalue, rows=[
                KeyValueRow(label="Parte A", value=""),
                KeyValueRow(label="Parte B", value=""),
                KeyValueRow(label="Fecha", value=""),
            ]),
            Block(id=_id(), type=BlockType.paragraph, text=(
                "Las partes acuerdan proteger toda la información confidencial "
                "compartida en el marco de su relación profesional."
            )),
            _heading("Cláusulas"),
            Block(id=_id(), type=BlockType.sections, entries=[
                SectionEntry(title="1. Objeto", text="Definición de la información confidencial."),
                SectionEntry(title="2. Obligaciones", text="No divulgar ni usar la información para otros fines."),
                SectionEntry(title="3. Vigencia", text="Duración del acuerdo y supervivencia de las obligaciones."),
            ]),
            _heading("Firmas"),
            Block(id=_id(), type=BlockType.signatures,
                  left=SignatureSide(name="", role="Parte A"),
                  right=SignatureSide(name="", role="Parte B")),
        ],
    )


def blank_template() -> Document:
    return Document(
        title="Documento sin título",
        company_name="",
        blocks=[
            _heading("Título del documento", level=1, align=Align.center),
            Block(id=_id(), type=BlockType.paragraph, text="Escribe aquí…"),
        ],
    )


TEMPLATES: dict[str, dict] = {
    "acta": {"id": "acta", "name": "Acta de reunión", "description": "Meeting minutes with agenda, agreements and signatures.", "build": acta_template},
    "nda": {"id": "nda", "name": "Acuerdo de confidencialidad", "description": "Two-party NDA with clauses and signatures.", "build": nda_template},
    "blank": {"id": "blank", "name": "Documento en blanco", "description": "Start from scratch with freely arranged blocks.", "build": blank_template},
}
