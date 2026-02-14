#!/usr/bin/env python3
"""
Big5 String Extractor - Extract Chinese strings from original C source files.

Usage:
  python -X utf8 big5_extract.py <source.c>                # Extract and show all Chinese strings
  python -X utf8 big5_extract.py <source.c> --line 400     # Show specific line decoded
  python -X utf8 big5_extract.py <source.c> --verify       # Cross-reference with CStr.cs

How it works:
  1. Reads original C source file using cp950 (Microsoft Big5 extension) codec
  2. Extracts all C string literals containing Chinese characters
  3. Decodes them to UTF-8 for display

IMPORTANT: Uses cp950 (NOT big5) codec because:
  - Standard big5 codec cannot decode \xF9xx range (Microsoft extension area)
  - Characters like 裏 (U+88CF, cp950: \xF9\xD8) would produce U+FFFD with big5
  - cp950 is the correct codec for files created on Windows/DOS systems

Requires: Python 3.8+
Encoding: Always run with -X utf8 flag on Windows
"""

import re
import sys
import io
import argparse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
# TODO: 根據你的專案修改以下路徑
SRC_DIR = PROJECT_ROOT / 'SRC'  # ← 改為你的 C 原始碼目錄
CSHARP_ROOT = PROJECT_ROOT / 'YourCSharpProject'  # ← 改為你的 C# 專案目錄
CSTR_FILE = CSHARP_ROOT / 'Src' / 'CStr.cs'  # ← 改為你的 CStr.cs 路徑

CHINESE_RE = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')


def read_big5_file(filepath):
    """Read a Big5-encoded file using cp950 codec."""
    with open(filepath, 'rb') as f:
        raw = f.read()
    lines = []
    for line_bytes in raw.split(b'\n'):
        try:
            lines.append(line_bytes.decode('cp950'))
        except UnicodeDecodeError:
            lines.append(line_bytes.decode('cp950', errors='replace'))
    return lines


def extract_c_strings(lines):
    """Extract C string literals from decoded source lines."""
    results = []
    for i, line in enumerate(lines, 1):
        # Find string literals
        for m in re.finditer(r'"((?:[^"\\]|\\.)*)"', line):
            content = m.group(1)
            if CHINESE_RE.search(content):
                results.append({
                    'line': i,
                    'raw': content,
                    'context': line.strip()[:120],
                })
    return results


def main():
    parser = argparse.ArgumentParser(description='Big5 String Extractor')
    parser.add_argument('source', help='C source file (e.g., ACT_OBJ.C)')
    parser.add_argument('--line', type=int, help='Show specific line number decoded')
    parser.add_argument('--verify', action='store_true', help='Cross-reference with CStr.cs')
    args = parser.parse_args()

    source = Path(args.source)
    if not source.exists():
        source = SRC_DIR / args.source
    if not source.exists():
        print(f'Error: {args.source} not found')
        sys.exit(1)

    lines = read_big5_file(source)
    print(f'Read {len(lines)} lines from {source.name} (cp950)')

    if args.line:
        idx = args.line - 1
        if 0 <= idx < len(lines):
            print(f'L{args.line}: {lines[idx].rstrip()}')
        else:
            print(f'Line {args.line} out of range (1-{len(lines)})')
        return

    strings = extract_c_strings(lines)
    print(f'Found {len(strings)} Chinese string literals\n')

    if args.verify and CSTR_FILE.exists():
        # Load CStr values for cross-reference
        cstr_content = CSTR_FILE.read_text(encoding='utf-8')
        cstr_values = set()
        for m in re.finditer(r'public\s+const\s+string\s+\w+\s*=\s*"((?:[^"\\]|\\.)*)"\s*;', cstr_content):
            cstr_values.add(m.group(1))

        matched = 0
        for s in strings:
            status = 'OK' if s['raw'] in cstr_values else 'MISSING'
            if status == 'MISSING':
                print(f'L{s["line"]:4d} [{status}]: "{s["raw"][:80]}"')
            else:
                matched += 1
        print(f'\n{matched}/{len(strings)} strings found in CStr.cs')
    else:
        for s in strings:
            print(f'L{s["line"]:4d}: "{s["raw"][:80]}"')


if __name__ == '__main__':
    main()
