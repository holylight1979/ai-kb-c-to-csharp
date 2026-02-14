# CStr 跳過清單

> 來源: cstr_add_missing.py, cstr_replacer.py 設定
> 信心度: VERIFIED
> 前置知識: atoms/cstr/why-centralize.md
> 相關原子: atoms/cstr/naming-rules.md
> 觸發條件: 判斷某字串是否需要提取到 CStr

## 知識
並非所有字串都需要集中化。以下字串類型應保留在原處。

### 跳過規則
| 類別 | 範例 | 原因 |
|------|------|------|
| 空字串 | `""` | 無意義 |
| 純空白 | `" "`, `"  "` | 格式用途 |
| 單一字元 | `"a"`, `"."` | 太短 |
| 換行符 | `"\n"`, `"\r"`, `"\r\n"` | 格式控制 |
| Tab | `"\t"` | 格式控制 |
| 單一數字 | `"0"` ~ `"9"` | 太短 |
| 泛用標記 | `"#"`, `"$"`, `"~"`, `"*"` | 格式標記 |
| 布林字串 | `"true"`, `"false"`, `"null"` | 語言常數 |

### 最小長度
```python
MIN_STRING_LENGTH = 2  # 長度 < 2 的字串一律跳過
```

### 特殊判斷
```csharp
// 這些不提取：
"\n"                // 換行
"  "                // 空白對齊
"#"                 // 區域檔案標記

// 這些要提取：
"你好\n"            // 含中文 → 提取（\n 保留在常數值中）
"等級：{0}\n"       // 含中文模板 → 提取
"OK\n"              // 純英文但有意義 → 視情況決定
```

### 工具行為
`cstr_add_missing.py` 和 `cstr_replacer.py` 內建跳過邏輯：
```python
def should_skip(s):
    s = s.strip()
    if len(s) < MIN_STRING_LENGTH:
        return True
    if s in SKIP_SET:  # 預定義跳過集合
        return True
    if all(c in ' \t\n\r' for c in s):
        return True
    return False
```

### 邊界案例
- `"OK"` → 英文短字串，通常保留原處
- `"HP"` → 遊戲術語，保留原處
- `"你"` → 單一中文字但長度 = 1 UTF-16 char → 跳過
- `"經驗"` → 兩個中文字，有意義 → 提取

## 行動
- 遇到疑似需要提取的字串，先檢查跳過清單
- 不確定時偏向「提取」（寧多勿少）
- 工具會自動處理大部分判斷

## 驗證
- 執行 `cstr_add_missing.py` 確認無新增
- 手動檢查是否有遺漏的有意義字串

## 失敗時
→ atoms/cstr/why-centralize.md（重新理解集中化目的）
