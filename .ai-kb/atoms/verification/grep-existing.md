# Grep Existing Implementation

> 來源: 重複實作陷阱（Trap J）防範
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: build-check, partial-class, delegation-oneliner
> 觸發條件: 建立任何新函式或方法之前

## 知識
**在建立新函式之前，必須先搜尋是否已有實作。**

重複實作（Trap J）的後果：
- 兩個版本行為不一致 → 難以除錯
- partial class 中可能導致 CS0101 編譯錯誤
- 不同模組各自維護一份 → 修改時容易遺漏

搜尋策略——必須搜尋兩種命名風格：

```bash
# C 風格（snake_case）
Grep "stop_fighting" --path {CSHARP_DIR}/MudGM/Src/ --glob "*.cs"

# C# 風格（PascalCase）
Grep "StopFighting" --path {CSHARP_DIR}/MudGM/Src/ --glob "*.cs"
```

搜尋範圍應涵蓋：
1. 所有 `.cs` 檔案（包含 partial class 的所有部分）
2. 介面定義檔
3. 基底類別

常見重複來源：
- CommModule 和 DbModule 都實作了同一個工具函式
- MERC.cs / MercTypes.cs / MercStubs.cs 三者有重疊
- Helper 類別中可能已有通用版本

找到既有實作後的處理：
1. 若已完整 → 使用 delegation-oneliner 委派
2. 若是 stub → 直接在原處實作，不要另建
3. 若簽名不同 → 評估是否需要重構

## 行動
```bash
# 範例：要建立 StopFighting 之前
cd {CSHARP_DIR}
```

使用 Grep 工具搜尋：
```
pattern: "StopFighting|stop_fighting"
path: "{CSHARP_DIR}/MudGM/Src"
glob: "*.cs"
output_mode: "content"
```

若找到結果，閱讀既有實作再決定行動。

## 驗證
搜尋結果為空 → 安全建立新函式。
搜尋結果非空 → 閱讀並決定：修改既有 or 委派。

## 失敗時
→ build-check (若不小心建了重複，編譯會報 CS0101)
→ delegation-oneliner (若需要委派到既有實作)
→ partial-class (確認是否在同一 partial class 中)
