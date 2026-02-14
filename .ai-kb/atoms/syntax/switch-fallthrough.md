# Switch Fall-Through 轉換

> 來源: ACT_WIZ.C, HANDLER.C, 通用 C→C# 規則
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: 無
> 觸發條件: C switch 語句中缺少 break 的 case

## 知識
C 允許 switch case 自動 fall-through（掉落到下一個 case）。
C# **禁止**隱式 fall-through，必須用 `goto case` 明確表示。

C 原始碼（故意 fall-through）：
```c
switch (level) {
    case 5:  bonus += 10;       // fall through
    case 4:  bonus += 8;        // fall through
    case 3:  bonus += 5; break;
    default: bonus = 0; break;
}
```

C# 正確轉換：
```csharp
switch (level) {
    case 5:  bonus += 10; goto case 4;
    case 4:  bonus += 8;  goto case 3;
    case 3:  bonus += 5;  break;
    default: bonus = 0;   break;
}
```

特殊情況 — 空 case 堆疊（C# 允許）：
```c
case 1:
case 2:
case 3:
    do_something(); break;
```
```csharp
// C# 允許空 case 堆疊，不需要 goto
case 1:
case 2:
case 3:
    DoSomething(); break;
```

判斷是否為「故意 fall-through」：
1. 有程式碼但沒有 break/return → 故意 fall-through
2. 有 `/* fall through */` 註解 → 確認故意
3. 空 case 只有標籤 → 堆疊合併，不算 fall-through

## 行動
- 逐一檢查每個 case 是否有 break/return
- 有程式碼無 break → 加 `goto case`
- 空 case 堆疊 → 直接保留

## 驗證
- `dotnet build` 編譯通過（C# 會報錯若漏處理）
- 邏輯路徑與 C 版完全一致

## 失敗時
→ 重新閱讀原始 C switch，逐 case 比對執行路徑
