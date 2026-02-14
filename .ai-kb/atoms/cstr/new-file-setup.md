# 新檔案 CStr 設定

> 來源: CLAUDE.md 工具流程，cstr_add_missing.py, cstr_replacer.py
> 信心度: VERIFIED
> 前置知識: atoms/cstr/why-centralize.md, atoms/cstr/naming-rules.md, atoms/cstr/region-structure.md
> 相關原子: atoms/encoding/cp950-vs-big5.md
> 觸發條件: 開始移植一個新的 C 原始檔到 C#

## 知識
移植新 C 檔案時，必須先設定 CStr 工具鏈才能處理中文字串。

### 步驟一：新增 FILE_TO_PREFIX 映射
在 **兩個** Python 工具中新增映射：

```python
# .claude/tools/cstr_add_missing.py
FILE_TO_PREFIX = {
    "COMM.C.cs": "COMM",
    "DB.C.cs": "DB",
    # ... 現有映射 ...
    "NEWFILE.C.cs": "NEWPFX",  # ← 新增
}

# .claude/tools/cstr_replacer.py
FILE_TO_PREFIX = {
    # ... 同上，保持兩邊一致 ...
    "NEWFILE.C.cs": "NEWPFX",  # ← 新增
}
```

### 步驟二：新增 CStr.cs region
```csharp
// CStr.cs 中，按字母順序插入
    #region NEWFILE
    #endregion
```

### 步驟三：執行標準工具流程
```bash
# 1. 從原始 C 檔案提取中文字串（Big5 → UTF-8）
python -X utf8 .claude/tools/big5_extract.py SRC/NEWFILE.C --verify

# 2. 移植 C# 檔案後，掃描並新增缺少的 CStr 常數
python -X utf8 .claude/tools/cstr_add_missing.py

# 3. 替換硬編碼中文字串為 CStr 引用
python -X utf8 .claude/tools/cstr_replacer.py --apply NEWFILE.C.cs

# 4. 編譯驗證
dotnet build {CSPROJ_PATH}
```

### PREFIX 命名慣例
| C 檔案         | 建議 PREFIX |
|---------------|------------|
| ACT_XXX.C     | AXXX       |
| SPECIAL.C     | SPEC       |
| SKILLS.C      | SKILL      |
| SAVE.C        | SAVE       |
| NOTE.C        | NOTE       |
| BAN.C         | BAN        |

PREFIX 規則：
- 全大寫
- 3-5 個字母
- 簡短但可辨識
- 不與現有 PREFIX 衝突

### 常見錯誤
1. 只改了一個工具的 FILE_TO_PREFIX → 另一個工具不認得新檔案
2. 忘記建 region → cstr_add_missing.py 不知道常數放哪裡
3. 忘記 `-X utf8` → Windows 上 Python 輸出亂碼

## 行動
- 移植新檔案前，先完成上述三步設定
- 設定完成後再開始移植程式碼
- 每次 `dotnet build` 確認無編譯錯誤

## 驗證
- `cstr_add_missing.py` 執行無錯誤
- `cstr_replacer.py` 能正確辨識新檔案
- `dotnet build` 編譯通過
- 新檔案中無硬編碼中文字串

## 失敗時
→ atoms/cstr/region-structure.md（確認 region 格式）
→ atoms/cstr/naming-rules.md（確認 PREFIX 命名）
