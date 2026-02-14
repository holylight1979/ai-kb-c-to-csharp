# Function Classifier — 函數特徵分析器

> 呼叫時機: PORT_FUNCTIONS 狀態中，對每個 C 函數執行一次
> 輸入: 一個 C 函數的原始碼文字
> 輸出: 特徵標籤集合 + 需載入的原子清單

## 演算法

```
FUNCTION classify(c_source: string) → (tags: Set, atoms: List)

  tags = {}
  atoms = []

  # ── 特徵掃描（逐條檢測） ──

  IF contains_cjk(c_source)
    tags.add("HAS_CHINESE")
    atoms.append("atoms/encoding/big5-what-is.md")

  IF regex_match(c_source, r'(sprintf|printf|fprintf|send_to_char.*%)')
    tags.add("HAS_PRINTF")
    atoms.append("atoms/syntax/printf-format.md")

  IF regex_match(c_source, r'\bswitch\s*\(')
    tags.add("HAS_SWITCH")
    atoms.append("atoms/syntax/switch-fallthrough.md")

  IF regex_match(c_source, r'(do_\w+|spell_\w+|spec_\w+)\s*\(')
    tags.add("HAS_CROSS_CALL")
    atoms.append("atoms/patterns/delegation-oneliner.md")

  IF regex_match(c_source, r'->(next|prev)\b|for\s*\(.*!=\s*NULL')
    tags.add("HAS_LINKED_LIST")
    atoms.append("atoms/syntax/global-linked-list.md")

  IF regex_match(c_source, r'fread_string|fread_number|fread_word')
    tags.add("HAS_FREAD_STR")
    atoms.append("atoms/syntax/fread-string.md")

  IF regex_match(c_source, r'(free\s*\(|extract_char|obj_from_char)')
    tags.add("HAS_CLEANUP")
    atoms.append("atoms/traps/G-cleanup-truncated.md")

  line_count = count_lines(c_source)
  IF line_count > 100
    tags.add("LINE_COUNT>100")
    atoms.append("atoms/traps/H-logic-omitted.md")

  IF regex_match(c_source, r'%-?\d+[ds]|%\d+\.\d+')
    tags.add("HAS_FORMAT_WIDTH")
    atoms.append("atoms/syntax/format-width-fatal.md")

  IF regex_match(c_source, r"\[0\]\s*==\s*'\\0'|\[0\]\s*==\s*0|== '\\0'")
    tags.add("HAS_NULL_CHECK")
    atoms.append("atoms/syntax/null-terminator.md")

  # ── 額外模式（補充偵測） ──

  IF regex_match(c_source, r'#define|IS_SET|REMOVE_BIT')
    atoms.append("atoms/syntax/macro-to-method.md")

  IF regex_match(c_source, r'\bmalloc\b|\bcalloc\b|\bfree\b')
    atoms.append("atoms/syntax/malloc-free.md")

  IF regex_match(c_source, r'(str_cmp|str_prefix|str_infix)')
    atoms.append("atoms/syntax/string-ops.md")

  # ── 去重 ──
  atoms = deduplicate(atoms)

  RETURN (tags, atoms)

END FUNCTION
```

## 標籤 → 風險等級映射

```
FUNCTION risk_from_tags(tags, line_count) → RISK_LEVEL

  IF "HAS_FREAD_STR" IN tags OR line_count > 150
    RETURN CRITICAL

  IF "LINE_COUNT>100" IN tags
     OR "HAS_PRINTF" IN tags AND "HAS_SWITCH" IN tags
     OR "HAS_FORMAT_WIDTH" IN tags
    RETURN HIGH

  IF line_count > 30 AND len(tags) >= 2
    RETURN MEDIUM

  RETURN LOW

END FUNCTION
```

## 使用方式

```
FOR EACH function IN c_file:
  (tags, atoms) = classify(function.source)
  risk = risk_from_tags(tags, function.line_count)
  # → 將函數分入 LOW/MEDIUM/HIGH/CRITICAL 群組
  # → 載入 atoms 作為移植參考
```

## 連結原子

- atoms/encoding/big5-what-is.md — HAS_CHINESE 觸發
- atoms/syntax/printf-format.md — HAS_PRINTF 觸發
- atoms/syntax/switch-fallthrough.md — HAS_SWITCH 觸發
- atoms/syntax/format-width-fatal.md — HAS_FORMAT_WIDTH 觸發
- atoms/syntax/null-terminator.md — HAS_NULL_CHECK 觸發
- atoms/syntax/global-linked-list.md — HAS_LINKED_LIST 觸發
- atoms/syntax/fread-string.md — HAS_FREAD_STR 觸發
- atoms/traps/G-cleanup-truncated.md — HAS_CLEANUP 觸發
- atoms/traps/H-logic-omitted.md — LINE_COUNT>100 觸發
- atoms/patterns/delegation-oneliner.md — HAS_CROSS_CALL 觸發
