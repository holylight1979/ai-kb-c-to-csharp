# CStr 工具集

用於 MUD GM 專案 C→C# 移植過程中的字串集中化管理工具。

## 概述

所有中文字串集中在 `MUD-Arion-CSharp/MudGM/Src/CStr.cs` 中，以 `CStr.REGION_NNN` 常數管理。
這些工具負責：提取原始 Big5 字串、新增缺少的常數、替換硬編碼字串。

## 工具列表

### 1. `big5_extract.py` — Big5 原始碼字串提取

從原始 C 原始碼（Big5/CP950 編碼）提取中文字串。

```bash
# 提取所有中文字串
python -X utf8 .claude/tools/big5_extract.py SRC/ACT_OBJ.C

# 查看特定行號
python -X utf8 .claude/tools/big5_extract.py SRC/ACT_OBJ.C --line 400

# 與 CStr.cs 交叉比對
python -X utf8 .claude/tools/big5_extract.py SRC/ACT_OBJ.C --verify
```

**重要**：使用 `cp950` 而非 `big5` 編解碼器，因為 `\xF9xx` 範圍（如「裏」U+88CF）只有 cp950 能正確解碼。

### 2. `cstr_add_missing.py` — 新增缺少的 CStr 常數

掃描所有 C# 原始檔，找出尚未存在於 CStr.cs 的字串並自動新增。

```bash
# 預覽（不修改檔案）
python -X utf8 .claude/tools/cstr_add_missing.py --dry-run

# 實際新增
python -X utf8 .claude/tools/cstr_add_missing.py
```

新增的常數會自動插入到對應的 `#region` 區段，命名為 `REGION_NNN`（流水號遞增）。

### 3. `cstr_replacer.py` — 替換硬編碼字串為 CStr 引用

掃描 C# 原始檔中的硬編碼字串，替換為 `CStr.XXX` 引用。

```bash
# 分析模式（預覽）
python -X utf8 .claude/tools/cstr_replacer.py --analyze ACT_OBJ.C.cs

# 套用替換
python -X utf8 .claude/tools/cstr_replacer.py --apply ACT_OBJ.C.cs
```

替換類型：
| 類型 | 原始碼 | 替換結果 |
|------|--------|----------|
| EXACT | `"某某文字"` | `CStr.REGION_NNN` |
| FORMAT | `$"文字{var}"` | `string.Format(CStr.REGION_NNN, var)` |
| MISSING | 找不到對應常數 | 需先用 `cstr_add_missing.py` 新增 |
| SKIP | 太短或太通用 | 不處理 |

## 標準工作流程

新移植一個 C 檔案後的字串集中化流程：

```
1. big5_extract.py  ACT_XXX.C --verify     # 確認原始字串，檢查亂碼
2. cstr_add_missing.py                      # 新增缺少的常數到 CStr.cs
3. cstr_replacer.py --analyze ACT_XXX.C.cs  # 預覽替換
4. cstr_replacer.py --apply   ACT_XXX.C.cs  # 套用替換
5. dotnet build MudGM/MudGM.csproj          # 編譯驗證
6. (若有 MISSING) 重複步驟 2-5
```

## 新增檔案支援

若移植新的 C 檔案，需在兩個腳本的 `FILE_TO_PREFIX` 字典中新增映射：

```python
FILE_TO_PREFIX = {
    ...
    'NEW_FILE.C.cs': 'NEWREGION',  # 新增這行
}
```

並在 CStr.cs 中建立對應的 `#region NEWREGION` / `#endregion` 區段。

## 已知限制

1. **複雜三元運算式**：`$"text {(cond ? "a" : "b")}"` 內的巢狀字串可能無法正確匹配
2. **陣列初始化**：`new[] { "a", "b" }` 中的字串需手動處理
3. **char 字面值**：`'的'` 等 char 常數不在掃描範圍內
4. **跨行字串**：目前僅處理單行字串
