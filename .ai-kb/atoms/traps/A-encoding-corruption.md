# Encoding Corruption (Big5 bytes written to UTF-8)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-A
> 信心度: VERIFIED
> 前置知識: Big5/CP950 編碼基礎
> 相關原子: encoding/big5-basics, encoding/cp950-decode
> 觸發條件: 檔案中出現半個中文字元、?、U+FFFD (�) 替代字元

## 知識

Big5 編碼的中文字元由兩個位元組組成。當這些位元組被當作 UTF-8 寫入時，
會產生亂碼。有兩種主要的損壞路徑：

**路徑一：標準損壞 — Big5 直接當 UTF-8 寫入**
```
原始 Big5: 0xA4 0x40 (一)
錯誤 UTF-8 解讀: 可能變成 ? 或 U+FFFD
```

**路徑二：0x5C 逃脫損壞**
Big5 第二位元組可能是 0x5C（即 ASCII 反斜線 `\`）。
C 編譯器或字串處理會將其視為逃脫字元：
```c
// Big5 "功" = 0xA5\x5C，第二位元組是反斜線
char *s = "功能";  // 0x5C 可能被解析為 escape
```

常見症狀：
- 字串只出現半個中文字（單一位元組殘留）
- 出現問號 `?` 取代原本中文
- 出現 U+FFFD 替代字元 `�`
- 字串長度與預期不符

Python 必須使用 `cp950` 而非 `big5` 解碼：
```python
# 正確
raw.decode('cp950')
# 錯誤 — 無法處理 \xF9xx 範圍
raw.decode('big5')
```

## 行動

1. 用 `cp950` 解碼原始 C 原始碼，取得正確中文文字
2. 在 C# 原始碼中搜尋損壞的字串片段
3. 替換為正確的 UTF-8 中文文字
4. 若為 CStr 常數，確認 CStr.cs 中的值也正確

```bash
python -X utf8 .claude/tools/big5_extract.py SOURCE.C --verify
```

## 驗證

執行 encoding-scan 確認無損壞殘留：
- 搜尋 U+FFFD 字元
- 搜尋孤立的高位元組（>0x7F 的單一位元組）
- 確認所有中文字串長度為偶數位元組

## 失敗時

→ encoding/cp950-decode, encoding/big5-basics
