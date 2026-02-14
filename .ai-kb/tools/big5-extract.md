# big5_extract.py 操作手冊

> 位置: {PROJECT_ROOT}\.claude\tools\big5_extract.py
> 用途: 從原始 C 原始碼（Big5/CP950 編碼）提取中文字串

## 基本用法

```bash
python -X utf8 .claude/tools/big5_extract.py SRC/XXX.C           # 提取所有中文字串
python -X utf8 .claude/tools/big5_extract.py SRC/XXX.C --line 400 # 查看特定行
python -X utf8 .claude/tools/big5_extract.py SRC/XXX.C --verify   # 與 CStr.cs 交叉比對
```

## 參數說明

| 參數 | 必要 | 說明 |
|------|------|------|
| `source` | 是 | C 原始碼檔案路徑（如 `SRC/ACT_OBJ.C`） |
| `--line N` | 否 | 顯示第 N 行的解碼內容 |
| `--verify` | 否 | 與 CStr.cs 交叉比對，顯示 [OK] 或 [MISSING] |

## 關鍵細節

- 使用 `cp950` 編碼（非 `big5`），因為 `\xF9xx` 範圍只有 cp950 能正確解碼
- `--verify` 模式會載入 CStr.cs 所有常數值，逐一比對提取的字串
- 輸出格式: `L{行號}: "字串內容"`
- 只提取包含 CJK 字元的字串（Unicode 範圍 `\u4e00-\u9fff` 等）
- 字串提取使用 C 字串正則式: `"((?:[^"\\]|\\.)*)"` 匹配雙引號內容

## 輸出範例

```
Read 2847 lines from ACT_OBJ.C (cp950)
Found 156 Chinese string literals

L  42: "你在這裏看到了什麼？"
L 105: "%s把%s丟在地上。\n\r"
```

## 常見問題

| 症狀 | 原因 | 解法 |
|------|------|------|
| 出現 U+FFFD (�) | 原始檔損壞或非 cp950 | 手動 hex 檢查原始位元組 |
| 終端亂碼 | 缺少 `-X utf8` 旗標 | 加上 `python -X utf8` |
| 字串數量為 0 | 路徑錯誤或檔案為 UTF-8 | 確認檔案確實是 Big5 編碼 |

## 工作流程中的位置

```
STATE: INIT → 用此工具確認原始字串，檢查是否有 FFFD 亂碼
STATE: CSTR → 用 --verify 確認 CStr.cs 覆蓋率
STATE: VERIFY → 最終驗收時再次 --verify 確認 100% 覆蓋
```

## 內部路徑解析

腳本自動解析專案結構:
- `SCRIPT_DIR`: `.claude/tools/`
- `PROJECT_ROOT`: `{PROJECT_ROOT}`
- `SRC_DIR`: `{PROJECT_ROOT}\SRC\`
- `CSTR_FILE`: `{CSHARP_DIR}\MudGM\Src\CStr.cs`

若 source 參數非絕對路徑，會自動嘗試 `SRC_DIR / source`。
