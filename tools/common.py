"""Shared helpers: repository paths, the page catalog, and ABC tune splitting."""

import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to a legacy code page

ROOT = Path(__file__).resolve().parent.parent
SCANS = ROOT / "original-pdf-scans"
CATALOG = ROOT / "catalog"
WORKS = ROOT / "works"
RENDER = ROOT / ".render"  # git-ignored scratch output

WORK_NAMES = ("arban", "clarke", "rochut")
LABEL_RE = re.compile(r"^(b[1-3]-)?(p\d{3}|f\d{2}|r\d{2}|z\d{2})$")
MUSIC_ID_RE = re.compile(r"^(arban|clarke|rochut)-((?:b[1-3]-)?(?:p\d{3}|f\d{2}|r\d{2}|z\d{2}))-(\d{2})$")
MUSIC_REF_RE = re.compile(r"\[♪ ([a-z0-9-]+)\]\(([^)]*)\)")


@dataclass(frozen=True)
class Page:
    work: str
    label: str
    printed: str
    source: str
    pdf_page: int  # 1-based page index within the source PDF
    chunk: str
    note: str

    @property
    def pdf_path(self) -> Path:
        return SCANS / self.source

    @property
    def md_path(self) -> Path:
        return WORKS / self.work / "pages" / f"{self.label}.md"

    @property
    def abc_path(self) -> Path:
        return WORKS / self.work / "abc" / f"{self.label}.abc"

    def music_id(self, x: int) -> str:
        return f"{self.work}-{self.label}-{x:02d}"


def load_pages() -> list[Page]:
    with open(CATALOG / "pages.csv", newline="", encoding="utf-8") as fh:
        return [
            Page(r["work"], r["label"], r["printed"], r["source"], int(r["pdf_page"]), r["chunk"], r["note"])
            for r in csv.DictReader(fh)
        ]


def find_page(pages: list[Page], work: str, label: str) -> Page:
    for p in pages:
        if p.work == work and p.label == label:
            return p
    raise SystemExit(f"no page {work}/{label} in catalog/pages.csv")


def resolve_pages(pages: list[Page], target: str, labels: list[str]) -> list[Page]:
    """`target` is a chunk id (arban-07) or a work name followed by page labels."""
    if target in WORK_NAMES:
        if not labels:
            raise SystemExit(f"give one or more page labels for {target}, e.g. p005")
        return [find_page(pages, target, lab) for lab in labels]
    chunk = [p for p in pages if p.chunk == target]
    if not chunk:
        raise SystemExit(f"unknown chunk or work: {target}")
    if labels:
        chunk = [p for p in chunk if p.label in labels]
    return chunk


def split_tunes(abc_text: str) -> tuple[str, list[tuple[int, str]]]:
    """Split an ABC tunebook into (preamble, [(X number, tune text starting at 'X:')])."""
    parts = re.split(r"^\s*X:", abc_text, flags=re.M)
    tunes = []
    for part in parts[1:]:
        m = re.match(r"\s*(\d+)", part)
        if not m:
            raise ValueError("X: field without a number")
        tunes.append((int(m.group(1)), "X:" + part))
    return parts[0], tunes
