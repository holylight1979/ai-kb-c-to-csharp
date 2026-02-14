# One-Liner Delegation Pattern

> 來源: COMM.C.cs, 移植架構設計
> 信心度: VERIFIED
> 前置知識: partial-class
> 相關原子: partial-class, stub-empty, grep-existing
> 觸發條件: 函式邏輯屬於另一個已移植模組時

## 知識
當某個函式在 C 中定義於 A 檔案，但邏輯上屬於 B 模組，
且 B 模組已經移植完成時，使用 one-liner delegation：

```csharp
// 在 COMM.C.cs 中，boot_db 實際由 DbModule 負責
public static void BootDb()
    => DbModule.BootDb();

// 在 FIGHT.C.cs 中，save_char_obj 實際由 SaveModule 負責
public static void SaveCharObj(CharData ch)
    => SaveModule.SaveCharObj(ch);
```

使用條件（三者都必須滿足）：
1. 目標方法已在另一個模組中實作完成
2. 方法簽名（參數類型與數量）完全匹配
3. 回傳型別一致

常見錯誤：
- 目標方法不存在（只有 stub）→ 變成間接空殼
- 參數順序或型別不同 → 編譯錯誤
- 忽略回傳值 → 邏輯錯誤

## 行動
1. 確認目標模組和方法已移植且非 stub
2. 確認方法簽名完全匹配
3. 撰寫 `=>` 單行委派
4. 編譯確認無錯誤

## 驗證
```bash
# 確認目標方法存在且有實作
Grep "public static .* TargetMethod" --path {CSHARP_DIR}/MudGM/Src/
# 編譯確認
dotnet build {CSPROJ_PATH}
```

## 失敗時
→ grep-existing (搜尋目標方法是否存在)
→ stub-scan (確認目標非空殼)
→ build-check (編譯驗證)
