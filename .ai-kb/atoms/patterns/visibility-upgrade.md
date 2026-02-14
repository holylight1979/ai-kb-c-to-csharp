# Visibility Upgrade Pattern

> 來源: 編譯錯誤分析, CS0122 修復經驗
> 信心度: VERIFIED
> 前置知識: partial-class
> 相關原子: using-static-import, partial-class
> 觸發條件: CS0122 "XXX is inaccessible due to its protection level"

## 知識
跨模組存取需要適當的可見性。C 沒有存取修飾詞，所有函式預設全域可見。
移植到 C# 時，預設可能設為 `private`，導致其他模組無法存取。

常見情境：
```csharp
// DbModule 中定義為 private
private static List<CharData> charList = new();

// CommModule 嘗試存取 → CS0122
foreach (var ch in DbModule.charList)  // 錯誤！
```

修復方式：
```csharp
// 改為 public 或 internal
public static List<CharData> charList = new();
```

判斷使用 public 或 internal：
- `public`: 可能被外部組件引用（通常用此）
- `internal`: 只在同一個 assembly 內使用

partial class 特殊情況：
- 同一個 partial class 的不同檔案共享 private 成員
- CS0122 出現在 partial class 成員間 → 檢查 class 名稱是否一致
- 常見錯誤：忘記加 `partial` 關鍵字，導致變成不同 class

批次修復：
```csharp
// 欄位、方法都可能需要升級
private int level;          → public int level;
private void Reset() { }   → public void Reset() { }
private const int MAX = 10; → public const int MAX = 10;
```

## 行動
1. 確認 CS0122 報錯的成員名稱和所在類別
2. 找到該成員的定義位置
3. 將 `private` 改為 `public`（或 `internal`）
4. 重新編譯確認

## 驗證
```bash
dotnet build {CSPROJ_PATH}
```
CS0122 錯誤應消失。

## 失敗時
→ build-check (重新編譯)
→ partial-class (確認是否為 partial class 問題)
