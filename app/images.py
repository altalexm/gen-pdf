"""Image pipeline: SSRF-safe loading, size caps and normalization.

Threat model: block images may point at arbitrary URLs. The loader denies
private/loopback/link-local targets (cloud metadata endpoints), caps
download size and dimensions, and re-encodes through Pillow so the PDF
renderer only ever sees sanitized bytes.
"""
from __future__ import annotations

import base64
import io
import ipaddress
import socket
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image, UnidentifiedImageError

MAX_DOWNLOAD_BYTES = 8 * 1024 * 1024
MAX_DATAURL_BYTES = 10 * 1024 * 1024
MAX_DIMENSION = 1600
FETCH_TIMEOUT = 10


def _host_is_public(hostname: str) -> bool:
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError:
            return False
        if not ip.is_global:
            return False
    return True


def _download(url: str) -> bytes:
    scheme = urlparse(url).scheme.lower()
    if scheme not in ("http", "https"):
        raise ValueError(f"unsupported image scheme: {scheme}")
    host = urlparse(url).hostname or ""
    if not _host_is_public(host):
        raise ValueError("image host is not public")
    req = urllib.request.Request(url, headers={"User-Agent": "gen-pdf/1.0 (+image fetch)"})
    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
        try:
            declared = int(resp.info().get("Content-Length") or 0)
        except (TypeError, ValueError):
            declared = 0
        if declared > MAX_DOWNLOAD_BYTES:
            raise ValueError("image too large")
        data = resp.read(MAX_DOWNLOAD_BYTES + 1)
    if len(data) > MAX_DOWNLOAD_BYTES:
        raise ValueError("image too large")
    return data


def load_raw(src: str) -> bytes:
    """Fetch raw bytes or raise ValueError. Never returns untrusted paths."""
    src = (src or "").strip()
    if not src:
        raise ValueError("empty image source")
    if src.startswith("data:"):
        if len(src) > MAX_DATAURL_BYTES:
            raise ValueError("embedded image too large")
        try:
            return base64.b64decode(src.split(",", 1)[1])
        except Exception as e:
            raise ValueError("invalid data URL") from e
    if src.startswith(("http://", "https://")):
        return _download(src)
    if "://" in src:
        raise ValueError("unsupported image scheme")
    p = Path(src)
    if p.is_file() and p.stat().st_size <= MAX_DOWNLOAD_BYTES:
        return p.read_bytes()
    raise ValueError("image not found")


def normalize(data: bytes, max_dimension: int = MAX_DIMENSION) -> bytes:
    """Re-encode through Pillow: downscale huge images, flatten to a
    PDF-friendly format. Raises ValueError on non-images."""
    try:
        with Image.open(io.BytesIO(data)) as img:
            img.draft(img.mode, (max_dimension, max_dimension))
            img.load()
            has_alpha = img.mode in ("RGBA", "LA") or (
                img.mode == "P" and "transparency" in img.info)
            if max(img.size) > max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)
            out = io.BytesIO()
            if has_alpha:
                img.convert("RGBA").save(out, format="PNG", optimize=True)
            else:
                img.convert("RGB").save(out, format="JPEG", quality=82, optimize=True)
            return out.getvalue()
    except (UnidentifiedImageError, OSError) as e:
        raise ValueError("not a readable image") from e


def load_image(src: str) -> bytes | None:
    """Pipeline entry point. Returns None instead of raising."""
    try:
        return normalize(load_raw(src))
    except Exception:
        return None


__all__ = ["load_image", "load_raw", "normalize",
           "MAX_DOWNLOAD_BYTES", "MAX_DATAURL_BYTES", "MAX_DIMENSION"]
