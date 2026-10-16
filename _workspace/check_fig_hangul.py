# -*- coding: utf-8 -*-
"""Scan figure sources for Hangul inside rendered string literals."""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def hangul_strings_in_py(path: Path) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    src = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        print(f"SYNTAX {path}: {e}")
        return hits
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if re.search(r"[가-힣]", node.value):
                hits.append((node.lineno, node.value))
    return hits


def main() -> int:
    roots = [
        Path("paper/figures/_build/build_all_figures.py"),
        Path("paper/figures/_build/build_map_data.py"),
        Path("paper/figures/_build/revision_figure_data.py"),
        Path("paper/figures/_build/embed_figures.py"),
    ]
    any_str = False
    for p in roots:
        if not p.exists():
            print("missing", p)
            continue
        hits = hangul_strings_in_py(p)
        print(f"== {p} ({len(hits)} hangul string constants) ==")
        for ln, s in hits:
            any_str = True
            print(f"  L{ln}: {s[:160]!r}")
    # raw source lines with hangul (comments ok, but list for review)
    print("\n== raw hangul lines in build_all_figures.py ==")
    p = Path("paper/figures/_build/build_all_figures.py")
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if re.search(r"[가-힣]", line):
            print(f"  L{i}: {line.strip()[:150]}")
    return 0 if not any_str else 1


if __name__ == "__main__":
    raise SystemExit(main())
