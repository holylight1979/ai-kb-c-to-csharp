# Formula Simplified Incorrectly (公式簡化錯誤)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-C
> 信心度: VERIFIED
> 前置知識: C 巨集展開規則
> 相關原子: syntax/c-macro-expand, patterns/get-ac-pattern
> 觸發條件: C# 公式結果與 C 公式不同值

## 知識

C MUD 程式碼大量使用巢狀巨集來計算數值。移植時若未完整展開巨集，
容易產生簡化錯誤，導致公式語義改變。

**典型案例：GET_AC 公式**

C 原始碼（巨集展開後）：
```c
// GET_AC(ch) = (ch)->armor - dex_app[(ch)->perm_stat[STAT_DEX]].defensive
// 其中 defensive 包含 con 的修正
// 完整公式: armor - (con - con/5)
```

C# 錯誤移植：
```csharp
// 錯誤：直接用 DexApp 查表取代整個公式
int ac = ch.Armor + Tables.DexApp[ch.GetStat(STAT_DEX)].Defensive;
```

正確移植步驟：
1. 找到 C 巨集定義
2. **逐層展開**，不要跳步
3. 確認每個運算元的來源
4. 保持運算順序與括號

**其他高風險公式：**
- GET_HITROLL / GET_DAMROLL
- URANGE / UMIN / UMAX 巢狀使用
- 經驗值計算（涉及多重條件）
- 傷害骰計算（涉及 number_range）

```c
// 展開範例
#define GET_AC(ch)  ((ch)->armor \
    + (IS_AWAKE(ch) ? dex_app[get_curr_stat(ch,STAT_DEX)].defensive : 0))
// 注意：IS_AWAKE 也是巨集，需要進一步展開
```

## 行動

1. 找到 C 中的巨集定義（通常在 merc.h）
2. 逐步展開每一層巨集，寫下中間結果
3. 將完整展開的公式翻譯為 C#
4. 手動帶入測試數值驗算

## 驗證

- 手動比對每個運算元的來源與計算順序
- 帶入邊界值（0, 1, 最大值）驗算結果是否一致
- 確認括號分組與運算優先序正確

## 失敗時

→ syntax/c-macro-expand, patterns/get-ac-pattern
