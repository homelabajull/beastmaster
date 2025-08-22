#!/usr/bin/env python3
"""
BEASTMASTER — a safe homelab multi-tool (aka "weaponized" utility 😉)

Subcommands:
  duyung        Print a pretty tree of a directory.
  harimau       Find files by glob/regex/name and basic metadata filters.
  cacing-pita   Copy files by name or extension into a target directory.
  seladang      Copy or move arbitrary files to a target directory.
  buaya         Report disk usage (top-N largest files/dirs).
  ketam         Compute/verify checksums (sha256) for files.

All functionality is defensive/administrative and **not** intended for
harming networks, systems, or data. Use responsibly on your own machines.
"""

from __future__ import annotations
import argparse
import hashlib
import os
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator, List, Optional, Tuple

# ---------------------------
# logic fx
# ---------------------------

def human_size(num: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num < 1024 or unit == "TB":
            return f"{num:.2f} {unit}" if unit != "B" else f"{num} {unit}"
        num /= 1024
    return f"{num:.2f} TB"


def iter_files(base: Path) -> Iterator[Path]:
    for p in base.rglob("*"):
        if p.is_file():
            yield p


# ---------------------------
# duyung — tree printer
# ---------------------------

def print_tree(path: Path, prefix: str = "") -> None:
    entries = sorted(list(path.iterdir()), key=lambda p: (not p.is_dir(), p.name.lower()))
    total = len(entries)
    for i, entry in enumerate(entries):
        connector = "└── " if i == total - 1 else "├── "
        print(prefix + connector + entry.name)
        if entry.is_dir():
            extension = "    " if i == total - 1 else "│   "
            print_tree(entry, prefix + extension)


# ---------------------------
# harimau — smart finder
# ---------------------------
@dataclass
class FindFilters:
    name: Optional[str] = None           # exact filename match
    glob: Optional[str] = None           # e.g., "*.mkv"
    regex: Optional[str] = None          # python regex against name
    min_size: Optional[int] = None       # bytes
    max_size: Optional[int] = None       # bytes
    changed_within_days: Optional[int] = None


def harimau(base: Path, filters: FindFilters) -> List[Path]:
    results: List[Path] = []
    pattern = re.compile(filters.regex) if filters.regex else None
    since = None
    if filters.changed_within_days is not None:
        since = datetime.now().timestamp() - (filters.changed_within_days * 86400)

    for p in iter_files(base):
        st = p.stat()
        if filters.name and p.name != filters.name:
            continue
        if filters.glob and not p.match(filters.glob):
            continue
        if pattern and not pattern.search(p.name):
            continue
        if filters.min_size is not None and st.st_size < filters.min_size:
            continue
        if filters.max_size is not None and st.st_size > filters.max_size:
            continue
        if since is not None and st.st_mtime < since:
            continue
        results.append(p)
    return results


# ---------------------------
# cacing-pita — selective copy
# ---------------------------

def cacing_pita(
    src: Path,
    dst: Path,
    names: List[str],
    exts: List[str],
    days: Optional[int],
    limit: Optional[int],
    overwrite: bool,
    dry_run: bool,
) -> Tuple[int, int]:
    if not dst.exists():
        if dry_run:
            print(f"[dry-run] would create: {dst}")
        else:
            dst.mkdir(parents=True, exist_ok=True)

    exts = [e.lower().lstrip('.') for e in exts]
    names_set = set(names)

    matched = 0
    copied = 0
    cutoff = None
    if days is not None:
        cutoff = datetime.now().timestamp() - days * 86400

    for p in iter_files(src):
        st = p.stat()
        if cutoff is not None and st.st_mtime < cutoff:
            continue
        if names_set and p.name not in names_set:
            pass
        elif names_set and p.name in names_set:
            pass
        if exts:
            if p.suffix.lower().lstrip('.') not in exts:
                if not (names_set and p.name in names_set):
                    continue
        elif not names_set:
            continue

        matched += 1
        if limit is not None and copied >= limit:
            break
        target = dst / p.name
        if target.exists() and not overwrite:
            print(f"skip exists: {target}")
            continue
        if dry_run:
            print(f"[dry-run] copy {p} -> {target}")
            copied += 1
        else:
            shutil.copy2(p, target)
            print(f"copied {p} -> {target}")
            copied += 1

    return matched, copied


# ---------------------------
# seladang — generic copy/move
# ---------------------------
def seladang(files: List[Path], dst: Path, move: bool, overwrite: bool, dry_run: bool) -> None:
    if not dst.exists():
        if dry_run:
            print(f"[dry-run] would create: {dst}")
        else:
            dst.mkdir(parents=True, exist_ok=True)

    for f in files:
        if not f.exists():
            print(f"missing: {f}")
            continue
        target = dst / f.name
        if target.exists() and not overwrite:
            print(f"skip exists: {target}")
            continue
        action = "move" if move else "copy"
        if dry_run:
            print(f"[dry-run] {action} {f} -> {target}")
        else:
            if move:
                shutil.move(str(f), target)
            else:
                shutil.copy2(f, target)
            print(f"{action}d {f} -> {target}")


# ---------------------------
# buaya — disk usage report
# ---------------------------

def buaya(base: Path, top: int, dirs: bool, files: bool) -> None:
    sizes: List[Tuple[int, Path]] = []

    def dir_size(p: Path) -> int:
        total = 0
        for q in p.rglob("*"):
            if q.is_file():
                try:
                    total += q.stat().st_size
                except FileNotFoundError:
                    pass
        return total

    if files:
        for p in iter_files(base):
            try:
                sizes.append((p.stat().st_size, p))
            except FileNotFoundError:
                pass

    if dirs:
        for p in base.rglob("*"):
            if p.is_dir():
                try:
                    sizes.append((dir_size(p), p))
                except PermissionError:
                    pass

    sizes.sort(reverse=True, key=lambda t: t[0])
    for sz, p in sizes[:top]:
        print(f"{human_size(sz):>10}  {p}")


# ---------------------------
# tapir — checksums
# ---------------------------
import hashlib

def sha256_file(p: Path, bufsize: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        while True:
            chunk = f.read(bufsize)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def tapir_compute(paths: List[Path], output: Optional[Path]) -> None:
    lines = []
    for p in paths:
        if p.is_dir():
            for f in iter_files(p):
                digest = sha256_file(f)
                line = f"{digest}  {f}"
                print(line)
                lines.append(line)
        elif p.is_file():
            digest = sha256_file(p)
            line = f"{digest}  {p}"
            print(line)
            lines.append(line)
    if output:
        output.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"written: {output}")


def tapir_verify(manifest: Path) -> int:
    mismatches = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, path_str = line.split(None, 1)
        path = Path(path_str.strip())
        if not path.exists():
            print(f"missing: {path}")
            mismatches += 1
            continue
        actual = sha256_file(path)
        if actual != digest:
            print(f"mismatch: {path}\n  expected {digest}\n  actual   {actual}")
            mismatches += 1
    if mismatches == 0:
        print("All good — no mismatches.")
    return mismatches


# ---------------------------
# parser
# ---------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="beastmaster", description="Safe homelab multi-tool")
    sub = p.add_subparsers(dest="cmd", required=True)

    # duyung
    pd = sub.add_parser("duyung", help="print a directory tree")
    pd.add_argument("path", type=Path, help="directory to print")

    # harimau
    ph = sub.add_parser("harimau", help="find files with filters")
    ph.add_argument("base", type=Path, help="base directory")
    ph.add_argument("--name", help="exact filename match")
    ph.add_argument("--glob", help="glob pattern, e.g. '*.mkv'")
    ph.add_argument("--regex", help="regex against filename")
    ph.add_argument("--min-size", type=int, help="min size (bytes)")
    ph.add_argument("--max-size", type=int, help="max size (bytes)")
    ph.add_argument("--changed-within-days", type=int, help="modified within N days")

    # cacing-pita
    pc = sub.add_parser("cacing-pita", help="copy by name/extension into a folder")
    pc.add_argument("src", type=Path, help="source directory")
    pc.add_argument("dst", type=Path, help="destination directory")
    pc.add_argument("--name", action="append", default=[], help="filename to copy (repeatable)")
    pc.add_argument("--ext", action="append", default=[], help="extension (without dot), repeatable")
    pc.add_argument("--days", type=int, help="only files modified within N days")
    pc.add_argument("--limit", type=int, help="copy at most N files")
    pc.add_argument("--overwrite", action="store_true", help="allow overwriting existing files")
    pc.add_argument("--dry-run", action="store_true", help="show actions without copying")

    # seladang
    psel = sub.add_parser("seladang", help="copy or move files to a target folder")
    psel.add_argument("dst", type=Path, help="destination directory")
    psel.add_argument("files", nargs="+", type=Path, help="files to copy/move")
    psel.add_argument("--move", action="store_true", help="move instead of copy")
    psel.add_argument("--overwrite", action="store_true", help="allow overwriting existing files")
    psel.add_argument("--dry-run", action="store_true", help="show actions without changing anything")

    # buaya
    pb = sub.add_parser("buaya", help="report largest files/dirs")
    pb.add_argument("base", type=Path, help="base directory")
    pb.add_argument("--top", type=int, default=20, help="show top N entries")
    pb.add_argument("--dirs", action="store_true", help="include directories")
    pb.add_argument("--files", action="store_true", help="include files")

    # ketam
    pk = sub.add_parser("tapir", help="checksums: compute or verify sha256")
    mode = pk.add_mutually_exclusive_group(required=True)
    mode.add_argument("--compute", nargs="+", type=Path, help="files or directories")
    mode.add_argument("--verify", type=Path, help="manifest file produced by --compute")
    pk.add_argument("--output", type=Path, help="write compute output to a file")

    return p

# ---------------------------
# main
# ---------------------------
def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.cmd == "duyung":
        base = args.path
        if not base.is_dir():
            print(f"not a directory: {base}", file=sys.stderr)
            return 2
        print(base.resolve().name)
        print_tree(base)
        return 0

    if args.cmd == "harimau":
        filters = FindFilters(
            name=args.name,
            glob=args.glob,
            regex=args.regex,
            min_size=args.min_size,
            max_size=args.max_size,
            changed_within_days=args.changed_within_days,
        )
        for p in harimau(args.base, filters):
            st = p.stat()
            print(f"{human_size(st.st_size):>10}  {datetime.fromtimestamp(st.st_mtime)}  {p}")
        return 0

    if args.cmd == "cacing-pita":
        matched, copied = cacing_pita(
            src=args.src,
            dst=args.dst,
            names=args.name,
            exts=args.ext,
            days=args.days,
            limit=args.limit,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
        )
        print(f"matched: {matched}, copied: {copied}")
        return 0

    if args.cmd == "seladang":
        seladang(
            files=args.files,
            dst=args.dst,
            move=args.move,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
        )
        return 0

    if args.cmd == "buaya":
        include_dirs = args.dirs or (not args.files)
        include_files = args.files or (not args.dirs)
        buaya(args.base, args.top, include_dirs, include_files)
        return 0

    if args.cmd == "tapir":
        if args.compute:
            ketam_compute(args.compute, args.output)
        elif args.verify:
            mismatches = ketam_verify(args.verify)
            return 1 if mismatches else 0
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
