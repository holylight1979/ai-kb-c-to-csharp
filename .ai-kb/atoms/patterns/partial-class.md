# Partial Class Pattern

> 來源: 專案架構設計, COMM.C / DB.C 移植
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: visibility-upgrade, using-static-import
> 觸發條件: 同一模組需拆分至多個檔案時

## 知識
C# 的 `partial class` 允許同一個類別分散在多個檔案中。
本專案大量使用此模式，因為單一 C 檔案可能過大。

已知的 partial class 組合：
```
CommModule:
  ├── COMM.C.cs        (主要通訊邏輯)
  ├── CommHelpers.cs   (輔助函式)
  └── NetCore.cs       (網路核心)

DbModule:
  ├── DB.C.cs          (資料庫主邏輯)
  ├── DB.C.Extra.cs    (額外功能)
  └── DB.C.GM.cs       (GM 專用功能)
```

每個檔案的宣告必須完全一致：
```csharp
// 檔案 A: COMM.C.cs
namespace MudGM.Src
{
    public static partial class CommModule
    {
        // ...
    }
}

// 檔案 B: CommHelpers.cs — 必須同 namespace、同 class 名
namespace MudGM.Src
{
    public static partial class CommModule
    {
        // 可存取檔案 A 的 private 成員
    }
}
```

常見錯誤：
1. 忘記 `partial` 關鍵字 → CS0101 重複定義
2. namespace 不同 → 變成不同類別
3. class 修飾詞不同（static vs non-static）→ 編譯錯誤
4. 每個檔案需要各自的 `using` 和 `using static` 宣告

## 行動
1. 新建分割檔案時複製原檔的 namespace 和 class 宣告
2. 確認加上 `partial` 關鍵字
3. 確認 `using` 宣告完整

## 驗證
```bash
dotnet build {CSPROJ_PATH}
```
不應有 CS0101 或 CS0260 錯誤。

## 失敗時
→ build-check (編譯驗證)
→ visibility-upgrade (若 partial 成員存取問題)
