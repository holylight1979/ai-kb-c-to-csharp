# cstr_add_missing.py 操作手冊

> 位置: {PROJECT_ROOT}\.claude\tools\cstr_add_missing.py
> 用途: 掃描 C# 原始檔，自動新增缺少的 CStr 常數到 CStr.cs

## 基本用法

```bash
python -X utf8 .claude/tools/cstr_add_missing.py --dry-run  # 預覽（不修改）
python -X utf8 .claude/tools/cstr_add_missing.py             # 實際新增
```

## 參數說明

| 參數 | 必要 | 說明 |
|------|------|------|
| `--dry-run` | 否 | 預覽模式，僅顯示將新增的常數，不修改 CStr.cs |

## 運作流程

1. 解析 CStr.cs，收集所有已存在的常數值（含 unescape）
2. 遍歷 `FILE_TO_PREFIX` 字典中的每個 .cs 檔案
3. 在每個檔案中搜尋未被 CStr 引用的字串字面值
4. 跨檔案去重（同一字串只新增一次）
5. 在 CStr.cs 對應 `#region` 的 `#endregion` 前方插入新常數

## 關鍵細節

- 掃描對象: `FILE_TO_PREFIX` 字典中所有映射的 .cs 檔案
- 自動跳過: `CStr.` 引用行、`const` 定義行、註解行（`//`, `/*`）
- 新增位置: 對應 `#region` 區段的 `#endregion` 前方
- 命名規則: `PREFIX_NNN`（三位數流水號，從該 prefix 最大編號 +1 遞增）
- 批次標記: `// --- Added by cstr_add_missing ---`

## 字串類型處理

| 類型 | 語法 | 處理方式 |
|------|------|----------|
| 一般字串 | `"某某文字"` | 直接提取值 |
| 插值字串 | `$"文字{var}"` | 轉為 format 模板 `文字{0}` |
| 逐字字串 | `@"某某"` | 處理 `""` → `"` 跳脫 |

## SKIP_STRINGS（不提取的字串）

```
'', ' ', '  ', '    ', '\n', '\r', '\n\r', '\r\n',
'\t', '0', '1', '#', '$', '~', '.', ',', ':', ';',
'S', 'M', 'O', 'P', 'G', 'E', 'D', 'R', 'B', '*',
'true', 'false', 'null', 'none'
```

最小字串長度: `MIN_STRING_LENGTH = 2`

## 新檔案支援

移植新檔案前，必須先完成兩步:

1. 在 `FILE_TO_PREFIX` 字典新增映射:
   ```python
   FILE_TO_PREFIX = { ..., 'NEW_FILE.C.cs': 'NEWPREFIX' }
   ```
2. 在 CStr.cs 建立對應區段:
   ```csharp
   #region NEWPREFIX
   #endregion
   ```

## 輸出範例

```
Existing CStr values: 1847
  ACT_OBJ.C.cs: 12 new
  FIGHT.C.cs: 3 new

Total to add: 15
CStr.cs updated with 15 new constants.
```

## 常見問題

| 症狀 | 原因 | 解法 |
|------|------|------|
| `WARNING: region "X" not found` | CStr.cs 缺少該 region | 新增 `#region X` / `#endregion` |
| 新增數量為 0 | 所有字串已存在或被 SKIP | 正常，無需處理 |
| 重複常數值 | 跨檔案相同字串 | 工具自動去重，只新增一次 |
