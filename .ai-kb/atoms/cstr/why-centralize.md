# 為何集中化字串

> 來源: 專案架構決策，CStr.cs
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: atoms/cstr/naming-rules.md, atoms/cstr/region-structure.md
> 觸發條件: 新增或修改中文字串時；質疑為何不直接寫字串

## 知識
本專案所有固定中文字串集中在 `CStr.cs`，不允許在業務邏輯中硬編碼。

### 為何這樣做
1. **統一維護**：所有中文字串在一個檔案中，修改不需搜尋全專案
2. **避免重複**：相同字串只定義一次，多處引用同一常數
3. **國際化準備**：未來若需多語系，只需替換 CStr.cs
4. **可讀性**：程式碼中 `CStr.COMM_015` 比一長串中文更簡潔
5. **編碼安全**：中文字串集中管理，減少編碼轉換出錯機會

### 目前規模
- 4,198 個 CStr 引用
- 橫跨 15 個 .cs 原始檔
- 0 個殘留硬編碼中文字串

### 使用方式
```csharp
// 錯誤：硬編碼中文
SendToChar("你沒有足夠的金幣。\n", ch);

// 正確：使用 CStr 常數
SendToChar(CStr.ACT_042, ch);

// 含格式化的情況
SendToChar(string.Format(CStr.ACT_043, goldNeeded), ch);
```

### 例外情況（不需集中化）
- 空字串 `""`
- 純格式字串 `"\n"`, `"\r"`
- 單一字元
- 見 atoms/cstr/skip-list.md

## 行動
- 新增中文字串時，先加到 CStr.cs 對應 region
- 業務邏輯中只引用 CStr 常數
- 定期用工具掃描是否有漏網的硬編碼中文

## 驗證
- `grep -rn` 搜尋 .cs 檔案中的中文字元
- 除了 CStr.cs 本身外，不應有中文字串定義

## 失敗時
→ atoms/cstr/naming-rules.md（確認命名規則後新增常數）
