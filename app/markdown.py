"""Markdown <-> blocks conversion (interoperability without lock-in)."""
from __future__ import annotations

import re
import uuid

from .models import (
    Block,
    BlockType,
    ChecklistItem,
    Document,
    ImageData,
    KeyValueRow,
    SectionEntry,
    SignatureSide,
    TableData,
)


def _id() -> str:
    return uuid.uuid4().hex[:12]


def document_to_markdown(doc: Document) -> str:
    out: list[str] = ["---", f"title: {doc.title.strip()}", f"status: {doc.status.value}"]
    if doc.tags:
        out.append(f"tags: [{', '.join(doc.tags)}]")
    out += ["---", "", f"# {doc.title}", ""]
    if doc.company_name.strip():
        out += [f"*{doc.company_name.strip()}*", ""]
    for b in doc.blocks:
        if b.type == BlockType.heading:
            out += [f"{'#' * max(1, min(3, b.level))} {b.text.strip()}", ""]
        elif b.type == BlockType.paragraph:
            if b.text.strip():
                out += [b.text.strip(), ""]
        elif b.type == BlockType.quote:
            if b.text.strip():
                out += [f"> {b.text.strip()}", ""]
        elif b.type == BlockType.code:
            if b.text.strip():
                out += ["```", b.text.rstrip(), "```", ""]
        elif b.type == BlockType.divider:
            out += ["---", ""]
        elif b.type == BlockType.keyvalue:
            for r in b.rows:
                if r.label.strip() or r.value.strip():
                    out += [f"**{r.label.strip()}:** {r.value.strip()}"]
            out += [""]
        elif b.type == BlockType.bullets:
            for i in b.items:
                if i.strip():
                    out += [f"- {i.strip()}"]
            out += [""]
        elif b.type == BlockType.checklist:
            for i in b.checklist:
                if i.text.strip():
                    out += [f"- [{'x' if i.checked else ' '}] {i.text.strip()}"]
            out += [""]
        elif b.type == BlockType.sections:
            for n, e in enumerate(b.entries, 1):
                if e.title.strip() or e.text.strip():
                    out += [f"{n}. **{e.title.strip()}**"]
                    if e.text.strip():
                        out += [e.text.strip()]
            out += [""]
        elif b.type == BlockType.table:
            t = b.table
            headers = [h.strip() for h in t.headers]
            rows = [[c.strip() for c in r] for r in t.rows if any(c.strip() for c in r)]
            if headers or rows:
                ncols = max([len(headers)] + [len(r) for r in rows])
                headers += [""] * (ncols - len(headers))
                out += ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * ncols) + " |"]
                for r in rows:
                    out += ["| " + " | ".join(r + [""] * (ncols - len(r))) + " |"]
                out += [""]
        elif b.type == BlockType.image:
            if b.image.src.strip() or b.image.caption.strip():
                out += [f"![{b.image.caption.strip()}]({b.image.src.strip()})", ""]
        elif b.type == BlockType.pagebreak:
            out += ["<!-- pagebreak -->", ""]
        elif b.type == BlockType.toc:
            out += ["[[_TOC_]]", ""]
        elif b.type == BlockType.columns:
            cols = [(c.title.strip(), c.text.strip()) for c in b.columns if c.title.strip() or c.text.strip()]
            if cols:
                out += ["| " + " | ".join(t for t, _ in cols) + " |",
                        "| " + " | ".join(["---"] * len(cols)) + " |",
                        "| " + " | ".join(d.replace("\n", "<br>") for _, d in cols) + " |", ""]
        elif b.type == BlockType.chart:
            pts = [(p.label.strip(), p.value) for p in b.chart.points if p.label.strip() or p.value]
            if pts:
                if b.chart.title.strip():
                    out += [f"**{b.chart.title.strip()}**"]
                out += ["| label | value |", "| --- | --- |"]
                out += [f"| {lb} | {v:g} |" for lb, v in pts] + [""]
        elif b.type == BlockType.signatures:
            out += ["::: signatures",
                    f"{b.left.name.strip()} | {b.left.role.strip()}",
                    f"{b.right.name.strip()} | {b.right.role.strip()}",
                    ":::", ""]
    return "\n".join(out).rstrip() + "\n"


def _new_block(btype: BlockType, **kw) -> Block:
    return Block(id=_id(), type=btype, **kw)


def markdown_to_document(text: str, title: str = "Imported document") -> Document:
    blocks: list[Block] = []
    lines = (text or "").replace("\r\n", "\n").split("\n")
    meta_tags: list[str] = []
    meta_status = "draft"
    if len(lines) >= 2 and lines[0].strip() == "---":
        try:
            end = lines.index("---", 1)
            for ln in lines[1:end]:
                if ":" in ln:
                    k, v = ln.split(":", 1)
                    k, v = k.strip().lower(), v.strip()
                    if k == "title" and v:
                        title = v
                    elif k == "tags":
                        meta_tags = [x.strip().lower().strip("[]") for x in v.split(",") if x.strip()]
                    elif k == "status" and v in ("draft", "in_review", "approved"):
                        meta_status = v
            lines = lines[end + 1:]
        except ValueError:
            pass
    i, n = 0, len(lines)
    para: list[str] = []
    kv_rows: list[KeyValueRow] = []
    doc_title = title

    def flush_para():
        if para:
            blocks.append(_new_block(BlockType.paragraph, text="\n".join(para).strip()))
            para.clear()

    def flush_kv():
        if kv_rows:
            blocks.append(_new_block(BlockType.keyvalue, rows=list(kv_rows)))
            kv_rows.clear()

    in_code, code_buf = False, []
    while i < n:
        line = lines[i]
        s = line.strip()
        if s.startswith("```"):
            if in_code:
                blocks.append(_new_block(BlockType.code, text="\n".join(code_buf)))
                code_buf = []
                in_code = False
            else:
                flush_para()
                flush_kv()
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(line.rstrip("\n"))
            i += 1
            continue
        if not s:
            flush_para()
            flush_kv()
            i += 1
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", s)
        if m:
            flush_para()
            flush_kv()
            level = len(m.group(1))
            if i == 0 or (not blocks and level == 1):
                doc_title = m.group(2).strip() or title
            else:
                blocks.append(_new_block(BlockType.heading, level=level, text=m.group(2).strip()))
            i += 1
            continue
        if s in ("---", "***", "___"):
            flush_para()
            flush_kv()
            blocks.append(_new_block(BlockType.divider))
            i += 1
            continue
        if s == "::: signatures":
            flush_para()
            flush_kv()
            sides: list[tuple[str, str]] = []
            i += 1
            while i < n and lines[i].strip() not in (":::", ""):
                parts = [p.strip() for p in lines[i].split("|")]
                sides.append((parts[0] if parts else "", parts[1] if len(parts) > 1 else ""))
                i += 1
            if i < n and lines[i].strip() == ":::":
                i += 1
            left = SignatureSide(name=sides[0][0] if len(sides) > 0 else "", role=sides[0][1] if len(sides) > 0 else "")
            right = SignatureSide(name=sides[1][0] if len(sides) > 1 else "", role=sides[1][1] if len(sides) > 1 else "")
            blocks.append(_new_block(BlockType.signatures, left=left, right=right))
            continue
        if s.startswith("> "):
            flush_para()
            flush_kv()
            quote = [s[2:]]
            while i + 1 < n and lines[i + 1].strip().startswith("> "):
                i += 1
                quote.append(lines[i].strip()[2:])
            blocks.append(_new_block(BlockType.quote, text="\n".join(quote)))
            i += 1
            continue
        if s.startswith("|") and s.endswith("|") and i + 1 < n and re.match(r"^\|?[\s:\-|]+\|?$", lines[i + 1].strip()):
            flush_para()
            flush_kv()
            headers = [c.strip() for c in s.strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            blocks.append(_new_block(BlockType.table, table=TableData(headers=headers, rows=rows)))
            continue
        m = re.match(r"^[-*]\s+\[([ xX])\]\s+(.*)$", s)
        if m:
            flush_para()
            flush_kv()
            items = [ChecklistItem(text=m.group(2).strip(), checked=m.group(1).lower() == "x")]
            while i + 1 < n:
                m2 = re.match(r"^[-*]\s+\[([ xX])\]\s+(.*)$", lines[i + 1].strip())
                if not m2:
                    break
                items.append(ChecklistItem(text=m2.group(2).strip(), checked=m2.group(1).lower() == "x"))
                i += 1
            blocks.append(_new_block(BlockType.checklist, checklist=items))
            i += 1
            continue
        m = re.match(r"^[-*]\s+(.*)$", s)
        if m:
            flush_para()
            flush_kv()
            items = [m.group(1).strip()]
            while i + 1 < n:
                m2 = re.match(r"^[-*]\s+(.*)$", lines[i + 1].strip())
                if not m2:
                    break
                items.append(m2.group(1).strip())
                i += 1
            blocks.append(_new_block(BlockType.bullets, items=items))
            i += 1
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", s)
        if m:
            flush_para()
            flush_kv()
            entries = []
            while i < n:
                m2 = re.match(r"^(\d+)\.\s+(.*)$", lines[i].strip())
                if not m2:
                    break
                title_text = re.sub(r"^\*\*(.*?)\*\*$", r"\1", m2.group(2).strip())
                i += 1
                desc = []
                while i < n and lines[i].strip() and not re.match(r"^(\d+)\.\s+", lines[i].strip()):
                    desc.append(lines[i].strip())
                    i += 1
                entries.append(SectionEntry(title=title_text, text="\n".join(desc)))
            blocks.append(_new_block(BlockType.sections, entries=entries))
            continue
        m = re.match(r"^\*\*(.+?):\*\*\s*(.*)$", s)
        if m:
            flush_para()
            kv_rows.append(KeyValueRow(label=m.group(1).strip(), value=m.group(2).strip()))
            i += 1
            continue
        if s == "<!-- pagebreak -->":
            flush_para()
            flush_kv()
            blocks.append(_new_block(BlockType.pagebreak))
            i += 1
            continue
        if s == "[[_TOC_]]":
            flush_para()
            flush_kv()
            blocks.append(_new_block(BlockType.toc))
            i += 1
            continue
        m = re.match(r"^!\[(.*?)\]\((.*?)\)$", s)
        if m:
            flush_para()
            flush_kv()
            blocks.append(_new_block(BlockType.image,
                                     image=ImageData(src=m.group(2).strip(), caption=m.group(1).strip())))
            i += 1
            continue
        para.append(s)
        i += 1
    flush_para()
    flush_kv()
    return Document(title=doc_title, tags=meta_tags, status=meta_status, blocks=blocks)


__all__ = ["document_to_markdown", "markdown_to_document"]
