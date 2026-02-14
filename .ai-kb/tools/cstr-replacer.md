# cstr_replacer.py 操作手冊

> 位置: {PROJECT_ROOT}\.claude\tools\cstr_replacer.py
> 用途: 替換 C# 原始檔中的硬編碼字串為 CStr.XXX 引用

## 基本用法

```bash
python -X utf8 .claude/tools/cstr_replacer.py --analyze XXX.C.cs  # 預覽分析
python -X utf8 .claude/tools/cstr_replacer.py --apply XXX.C.cs    # 套用替換
```

## 參數說明

| 參數 | 必要 | 說明 |
|------|------|------|
| `mode` | 是 | `--analyze`（預覽）或 `--apply`（套用） |
| `source` | 是 | 目標 .cs 檔案名稱或完整路徑 |

## 匹配類型

| 類型 | 原始碼 | 替換結果 | 說明 |
|------|--------|----------|------|
| EXACT | `"某某文字"` | `CStr.PREFIX_NNN` | 字串值完全匹配 |
| FORMAT | `$"文字{var}"` | `string.Format(CStr.PREFIX_NNN, var)` | 插值轉 format |
| MISSING | 找不到對應常數 | 不替換 | 需先用 cstr_add_missing |
| SKIP | 太短或太通用 | 不替換 | 如空白、單字元等 |

## 運作流程

1. 解析 CStr.cs 建立反向映射（字串值 → 常數名稱）
2. 根據 `FILE_TO_PREFIX` 決定該檔案的偏好前綴
3. 掃描目標檔案中所有字串字面值
4. 分類為 EXACT / FORMAT / MISSING / SKIP
5. `--apply` 模式下，從檔案末尾往前替換（避免位移問題）

## 反向映射優先級

當同一字串值有多個常數名稱時，選擇順序:
1. 與目標檔案同前綴的常數（如 `ACTOBJ_xxx`）
2. 通用前綴 `M_USE_xxx`
3. 第一個找到的常數

## 重要注意事項

- **必須先執行** `cstr_add_missing.py` 確保所有常數已存在
- 替換是**位置感知**的：從檔案末尾往前替換，避免行內位移
- `FILE_TO_PREFIX` 字典必須有目標檔案的映射
- 自動跳過: `CStr.` 已引用行、`const` 定義行、註解行

## 輸出範例（--analyze）

```
======================================================================
CStr Replacement Analysis: ACT_OBJ.C.cs
======================================================================
  EXACT matches:   142
  FORMAT matches:    18
  MISSING:            0
  SKIP:              34

--- EXACT (142) ---
  L  42: "你丟下了" -> CStr.ACTOBJ_001
  L  55: "你沒有那個東西。" -> CStr.ACTOBJ_002
======================================================================
```

## 已知限制

| 限制 | 說明 |
|------|------|
| 複雜三元運算式 | `$"text {(cond ? "a" : "b")}"` 巢狀字串可能無法正確匹配 |
| 陣列初始化 | `new[] { "a", "b" }` 中的字串需手動處理 |
| char 字面值 | `'的'` 等 char 常數不在掃描範圍 |
| 跨行字串 | 只處理單行字串，多行 verbatim 不支援 |
| 字串拼接 | `"abc" + "def"` 兩段分別匹配，非整體 |

## 完整工作流程

```
1. cstr_add_missing.py --dry-run        # 確認有多少缺少
2. cstr_add_missing.py                  # 新增到 CStr.cs
3. cstr_replacer.py --analyze XXX.C.cs  # 預覽，確認 MISSING=0
4. cstr_replacer.py --apply XXX.C.cs    # 套用替換
5. dotnet build {CSPROJ_PATH}            # 編譯驗證
```
