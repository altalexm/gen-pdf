"""gen-pdf command line: validate and convert documents without the server.

Usage:
    python -m app.cli validate doc.json
    python -m app.cli pdf doc.json -o out.pdf
    python -m app.cli markdown doc.json [-o out.md]
    python -m app.cli docx doc.json -o out.docx
    python -m app.cli layout doc.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .docx_io import document_to_docx
from .markdown import document_to_markdown
from .models import Document, migrate_document
from .models import validate_document as _validate
from .pdf import layout as _layout
from .pdf import render_pdf


def load(path: str) -> Document:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return Document(**migrate_document(raw))


def cmd_validate(args) -> int:
    result = _validate(load(args.doc))
    print(f"ok={result.ok}")
    for e in result.errores:
        print(f"ERROR: {e}")
    for w in result.avisos:
        print(f"warning: {w}")
    return 0 if result.ok else 1


def _write(data: bytes, out: str | None, default: str) -> None:
    target = Path(out or default)
    target.write_bytes(data)
    print(f"wrote {target} ({len(data)} bytes)")


def cmd_pdf(args) -> int:
    doc = load(args.doc)
    result = _validate(doc)
    if not result.ok:
        for e in result.errores:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    _write(render_pdf(doc), args.o, Path(args.doc).with_suffix(".pdf").name)
    return 0


def cmd_markdown(args) -> int:
    text = document_to_markdown(load(args.doc))
    if args.o:
        Path(args.o).write_text(text, encoding="utf-8")
        print(f"wrote {args.o}")
    else:
        print(text, end="")
    return 0


def cmd_docx(args) -> int:
    _write(document_to_docx(load(args.doc)), args.o, Path(args.doc).with_suffix(".docx").name)
    return 0


def cmd_layout(args) -> int:
    info = _layout(load(args.doc))
    print(json.dumps(info, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="gen-pdf", description="Convert gen-pdf documents")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def _add(name, fn, with_output=False):
        parser = sub.add_parser(name)
        parser.add_argument("doc")
        if with_output:
            parser.add_argument("-o")
        parser.set_defaults(fn=fn)
        return parser

    _add("validate", cmd_validate)
    _add("pdf", cmd_pdf, with_output=True)
    _add("markdown", cmd_markdown, with_output=True)
    _add("docx", cmd_docx, with_output=True)
    _add("layout", cmd_layout)
    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except (OSError, ValueError, KeyError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
