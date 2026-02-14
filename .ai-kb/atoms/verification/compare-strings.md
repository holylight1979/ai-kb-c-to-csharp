# Compare Strings Verification

> 來源: 字串完整性驗證流程
> 信心度: VERIFIED
> 前置知識: encoding-scan
> 相關原子: encoding-scan, decode-big5, build-check
> 觸發條件: 移植完成一個 C 檔案後、CStr 字串集中化後

## 知識
此工具從 C 原始碼（Big5）和 C# 原始碼（UTF-8）各自提取中文字串，
進行並排比對。

輸出三個區段：
1. **共同字串**: 兩邊都有 → 正常
2. **In C but not C#**: C 有但 C# 沒有 → 可能遺漏或損壞
3. **In C# but not C**: C# 有但 C 沒有 → 可能是新增或 CStr 合併

「In C but not C#」需要逐一檢查：
- 字串可能被 CStr 常數取代（正常）
- 字串可能在移植時遺漏（需補回）
- 字串可能因編碼錯誤而損壞（需重新解碼）

CStr 集中化後的注意事項：
- 中文字串已移至 CStr.cs，compare-strings 需包含 CStr.cs
- 或改用 Grep 搜尋 CStr.cs 確認字串存在

使用 cp950 而非 big5 解碼，確保 `\xF9xx` 範圍字元正確。

## 行動
```bash
cd {CSHARP_DIR}
python -X utf8 verify.py compare-strings SRC/ACT_WIZ.C {CSHARP_DIR}/MudGM/Src/ACT_WIZ.C.cs
```

配合 CStr.cs 檢查：
```bash
python -X utf8 verify.py compare-strings SRC/ACT_WIZ.C {CSHARP_DIR}/MudGM/Src/CStr.cs
```

## 驗證
「In C but not C#」區段應為空，或每個項目都有合理解釋。
任何無法解釋的缺失字串都必須調查。

## 失敗時
→ encoding-scan (檢查編碼問題)
→ decode-big5 (重新從原始碼提取正確字串)
