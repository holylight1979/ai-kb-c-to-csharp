#!/usr/bin/env python3
"""
CStr Replacer - Replace hardcoded strings in C# source files with CStr.XXX references.

Usage:
  python -X utf8 cstr_replacer.py --analyze <source.cs>    # Dry-run analysis
  python -X utf8 cstr_replacer.py --apply <source.cs>      # Apply replacements

How it works:
  1. Parses CStr.cs to build a reverse mapping (string value -> constant name)
  2. Scans the target source file for string literals ("...", $"...", @"...")
  3. Classifies each string as EXACT match, FORMAT match, MISSING, or SKIP
  4. In --apply mode, replaces EXACT and FORMAT matches in-place

Match types:
  EXACT:  "some text" -> CStr.REGION_NNN (direct value match)
  FORMAT: $"text {var}" -> string.Format(CStr.REGION_NNN, var) (interpolation to format)
  MISSING: String not found in CStr.cs (needs manual addition first)
  SKIP: Too short or generic (e.g., " ", "\\n", single chars)

Typical workflow:
  1. Run cstr_add_missing.py to add all missing strings to CStr.cs
  2. Run cstr_replacer.py --analyze to preview replacements
  3. Run cstr_replacer.py --apply to apply
  4. Run dotnet build to verify

Requires: Python 3.8+
Encoding: Always run with -X utf8 flag on Windows
"""

import re
import sys
import io
import argparse
from pathlib import Path
from collections import defaultdict

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Compute project paths relative to this script
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent  # .claude/tools/ -> project root
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

# Strings too short or generic to warrant CStr replacement
SKIP_STRINGS = {
    '', ' ', '  ', '    ', '\n', '\r', '\n\r', '\r\n',
    '\t', '0', '1', '#', '$', '~', '.', ',', ':', ';',
    'S', 'M', 'O', 'P', 'G', 'E', 'D', 'R', 'B', '*',
    'true', 'false', 'null', 'none',
}
MIN_STRING_LENGTH = 2


def unescape_csharp(s):
    """Unescape a C# string literal value to its runtime representation."""
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
                    hex_str += s[j]
                    j += 1
                if hex_str:
                    result.append(chr(int(hex_str, 16)))
                    i = j
                    continue
                else:
                    result.append('\\x')
            elif c == 'u':
                hex_str = s[i+2:i+6]
                if len(hex_str) == 4 and all(c in '0123456789abcdefABCDEF' for c in hex_str):
                    result.append(chr(int(hex_str, 16)))
                    i += 6
                    continue
                else:
                    result.append('\\u')
            else:
                result.append('\\')
                result.append(c)
            i += 2
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


def escape_for_display(s):
    """Escape a string for human-readable display."""
    return s.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t').replace('\x1b', '\\x1b')


def parse_cstr():
    """Parse CStr.cs and return (constants, arrays, regions)."""
    content = CSTR_FILE.read_text(encoding='utf-8')
    const_pattern = re.compile(r'public\s+const\s+string\s+(\w+)\s*=\s*"((?:[^"\\]|\\.)*)"\s*;')
    constants = {}
    current_region = None
    regions = {}

    for line in content.split('\n'):
        rm = re.match(r'\s*#region\s+(.*)', line)
        if rm:
            current_region = rm.group(1).strip()
            continue
        m = const_pattern.search(line)
        if m:
            name, raw = m.group(1), m.group(2)
            constants[name] = unescape_csharp(raw)
            if current_region:
                regions[name] = current_region

    return constants, regions


def build_reverse_map(constants, preferred_prefix=None):
    """Build value -> constant name mapping with priority selection."""
    value_to_names = defaultdict(list)
    for name, value in constants.items():
        value_to_names[value].append(name)

    reverse_map = {}
    for value, names in value_to_names.items():
        if len(names) == 1:
            reverse_map[value] = names[0]
        else:
            selected = None
            if preferred_prefix:
                matches = [n for n in names if n.startswith(preferred_prefix + '_')]
                if matches:
                    selected = matches[0]
            if not selected:
                muse = [n for n in names if n.startswith('M_USE_')]
                if muse:
                    selected = muse[0]
            reverse_map[value] = selected or names[0]

    return reverse_map


def build_format_patterns(constants):
    """Build regex patterns for matching $"..." interpolations against CStr format strings."""
    patterns = []
    for name, value in constants.items():
        placeholders = re.findall(r'\{(\d+)\}', value)
        if not placeholders:
            continue
        escaped = escape_for_display(value)
        parts = re.split(r'\{\d+\}', escaped)
        regex_parts = []
        for i, part in enumerate(parts):
            regex_parts.append(re.escape(part))
            if i < len(parts) - 1:
                regex_parts.append(r'(\{[^}]+\})')
        try:
            compiled = re.compile('^' + ''.join(regex_parts) + '$')
            patterns.append((name, value, compiled, len(placeholders)))
        except re.error:
            pass
    return patterns


def scan_source_file(filepath):
    """Extract all string literals from a C# source file."""
    content = filepath.read_text(encoding='utf-8')
    strings = []

    for line_num, line in enumerate(content.split('\n'), 1):
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('/*'):
            continue
        if 'public const string' in line or 'public static readonly string[]' in line:
            continue
        if 'CStr.' in line:
            continue

        # $"..." interpolations
        for m in re.finditer(r'\$"((?:[^"\\]|\\.)*)"', line):
            strings.append({'line': line_num, 'col': m.start(), 'type': 'interpolation',
                            'raw': m.group(0), 'content': m.group(1), 'context': stripped})

        # "..." regular strings (not preceded by $ or @)
        for m in re.finditer(r'(?<!\$)(?<!@)"((?:[^"\\]|\\.)*)"', line):
            if any(s['line'] == line_num and s['col'] <= m.start() < s['col'] + len(s['raw'])
                   for s in strings):
                continue
            strings.append({'line': line_num, 'col': m.start(), 'type': 'regular',
                            'raw': m.group(0), 'content': m.group(1), 'context': stripped})

        # @"..." verbatim strings
        for m in re.finditer(r'@"((?:[^"]|"")*)"', line):
            strings.append({'line': line_num, 'col': m.start(), 'type': 'verbatim',
                            'raw': m.group(0), 'content': m.group(1).replace('""', '"'),
                            'context': stripped})

    return strings, content


def match_strings(strings, reverse_map, format_patterns, constants):
    """Classify each found string as EXACT, FORMAT, MISSING, or SKIP."""
    results = []
    for sf in strings:
        content, stype = sf['content'], sf['type']
        unescaped = unescape_csharp(content) if stype != 'interpolation' else None

        if unescaped is not None and (unescaped in SKIP_STRINGS or len(unescaped) < MIN_STRING_LENGTH):
            results.append({**sf, 'match': 'SKIP'}); continue

        if stype == 'interpolation':
            if '{' not in content:
                unescaped = unescape_csharp(content)
                if unescaped in SKIP_STRINGS or len(unescaped) < MIN_STRING_LENGTH:
                    results.append({**sf, 'match': 'SKIP'}); continue
                if unescaped in reverse_map:
                    results.append({**sf, 'match': 'EXACT', 'cstr_name': reverse_map[unescaped],
                                    'replacement': f'CStr.{reverse_map[unescaped]}'}); continue

            matched = False
            for name, _, pattern, _ in format_patterns:
                m = pattern.match(content)
                if m:
                    vars_clean = [v.strip('{}') for v in m.groups()]
                    args = ', '.join(vars_clean)
                    results.append({**sf, 'match': 'FORMAT', 'cstr_name': name,
                                    'replacement': f'string.Format(CStr.{name}, {args})'}); matched = True; break
            if not matched:
                text_only = re.sub(r'\{[^}]+\}', '', content)
                if text_only.strip() and len(text_only.strip()) >= MIN_STRING_LENGTH:
                    results.append({**sf, 'match': 'MISSING'})
                else:
                    results.append({**sf, 'match': 'SKIP'})
            continue

        if unescaped in reverse_map:
            results.append({**sf, 'match': 'EXACT', 'cstr_name': reverse_map[unescaped],
                            'replacement': f'CStr.{reverse_map[unescaped]}'}); continue

        if len(unescaped) >= MIN_STRING_LENGTH:
            results.append({**sf, 'match': 'MISSING'})
        else:
            results.append({**sf, 'match': 'SKIP'})

    return results


def print_report(results, filename):
    exact = [r for r in results if r['match'] == 'EXACT']
    fmt = [r for r in results if r['match'] == 'FORMAT']
    missing = [r for r in results if r['match'] == 'MISSING']
    skip = [r for r in results if r['match'] == 'SKIP']

    print(f'\n{"="*70}')
    print(f'CStr Replacement Analysis: {filename}')
    print(f'{"="*70}')
    print(f'  EXACT matches:  {len(exact):4d}')
    print(f'  FORMAT matches: {len(fmt):4d}')
    print(f'  MISSING:        {len(missing):4d}')
    print(f'  SKIP:           {len(skip):4d}')

    if exact:
        print(f'\n--- EXACT ({len(exact)}) ---')
        for r in exact:
            print(f'  L{r["line"]:4d}: "{escape_for_display(r["content"][:50])}" -> {r["replacement"]}')
    if fmt:
        print(f'\n--- FORMAT ({len(fmt)}) ---')
        for r in fmt:
            print(f'  L{r["line"]:4d}: $"{escape_for_display(r["content"][:50])}" -> {r["replacement"][:80]}')
    if missing:
        print(f'\n--- MISSING ({len(missing)}) ---')
        for r in missing:
            print(f'  L{r["line"]:4d}: "{escape_for_display(r["content"][:60])}"')
    print(f'{"="*70}')


def apply_replacements(filepath, results, content):
    lines = content.split('\n')
    replaceable = sorted(
        [r for r in results if r['match'] in ('EXACT', 'FORMAT')],
        key=lambda r: (r['line'], r['col']), reverse=True
    )
    applied = 0
    for r in replaceable:
        line = lines[r['line'] - 1]
        pos = line.find(r['raw'], r['col'])
        if pos >= 0:
            lines[r['line'] - 1] = line[:pos] + r['replacement'] + line[pos + len(r['raw']):]
            applied += 1
    filepath.write_text('\n'.join(lines), encoding='utf-8')
    print(f'\nApplied {applied} replacements to {filepath.name}')
    return applied


def main():
    parser = argparse.ArgumentParser(description='CStr Replacer')
    parser.add_argument('mode', choices=['--analyze', '--apply'])
    parser.add_argument('source', help='Source .cs file (name or full path)')
    args = parser.parse_args()

    source = Path(args.source)
    if not source.exists():
        source = SRC_DIR / args.source
    if not source.exists():
        print(f'Error: {args.source} not found'); sys.exit(1)

    prefix = FILE_TO_PREFIX.get(source.name)
    constants, regions = parse_cstr()
    reverse_map = build_reverse_map(constants, prefix)
    format_patterns = build_format_patterns(constants)
    strings, content = scan_source_file(source)
    results = match_strings(strings, reverse_map, format_patterns, constants)
    print_report(results, source.name)

    if args.mode == '--apply':
        apply_replacements(source, results, content)
        print('Run: dotnet build MudGM/MudGM.csproj to verify.')


if __name__ == '__main__':
    main()
