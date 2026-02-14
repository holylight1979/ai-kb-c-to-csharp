# Null Terminator 轉換

> 來源: MERC.H, COMM.C, 通用 C→C# 移植慣例
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: atoms/syntax/string-ops.md
> 觸發條件: 看到 C 程式碼中 `arg[0]=='\0'` 或 `*arg=='\0'` 判斷

## 知識
C 字串以 null terminator (`'\0'`) 結尾，判斷空字串的慣用法：
```c
if (arg[0] == '\0')    // 最常見
if (*arg == '\0')      // 指標寫法
if (!*arg)             // 簡寫
```

C# 字串沒有 null terminator，對應寫法：
```csharp
// 方案一：長度檢查（最直接）
if (arg.Length == 0)

// 方案二：IsNullOrEmpty（防禦性，推薦）
if (string.IsNullOrEmpty(arg))

// 方案三：IsNullOrWhiteSpace（若原始碼語意包含空白）
if (string.IsNullOrWhiteSpace(arg))
```

注意：C 中 `arg` 不可能為 NULL 與 `arg[0]=='\0'` 是不同檢查。
若原始碼有 `if (!arg || !*arg)` → C# 用 `string.IsNullOrEmpty(arg)`。

## 行動
- 搜尋所有 `[0] == '\0'`、`*arg == '\0'`、`!*arg` 模式
- 替換為 `string.IsNullOrEmpty()` 或 `.Length == 0`
- 若原始碼確定不會傳入 null，可用 `.Length == 0`

## 驗證
- 編譯通過無警告
- 空字串輸入時行為與 C 版一致
- null 輸入時不拋出 NullReferenceException

## 失敗時
→ atoms/syntax/string-ops.md（字串操作總覽）
