#!/usr/bin/env python3
"""
consolidator.py - Merge raw per-section Zig docs into themed reference files.

Takes the numbered markdown files produced by zig_docs_converter.py (e.g.
01-introduction.md, 02-zig-standard-library.md, ...) and consolidates them
into the themed reference files used by the skill (core-language.md,
control-flow.md, etc.).

Usage:
    python consolidator.py <input_dir> <output_dir> [--version VERSION]

Example:
    python consolidator.py ../../converter/docs-master ../references/v0.16.0 --version 0.16.0
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


# ============================================================================
# Mapping: themed file -> list of raw section file prefixes (number prefixes)
#
# Each themed file consolidates several raw sections. The raw files are named
# like "01-introduction.md", "16-struct.md", etc.  We match by the leading
# number so the mapping survives minor title changes across Zig versions.
# ============================================================================

THEME_MAP: Dict[str, dict] = {
    "core-language.md": {
        "title": "Core Language Features",
        "subtitle": "Basic Zig syntax, types, literals, variables, and operators",
        "sections": [1, 2, 3, 4, 5, 6, 8, 9, 10, 11],
    },
    "arrays-slices.md": {
        "title": "Arrays, Vectors, and Slices",
        "subtitle": "Working with sequential data structures in Zig",
        "sections": [12, 13, 15],
    },
    "pointers-references.md": {
        "title": "Pointers and References",
        "subtitle": "Low-level memory access with pointers in Zig",
        "sections": [14],
    },
    "structs-methods.md": {
        "title": "Structs and Methods",
        "subtitle": "Defining structs and implementing methods in Zig",
        "sections": [16],
    },
    "enums-unions.md": {
        "title": "Enums and Unions",
        "subtitle": "Tagged unions, enums, and variant types in Zig",
        "sections": [17, 18, 19],
    },
    "control-flow.md": {
        "title": "Control Flow",
        "subtitle": "Program flow control structures and patterns",
        "sections": [20, 21, 22, 23, 24, 25, 26, 27],
    },
    "functions-errors.md": {
        "title": "Functions and Error Handling",
        "subtitle": "Function design, error handling patterns, and type conversions",
        "sections": [28, 29, 30, 31, 32, 33],
    },
    "comptime.md": {
        "title": "Compile-Time Programming",
        "subtitle": "Compile-time code execution and metaprogramming",
        "sections": [34],
    },
    "stdlib-builtins.md": {
        "title": "Standard Library and Builtins",
        "subtitle": "Zig standard library and builtin functions",
        "sections": [35, 36, 38],
    },
    "testing-quality.md": {
        "title": "Testing and Code Quality",
        "subtitle": "Testing framework, undefined behavior, and best practices",
        "sections": [7, 39, 40, 41],
    },
    "memory-management.md": {
        "title": "Memory Management",
        "subtitle": "Memory allocation, ownership, and optimization",
        "sections": [42],
    },
    "build-system.md": {
        "title": "Build System",
        "subtitle": "Building projects with Zig",
        "sections": [43, 44, 45],
    },
    "c-interop.md": {
        "title": "C Interoperability",
        "subtitle": "Interfacing with C code and cross-compilation",
        "sections": [46, 47, 48],
    },
    "quick-reference.md": {
        "title": "Quick Reference",
        "subtitle": "Style guide, encoding, keywords, and appendix",
        "sections": [49, 50, 51, 52],
    },
}

# Sections that are stubs or should be noted but not given their own theme.
# 37 = "Async Functions" (stub in master as of 2026-04; tracked separately)
SKIPPED_SECTIONS = {37}


def find_raw_file(input_dir: Path, section_num: int) -> Optional[Path]:
    """Find the raw markdown file for a given section number."""
    prefix = f"{section_num:02d}-"
    for f in sorted(input_dir.glob(f"{prefix}*.md")):
        return f
    return None


def read_section(path: Path) -> str:
    """Read a raw section file and return its content."""
    return path.read_text(encoding="utf-8").strip()


def build_themed_file(
    title: str,
    subtitle: str,
    section_contents: List[str],
) -> str:
    """Assemble a themed reference file from section contents."""
    header = f"# {title}\n\n*{subtitle}*\n\n"
    body = "\n\n---\n\n".join(section_contents)
    return header + body + "\n"


def consolidate(input_dir: Path, output_dir: Path, version: str = "master") -> None:
    """Run the full consolidation pipeline."""
    input_dir = input_dir.resolve()
    output_dir = output_dir.resolve()

    if not input_dir.is_dir():
        print(f"Error: input directory does not exist: {input_dir}", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Track which raw sections we consume so we can warn about unmapped ones
    consumed: set = set()
    all_raw = set()
    for f in input_dir.glob("*.md"):
        m = re.match(r"^(\d+)-", f.name)
        if m:
            all_raw.add(int(m.group(1)))

    stats = []

    for themed_name, spec in THEME_MAP.items():
        section_contents: List[str] = []
        for sec_num in spec["sections"]:
            raw_path = find_raw_file(input_dir, sec_num)
            if raw_path is None:
                print(f"  Warning: no raw file for section {sec_num} "
                      f"(needed by {themed_name})", file=sys.stderr)
                continue
            content = read_section(raw_path)
            if content:
                section_contents.append(content)
                consumed.add(sec_num)

        if not section_contents:
            print(f"  Warning: {themed_name} has no content, skipping",
                  file=sys.stderr)
            continue

        output_text = build_themed_file(
            spec["title"], spec["subtitle"], section_contents
        )
        out_path = output_dir / themed_name
        out_path.write_text(output_text, encoding="utf-8")
        stats.append((themed_name, len(section_contents), len(output_text)))
        print(f"  Created {themed_name} "
              f"({len(section_contents)} sections, "
              f"{len(output_text)} bytes)")

    # Copy version-differences.md if it exists in the input, otherwise
    # create a placeholder that will be filled in manually.
    vd_src = input_dir.parent.parent / "zig-programming" / "references" / "version-differences.md"
    vd_dst = output_dir / "version-differences.md"
    if not vd_dst.exists():
        if vd_src.exists():
            vd_dst.write_text(vd_src.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"  Copied version-differences.md from existing references")
        else:
            vd_dst.write_text(
                "# Zig Version Differences\n\n"
                "<!-- TODO: update for this version -->\n",
                encoding="utf-8",
            )
            print(f"  Created placeholder version-differences.md")

    # Report unmapped sections
    unmapped = all_raw - consumed - SKIPPED_SECTIONS
    if unmapped:
        print(f"\n  Note: {len(unmapped)} raw section(s) not mapped to any theme:")
        for num in sorted(unmapped):
            raw = find_raw_file(input_dir, num)
            name = raw.name if raw else f"{num:02d}-???"
            print(f"    - {name}")

    skipped_found = all_raw & SKIPPED_SECTIONS
    if skipped_found:
        print(f"\n  Skipped sections (handled separately):")
        for num in sorted(skipped_found):
            raw = find_raw_file(input_dir, num)
            name = raw.name if raw else f"{num:02d}-???"
            print(f"    - {name}")

    print(f"\nDone: {len(stats)} themed files written to {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Consolidate raw Zig doc sections into themed reference files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python consolidator.py ../../converter/docs-master ../references/v0.16.0 --version 0.16.0
        """,
    )
    parser.add_argument("input_dir", type=Path,
                        help="Directory containing numbered raw .md files")
    parser.add_argument("output_dir", type=Path,
                        help="Output directory for themed reference files")
    parser.add_argument("--version", default="master",
                        help="Zig version label (default: master)")

    args = parser.parse_args()
    consolidate(args.input_dir, args.output_dir, args.version)


if __name__ == "__main__":
    main()
