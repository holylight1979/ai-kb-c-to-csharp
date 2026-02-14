#!/usr/bin/env python3
"""
CStr Add Missing - Scan C# source files and add missing strings to CStr.cs.

Usage:
  python -X utf8 cstr_add_missing.py                       # Scan all known source files
  python -X utf8 cstr_add_missing.py --dry-run              # Preview without modifying CStr.cs

How it works:
  1. Parses CStr.cs to collect all existing constant values
  2. Scans each source file for string literals not in CStr.cs
  3. Deduplicates across files
  4. Generates new REGION_NNN constants and inserts into the correct #region

Output:
  - Prints per-file counts of missing strings
  - Inserts new constants before each #endregion marker
  - Each new batch is marked with "--- Added by cstr_add_missing ---"

Typical workflow:
  1. Run cstr_add_missing.py to add new strings to CStr.cs
  2. Run cstr_replacer.py --apply on each source file
  3. Run dotnet build to verify

Requires: Python 3.8+
Encoding: Always run with -X utf8 flag on Windows
"""

import re
import sys
import io
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Compute project paths relative to this script
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
# TODO: 根據你的專案修改以下路徑
CSHARP_ROOT = PROJECT_ROOT / 'YourCSharpProject'  # ← 改為你的 C# 專案目錄
CSTR_FILE = CSHARP_ROOT / 'MudGM' / 'Src' / 'CStr.cs'
SRC_DIR = CSHARP_ROOT / 'MudGM' / 'Src'

# TODO: 根據你的專案修改此映射表
# 格式: 'C#檔案名': 'CStr前綴'
FILE_TO_PREFIX = {
    'EXAMPLE.C.cs': 'EXAMPLE',  # ← 修改為你的檔案
    # 'ANOTHER.C.cs': 'ANOTHER',
}

SKIP_STRINGS = {
    '', ' ', '  ', '    ', '\n', '\r', '\n\r', '\r\n',
    '\t', '0', '1', '#', '$', '~', '.', ',', ':', ';',
    'S', 'M', 'O', 'P', 'G', 'E', 'D', 'R', 'B', '*',
    'true', 'false', 'null', 'none',
}


def unescape_csharp(s):
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            c = s[i + 1]
            if c == 'n': result.append('\n')
            elif c == 'r': result.append('\r')
            elif c == 't': result.append('\t')
            elif c == '\\': result.append('\\')
            elif c == '"': result.append('"')
            elif c == '\'': result.append("'")
            elif c == '0': result.append('\0')
            elif c == 'x':
                hex_str = ''
                j = i + 2
                while j < len(s) and j < i + 6 and s[j] in '0123456789abcdefABCDEF':
                    hex_str += s[j]; j += 1
                if hex_str: result.append(chr(int(hex_str, 16))); i = j; continue
                else: result.append('\\x')
            elif c == 'u':
                hex_str = s[i+2:i+6]
                if len(hex_str) == 4 and all(c in '0123456789abcdefABCDEF' for c in hex_str):
                    result.append(chr(int(hex_str, 16))); i += 6; continue
                else: result.append('\\u')
            else: result.append('\\'); result.append(c)
            i += 2
        else: result.append(s[i]); i += 1
    return ''.join(result)


def escape_for_csharp(s):
    result = []
    for c in s:
        if c == '\\': result.append('\\\\')
        elif c == '"': result.append('\\"')
        elif c == '\n': result.append('\\n')
        elif c == '\r': result.append('\\r')
        elif c == '\t': result.append('\\t')
        elif c == '\0': result.append('\\0')
        elif c == '\x1b': result.append('\\x1b')
        else: result.append(c)
    return ''.join(result)


def parse_existing_cstr():
    content = CSTR_FILE.read_text(encoding='utf-8')
    existing_values = set()
    max_numbers = defaultdict(int)

    for m in re.finditer(r'public\s+const\s+string\s+(\w+)\s*=\s*"((?:[^"\\]|\\.)*)"\s*;', content):
        name, raw = m.group(1), m.group(2)
        existing_values.add(unescape_csharp(raw))
        num_m = re.match(r'(\w+?)_(\d+)$', name)
        if num_m:
            prefix, num = num_m.group(1), int(num_m.group(2))
            max_numbers[prefix] = max(max_numbers[prefix], num)

    for m in re.finditer(r'public\s+static\s+readonly\s+string\[\]\s+\w+\s*=\s*\{([^}]*)\}\s*;', content):
        for item in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1)):
            existing_values.add(unescape_csharp(item))

    return existing_values, max_numbers, content


def scan_file_for_missing(filepath, existing_values):
    content = filepath.read_text(encoding='utf-8')
    missing = []

    for line_num, line in enumerate(content.split('\n'), 1):
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('/*'): continue
        if 'public const string' in line or 'public static readonly string[]' in line: continue
        if 'CStr.' in line: continue

        # Regular strings
        for m in re.finditer(r'(?<!\$)(?<!@)"((?:[^"\\]|\\.)*)"', line):
            val = unescape_csharp(m.group(1))
            if val in SKIP_STRINGS or len(val) < 2 or val in existing_values: continue
            missing.append({'line': line_num, 'value': val, 'raw_escaped': m.group(1),
                            'type': 'regular', 'context': stripped[:120]})

        # Interpolated strings -> extract format template
        for m in re.finditer(r'\$"((?:[^"\\]|\\.)*)"', line):
            interp = m.group(1)
            parts = re.split(r'\{([^}]+)\}', interp)
            if len(parts) <= 1: continue
            template_parts = []
            var_idx = 0
            for i, part in enumerate(parts):
                if i % 2 == 0: template_parts.append(part)
                else: template_parts.append('{' + str(var_idx) + '}'); var_idx += 1
            template = unescape_csharp(''.join(template_parts))
            if template in SKIP_STRINGS or len(template) < 2 or template in existing_values: continue
            missing.append({'line': line_num, 'value': template,
                            'raw_escaped': escape_for_csharp(template),
                            'type': 'format', 'context': stripped[:120]})

        # Verbatim strings
        for m in re.finditer(r'@"((?:[^"]|"")*)"', line):
            val = m.group(1).replace('""', '"')
            if val in SKIP_STRINGS or len(val) < 2 or val in existing_values: continue
            missing.append({'line': line_num, 'value': val, 'raw_escaped': escape_for_csharp(val),
                            'type': 'verbatim', 'context': stripped[:120]})

    return missing


def insert_into_cstr(content, additions_by_prefix, max_numbers):
    prefix_to_region = {
        'M_USE': 'Common Strings', 'CONST': 'CONST', 'COMM': 'COMM',
        'DB': 'DB', 'HANDLER': 'HANDLER', 'INTERP': 'INTERP',
        'UPDATE': 'UPDATE', 'SAVE': 'SAVE', 'ACTCOMM': 'ACTCOMM',
        'ACTINFO': 'ACTINFO', 'ACTMOVE': 'ACTMOVE', 'ACTOBJ': 'ACT_OBJ.C',
        'ACTWIZ': 'ACTWIZ', 'FIGHT': 'FIGHT',
    }

    lines = content.split('\n')
    insertions = []

    for prefix, items in additions_by_prefix.items():
        region_name = prefix_to_region.get(prefix, prefix)
        next_num = max_numbers.get(prefix, 0) + 1

        new_lines = []
        for item in items:
            name = f'{prefix}_{next_num:03d}'
            new_lines.append(f'    public const string {name} = "{item["raw_escaped"]}";')
            next_num += 1

        # Find #endregion for this region
        in_region = False
        endregion_idx = None
        for i, line in enumerate(lines):
            if f'#region {region_name}' in line:
                in_region = True
            elif in_region and '#endregion' in line:
                endregion_idx = i
                break

        if endregion_idx is not None:
            text = '\n    // --- Added by cstr_add_missing ---\n' + '\n'.join(new_lines) + '\n'
            insertions.append((endregion_idx, text))
        else:
            print(f'  WARNING: region "{region_name}" not found for prefix {prefix}')

    insertions.sort(key=lambda x: x[0], reverse=True)
    for idx, text in insertions:
        lines.insert(idx, text)

    return '\n'.join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='CStr Add Missing')
    parser.add_argument('--dry-run', action='store_true', help='Preview without modifying CStr.cs')
    args = parser.parse_args()

    existing_values, max_numbers, cstr_content = parse_existing_cstr()
    print(f'Existing CStr values: {len(existing_values)}')

    source_files = sorted(FILE_TO_PREFIX.keys())
    all_missing = defaultdict(list)
    all_values_seen = set()
    total = 0

    for filename in source_files:
        filepath = SRC_DIR / filename
        if not filepath.exists(): continue
        prefix = FILE_TO_PREFIX[filename]
        missing = scan_file_for_missing(filepath, existing_values)

        deduped = []
        for item in missing:
            if item['value'] not in all_values_seen:
                all_values_seen.add(item['value'])
                existing_values.add(item['value'])
                deduped.append(item)

        if deduped:
            all_missing[prefix].extend(deduped)
            print(f'  {filename}: {len(deduped)} new')
            total += len(deduped)

    print(f'\nTotal to add: {total}')

    if args.dry_run:
        print('(Dry run - CStr.cs not modified)')
        return

    if total > 0:
        new_content = insert_into_cstr(cstr_content, all_missing, max_numbers)
        CSTR_FILE.write_text(new_content, encoding='utf-8')
        print(f'CStr.cs updated with {total} new constants.')


if __name__ == '__main__':
    main()
