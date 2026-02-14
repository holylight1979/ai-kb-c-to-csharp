# Nested If Flattened (巢狀 if 被攤平為平行 if)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-K
> 信心度: VERIFIED
> 前置知識: C 大括號與縮排對應
> 相關原子: syntax/c-brace-matching, verification/indentation-check
> 觸發條件: C 中巢狀的 if-else 在 C# 中變成同層級的平行 if

## 知識

C MUD 程式碼的縮排風格不一致，加上大量巢狀條件，容易在移植時
將內層 if 誤認為與外層同級，改變條件的依賴關係。

**典型案例：**

C 原始碼（巢狀結構）：
```c
if (IS_NPC(ch))
{
    if (ch->level > 10)
    {
        // 只有 NPC 且等級 > 10 才執行
        do_special_attack(ch);
    }
    else
    {
        // NPC 但等級 <= 10
        do_normal_attack(ch);
    }
}
else
{
    // 非 NPC（玩家）
    do_player_attack(ch);
}
```

錯誤移植（攤平為平行 if）：
```csharp
if (ch.IsNpc())
{
    // ...
}
// 錯誤：這個 if 不再是巢狀在 IsNpc 內
if (ch.Level > 10)
{
    DoSpecialAttack(ch);  // 玩家等級 > 10 也會執行！
}
else
{
    DoNormalAttack(ch);   // 邏輯完全改變
}
```

**為什麼容易出錯：**
- C 原始碼縮排可能用 tab 混 space
- 大括號可能在同一行或下一行，風格不一致
- 深層巢狀（4-5 層）難以目視追蹤
- AI 模型處理長函式時容易丟失巢狀層級

**偵測方法：**
- 比對 C 與 C# 的縮排層級數
- 數大括號的開合配對
- 特別注意 `else` 與哪個 `if` 配對

## 行動

1. 在 C 原始碼中標記每個 `{` 的巢狀層級
2. 在 C# 中做同樣的標記
3. 比對每個 if/else 的層級是否一致
4. 修正所有層級不符的條件

## 驗證

- 比對 C 與 C# 的最大縮排深度
- 確認 else 分支與正確的 if 配對
- 用邊界條件測試邏輯路徑

## 失敗時

→ syntax/c-brace-matching, verification/indentation-check
