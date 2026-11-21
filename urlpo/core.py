import os
import re
import hashlib
from pathlib import Path
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

# Patterns
URL_RE = re.compile(
    r"""(?i)\b(?:https?://|//)[^\s"'<>\\)]+|url\(\s*['"]?([^)'"]+)['"]?\s*\)""",
    re.IGNORECASE,
)
HTML_ATTRS = ("href", "src", "data-src", "poster", "action", "content")


def extract_urls(content: str, base_url: str | None = None, filetype: str = "html") -> set[str]:
    """Extract absolute URLs from file content."""
    urls: set[str] = set()

    if filetype in ("html", "htm"):
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup.find_all(True):
            for attr in HTML_ATTRS:
                val = tag.get(attr)
                if val and isinstance(val, str):
                    urls.add(val.strip())
        # meta refresh, etc.
        for meta in soup.find_all("meta", attrs={"http-equiv": re.compile("refresh", re.I)}):
            content_attr = meta.get("content", "")
            m = re.search(r"url=(.+)", content_attr, re.I)
            if m:
                urls.add(m.group(1).strip())

    # Always run regex for JS/CSS and extra HTML
    for m in URL_RE.finditer(content):
        u = m.group(1) if m.group(1) else m.group(0)
        u = u.strip().strip("'\"")
        if u:
            urls.add(u)

    # Make absolute if base given
    cleaned = set()
    for u in urls:
        if u.startswith(("data:", "javascript:", "mailto:", "#")):
            continue
        if u.startswith("//"):
            u = "https:" + u
        if base_url and not u.startswith(("http://", "https://")):
            u = urljoin(base_url, u)
        if u.startswith(("http://", "https://")):
            cleaned.add(u.split("#")[0])  # drop fragment

    return cleaned


def safe_filename(url: str) -> str:
    """Create a safe local filename from URL."""
    parsed = urlparse(url)
    name = os.path.basename(parsed.path) or "index"
    # limit length + hash to avoid collisions
    h = hashlib.md5(url.encode()).hexdigest()[:8]
    if len(name) > 80:
        name = name[:70]
    return f"{h}_{name}"


def download_one(url: str, dest_dir: Path, timeout: int = 15) -> tuple[str, bool, str]:
    """Download single URL. Returns (url, success, message)."""
    try:
        r = requests.get(url, timeout=timeout, stream=True, headers={
            "User-Agent": "urlpo/0.1 (Termux)"
        })
        r.raise_for_status()
        fname = safe_filename(url)
        path = dest_dir / fname
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return url, True, str(path)
    except Exception as e:
        return url, False, str(e)


def process_file(
    filepath: str | Path,
    out_dir: str | Path = "UrlPo",
    base_url: str | None = None,
    workers: int = 8,
) -> dict:
    """
    Read file → extract URLs → download into out_dir.
    Returns summary dict.
    """
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    content = path.read_text(encoding="utf-8", errors="ignore")
    ext = path.suffix.lower().lstrip(".")
    filetype = "html" if ext in ("html", "htm") else ext

    urls = extract_urls(content, base_url=base_url, filetype=filetype)
    dest = Path(out_dir)
    dest.mkdir(parents=True, exist_ok=True)

    results = {"total": len(urls), "ok": 0, "fail": 0, "files": []}

    if not urls:
        return results

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(download_one, u, dest): u for u in urls}
        for fut in as_completed(futures):
            url, success, msg = fut.result()
            if success:
                results["ok"] += 1
                results["files"].append(msg)
            else:
                results["fail"] += 1
                print(f"[fail] {url} → {msg}")

    return results
