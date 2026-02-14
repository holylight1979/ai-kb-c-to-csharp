# Encoding Scan Verification

> 來源: 專案編碼規範, Big5→UTF-8 轉換經驗
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: compare-strings, decode-big5
> 觸發條件: 修改任何包含中文字串的檔案後

## 知識
原始 C 原始碼使用 Big5 編碼（cp950），C# 使用 UTF-8。
轉換過程中常見兩類問題：

1. **PUA 字元（U+E000-F8FF）**: Big5 某些字元被錯誤映射到 Unicode 私用區
2. **替換字元（U+FFFD）**: 解碼失敗時產生的替代符號

任何一個 PUA 或 U+FFFD 都代表編碼轉換失敗，必須修正。

常見出問題的字元：
- `\xF9\xD8`（裏）→ 必須用 cp950 而非 big5 解碼
- `\xF9xx` 範圍的所有字元都只有 cp950 能正確處理
- 全形標點符號偶爾也會出錯

CStr 字串集中化後，中文字串集中在 `CStr.cs`。
掃描重點應放在該檔案以及任何新移植的檔案。

零容忍政策：掃描結果必須為 0 個問題。

## 行動
```bash
cd {CSHARP_DIR}
python -X utf8 verify.py encoding-scan --path {CSHARP_DIR}/MudGM/Src
```
每次修改中文字串後都必須執行。

## 驗證
輸出應顯示：
```
Encoding scan: 0 PUA characters, 0 replacement characters
```
任何非零結果都需要修正。

## 失敗時
→ decode-big5 (重新從 C 原始碼解碼正確字串)
→ compare-strings (比對原始字串)
