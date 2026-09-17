"""Document library backed by SQLite (stdlib only).

Features: soft-delete trash, version snapshots with diff support, FTS5
full-text search, per-block comments, user templates, tags/favorites/status.
"""
from __future__ import annotations

import difflib
import json
import os
import sqlite3
import time
import uuid
from pathlib import Path

MAX_VERSIONS = 30


def db_path() -> Path:
    p = Path(os.getenv("GENPDF_DB", "data/library.db"))
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _connect() -> sqlite3.Connection:
    con = sqlite3.connect(db_path())
    con.row_factory = sqlite3.Row
    con.execute(
        "CREATE TABLE IF NOT EXISTS documents ("
        "id TEXT PRIMARY KEY, title TEXT NOT NULL, updated_at REAL NOT NULL, "
        "deleted_at REAL, tags TEXT NOT NULL DEFAULT '', favorite INTEGER NOT NULL DEFAULT 0, "
        "status TEXT NOT NULL DEFAULT 'draft', data TEXT NOT NULL)"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS versions ("
        "id TEXT PRIMARY KEY, doc_id TEXT NOT NULL, created_at REAL NOT NULL, "
        "label TEXT NOT NULL DEFAULT '', data TEXT NOT NULL)"
    )
    con.execute("CREATE INDEX IF NOT EXISTS idx_versions_doc ON versions (doc_id, created_at)")
    con.execute(
        "CREATE TABLE IF NOT EXISTS comments ("
        "id TEXT PRIMARY KEY, doc_id TEXT NOT NULL, block_id TEXT NOT NULL DEFAULT '', "
        "author TEXT NOT NULL DEFAULT '', text TEXT NOT NULL DEFAULT '', "
        "resolved INTEGER NOT NULL DEFAULT 0, created_at REAL NOT NULL)"
    )
    con.execute("CREATE INDEX IF NOT EXISTS idx_comments_doc ON comments (doc_id)")
    con.execute(
        "CREATE TABLE IF NOT EXISTS user_templates ("
        "id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', "
        "created_at REAL NOT NULL, data TEXT NOT NULL)"
    )
    try:
        con.execute("CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(doc_id UNINDEXED, title, content)")
    except sqlite3.OperationalError:
        pass  # SQLite without FTS5: search falls back to LIKE
    # Light migrations for DBs created by older versions
    cols = {r[1] for r in con.execute("PRAGMA table_info(documents)").fetchall()}
    for name, ddl in [
        ("deleted_at", "ALTER TABLE documents ADD COLUMN deleted_at REAL"),
        ("tags", "ALTER TABLE documents ADD COLUMN tags TEXT NOT NULL DEFAULT ''"),
        ("favorite", "ALTER TABLE documents ADD COLUMN favorite INTEGER NOT NULL DEFAULT 0"),
        ("status", "ALTER TABLE documents ADD COLUMN status TEXT NOT NULL DEFAULT 'draft'"),
    ]:
        if name not in cols:
            con.execute(ddl)
    return con


def _tags_str(tags: object) -> str:
    if isinstance(tags, list):
        tags = [str(x).strip().lower() for x in tags if str(x).strip()]
        return ",".join(sorted(set(tags)))
    return ""


def flatten_content(data: dict) -> str:
    """All searchable text of a document, for the FTS index."""
    parts = [str(data.get("title", "")), str(data.get("company_name", ""))]
    for b in data.get("blocks", []) or []:
        parts.append(str(b.get("text", "")))
        for r in b.get("rows", []) or []:
            parts += [str(r.get("label", "")), str(r.get("value", ""))]
        parts += [str(x) for x in b.get("items", []) or []]
        for e in b.get("entries", []) or []:
            parts += [str(e.get("title", "")), str(e.get("text", ""))]
        for i in b.get("checklist", []) or []:
            parts.append(str(i.get("text", "")))
        t = b.get("table", {}) or {}
        parts += [str(h) for h in t.get("headers", []) or []]
        for r in t.get("rows", []) or []:
            parts += [str(c) for c in r]
        for c in b.get("columns", []) or []:
            parts += [str(c.get("title", "")), str(c.get("text", ""))]
        parts.append(str((b.get("image", {}) or {}).get("caption", "")))
    return "\n".join(p for p in parts if p)


def _reindex(con: sqlite3.Connection, doc_id: str, title: str, data: dict) -> None:
    try:
        con.execute("DELETE FROM docs_fts WHERE doc_id = ?", (doc_id,))
        con.execute("INSERT INTO docs_fts (doc_id, title, content) VALUES (?, ?, ?)",
                    (doc_id, title, flatten_content(data)))
    except sqlite3.OperationalError:
        pass


def _row_to_dict(row: sqlite3.Row) -> dict:
    data = json.loads(row["data"])
    data.setdefault("id", row["id"])
    return {"id": row["id"], "title": row["title"], "updated_at": row["updated_at"],
            "deleted_at": row["deleted_at"], "tags": (row["tags"] or "").split(",") if row["tags"] else [],
            "favorite": bool(row["favorite"]), "status": row["status"], "document": data}


# ---------------- documents ----------------

def list_documents(query: str = "", tag: str = "", favorites_only: bool = False,
                   status: str = "", include_deleted: bool = False) -> list[dict]:
    with _connect() as con:
        if not include_deleted:
            base = "deleted_at IS NULL"
        else:
            base = "1=1"
        params: list[object] = []
        where = [base]
        ids: set[str] | None = None
        if query.strip():
            q = query.strip()
            try:
                quoted = '"' + q.replace('"', '""') + '"'
                rows = con.execute("SELECT doc_id FROM docs_fts WHERE docs_fts MATCH ?", (quoted,)).fetchall()
                ids = {r[0] for r in rows}
            except sqlite3.OperationalError:
                ids = None
            if ids is None:  # no FTS support: title fallback
                where.append("title LIKE ?")
                params.append(f"%{q}%")
            elif ids:
                where.append(f"id IN ({','.join('?' * len(ids))})")
                params.extend(sorted(ids))
            else:
                return []
        if tag.strip():
            where.append("((',' || tags || ',') LIKE ?)")
            params.append(f"%,{tag.strip().lower()},%")
        if favorites_only:
            where.append("favorite = 1")
        if status.strip():
            where.append("status = ?")
            params.append(status.strip())
        cur = con.execute(
            f"SELECT id, title, updated_at, deleted_at, tags, favorite, status, data FROM documents "
            f"WHERE {' AND '.join(where)} ORDER BY updated_at DESC", params)
        return [_row_to_dict(r) for r in cur.fetchall()]


def get_document(doc_id: str) -> dict | None:
    with _connect() as con:
        row = con.execute(
            "SELECT id, title, updated_at, deleted_at, tags, favorite, status, data FROM documents WHERE id = ?",
            (doc_id,)).fetchone()
        return _row_to_dict(row) if row else None


def save_document(data: dict) -> dict:
    # Normalize through the model in JSON mode so enums become plain
    # values (str(DocStatus.draft) would otherwise leak 'DocStatus.draft').
    from .models import Document as _Document

    data = _Document(**data).model_dump(mode="json")
    doc_id = (data.get("id") or "").strip() or uuid.uuid4().hex[:12]
    data["id"] = doc_id
    data["tags"] = sorted({str(x).strip().lower() for x in (data.get("tags") or []) if str(x).strip()})
    data["favorite"] = bool(data.get("favorite", False))
    data["status"] = str(data.get("status") or "draft")
    title = (data.get("title") or "Untitled").strip() or "Untitled"
    now = time.time()
    with _connect() as con:
        prev = con.execute("SELECT data FROM documents WHERE id = ?", (doc_id,)).fetchone()
        con.execute(
            "INSERT INTO documents (id, title, updated_at, deleted_at, tags, favorite, status, data) "
            "VALUES (?, ?, ?, NULL, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET title=excluded.title, updated_at=excluded.updated_at, "
            "deleted_at=NULL, tags=excluded.tags, favorite=excluded.favorite, status=excluded.status, data=excluded.data",
            (doc_id, title, now, _tags_str(data["tags"]), int(data["favorite"]), data["status"],
             json.dumps(data, ensure_ascii=False)))
        _reindex(con, doc_id, title, data)
        if not prev or prev[0] != json.dumps(data, ensure_ascii=False):
            _snapshot(con, doc_id, data, label="autosave")
    return {"id": doc_id, "title": title, "updated_at": now, "document": data}


def soft_delete(doc_id: str) -> bool:
    with _connect() as con:
        cur = con.execute("UPDATE documents SET deleted_at = ? WHERE id = ? AND deleted_at IS NULL",
                          (time.time(), doc_id))
        return cur.rowcount > 0


def restore_document(doc_id: str) -> bool:
    with _connect() as con:
        cur = con.execute("UPDATE documents SET deleted_at = NULL WHERE id = ?", (doc_id,))
        return cur.rowcount > 0


def purge_document(doc_id: str) -> bool:
    with _connect() as con:
        con.execute("DELETE FROM versions WHERE doc_id = ?", (doc_id,))
        con.execute("DELETE FROM comments WHERE doc_id = ?", (doc_id,))
        try:
            con.execute("DELETE FROM docs_fts WHERE doc_id = ?", (doc_id,))
        except sqlite3.OperationalError:
            pass
        cur = con.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        return cur.rowcount > 0


def duplicate_document(doc_id: str) -> dict | None:
    existing = get_document(doc_id)
    if not existing or existing["deleted_at"]:
        return None
    data = existing["document"]
    data["id"] = uuid.uuid4().hex[:12]
    data["title"] = f"{data.get('title', 'Untitled')} (copy)"
    return save_document(data)


def all_tags() -> list[dict]:
    with _connect() as con:
        cur = con.execute("SELECT tags FROM documents WHERE deleted_at IS NULL AND tags <> ''")
        counts: dict[str, int] = {}
        for (tags,) in cur.fetchall():
            for tag in tags.split(","):
                if tag:
                    counts[tag] = counts.get(tag, 0) + 1
        return [{"tag": k, "count": v} for k, v in sorted(counts.items())]


# ---------------- versions ----------------

def _snapshot(con: sqlite3.Connection, doc_id: str, data: dict, label: str = "") -> str:
    vid = uuid.uuid4().hex[:12]
    con.execute("INSERT INTO versions (id, doc_id, created_at, label, data) VALUES (?, ?, ?, ?, ?)",
                (vid, doc_id, time.time(), label, json.dumps(data, ensure_ascii=False)))
    con.execute(
        "DELETE FROM versions WHERE doc_id = ? AND id NOT IN "
        "(SELECT id FROM versions WHERE doc_id = ? ORDER BY created_at DESC LIMIT ?)",
        (doc_id, doc_id, MAX_VERSIONS))
    return vid


def list_versions(doc_id: str) -> list[dict]:
    with _connect() as con:
        cur = con.execute("SELECT id, created_at, label FROM versions WHERE doc_id = ? ORDER BY created_at DESC",
                          (doc_id,))
        return [{"id": r[0], "created_at": r[1], "label": r[2]} for r in cur.fetchall()]


def get_version(doc_id: str, version_id: str) -> dict | None:
    with _connect() as con:
        row = con.execute("SELECT data, created_at, label FROM versions WHERE doc_id = ? AND id = ?",
                          (doc_id, version_id)).fetchone()
        if not row:
            return None
        return {"data": json.loads(row[0]), "created_at": row[1], "label": row[2]}


def restore_version(doc_id: str, version_id: str) -> dict | None:
    current = get_document(doc_id)
    version = get_version(doc_id, version_id)
    if not current or not version:
        return None
    with _connect() as con:
        _snapshot(con, doc_id, current["document"], label="before restore")
    data = version["data"]
    data["id"] = doc_id
    return save_document(data)


def diff_texts(old: str, new: str) -> str:
    return "".join(difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile="before", tofile="after"))


# ---------------- comments ----------------

def list_comments(doc_id: str, include_resolved: bool = True) -> list[dict]:
    with _connect() as con:
        q = "SELECT id, block_id, author, text, resolved, created_at FROM comments WHERE doc_id = ?"
        if not include_resolved:
            q += " AND resolved = 0"
        cur = con.execute(q + " ORDER BY created_at", (doc_id,))
        return [{"id": r[0], "block_id": r[1], "author": r[2], "text": r[3],
                 "resolved": bool(r[4]), "created_at": r[5]} for r in cur.fetchall()]


def add_comment(doc_id: str, block_id: str, author: str, text: str) -> dict:
    cid = uuid.uuid4().hex[:12]
    now = time.time()
    with _connect() as con:
        con.execute("INSERT INTO comments (id, doc_id, block_id, author, text, resolved, created_at) "
                    "VALUES (?, ?, ?, ?, ?, 0, ?)",
                    (cid, doc_id, block_id or "", (author or "").strip()[:60], (text or "").strip(), now))
    return {"id": cid, "block_id": block_id or "", "author": (author or "").strip()[:60],
            "text": (text or "").strip(), "resolved": False, "created_at": now}


def update_comment(doc_id: str, comment_id: str, text: str | None = None,
                   resolved: bool | None = None) -> dict | None:
    with _connect() as con:
        row = con.execute("SELECT id, block_id, author, text, resolved, created_at FROM comments "
                          "WHERE doc_id = ? AND id = ?", (doc_id, comment_id)).fetchone()
        if not row:
            return None
        new_text = row[3] if text is None else text.strip()
        new_resolved = row[4] if resolved is None else int(bool(resolved))
        con.execute("UPDATE comments SET text = ?, resolved = ? WHERE doc_id = ? AND id = ?",
                    (new_text, new_resolved, doc_id, comment_id))
        return {"id": row[0], "block_id": row[1], "author": row[2], "text": new_text,
                "resolved": bool(new_resolved), "created_at": row[5]}


def delete_comment(doc_id: str, comment_id: str) -> bool:
    with _connect() as con:
        cur = con.execute("DELETE FROM comments WHERE doc_id = ? AND id = ?", (doc_id, comment_id))
        return cur.rowcount > 0


# ---------------- user templates ----------------

def list_user_templates() -> list[dict]:
    with _connect() as con:
        cur = con.execute("SELECT id, name, description, created_at FROM user_templates ORDER BY created_at DESC")
        return [{"id": r[0], "name": r[1], "description": r[2], "created_at": r[3]} for r in cur.fetchall()]


def get_user_template(template_id: str) -> dict | None:
    with _connect() as con:
        row = con.execute("SELECT id, name, description, data FROM user_templates WHERE id = ?",
                          (template_id,)).fetchone()
        if not row:
            return None
        return {"id": row[0], "name": row[1], "description": row[2], "document": json.loads(row[3])}


def save_user_template(name: str, description: str, data: dict) -> dict:
    tid = uuid.uuid4().hex[:12]
    with _connect() as con:
        con.execute("INSERT INTO user_templates (id, name, description, created_at, data) VALUES (?, ?, ?, ?, ?)",
                    (tid, (name or "Untitled template").strip(), (description or "").strip(),
                     time.time(), json.dumps(data, ensure_ascii=False)))
    return {"id": tid, "name": name}


def delete_user_template(template_id: str) -> bool:
    with _connect() as con:
        cur = con.execute("DELETE FROM user_templates WHERE id = ?", (template_id,))
        return cur.rowcount > 0
