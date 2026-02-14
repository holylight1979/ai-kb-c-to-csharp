# Chinese Translated to English (中文被翻譯為英文)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-D
> 信心度: VERIFIED
> 前置知識: Big5/CP950 編碼, CStr 字串集中化
> 相關原子: encoding/cp950-decode, cstr/string-centralization
> 觸發條件: C# 中出現英文字串，但 C 原始碼對應位置為中文

## 知識

AI 輔助移植時，模型可能將 Big5 編碼的中文字串「翻譯」為英文，
而非保留原始中文。這會改變遊戲的語言體驗。

**典型案例：代名詞陣列**

C 原始碼（Big5 編碼）：
```c
char *he_she[] = { "它", "他", "她" };
```

錯誤移植（翻譯為英文）：
```csharp
string[] HeShe = { "it", "he", "she" };
```

正確移植（保留中文）：
```csharp
string[] HeShe = { "它", "他", "她" };
// 或使用 CStr 常數
string[] HeShe = { CStr.TA_IT, CStr.TA_HE, CStr.TA_SHE };
```

**高風險區域：**
- 代名詞系統（他/她/它）
- 方向名稱（東/南/西/北）
- 狀態描述（站/坐/臥/睡）
- 戰鬥訊息（攻擊/閃避/格擋）
- 技能/法術名稱
- 物品描述字串

**根本原因：**
Big5 原始碼在未正確解碼前是亂碼，AI 模型會嘗試「理解」
語義並輸出英文翻譯，而非原封不動搬移中文字串。

## 行動

1. 用 `cp950` 解碼 C 原始碼確認原始語言
2. 搜尋 C# 中所有字串字面值
3. 比對 C 與 C# 的字串內容
4. 將英文翻譯替換回原始中文
5. 考慮將字串集中至 CStr.cs

```bash
python -X utf8 .claude/tools/big5_extract.py SOURCE.C --verify
```

## 驗證

執行 compare-strings 比對 C 與 C# 的字串：
- 確認所有遊戲內顯示文字為中文
- 確認代名詞陣列為中文
- 確認無 "it", "he", "she" 等翻譯殘留

## 失敗時

→ encoding/cp950-decode, cstr/string-centralization
