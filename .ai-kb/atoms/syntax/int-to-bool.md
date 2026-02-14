# Int 轉 Bool 判斷

> 來源: MERC.H 結構定義，全專案欄位型別決策
> 信心度: VERIFIED
> 前置知識: 無
> 相關原子: atoms/syntax/macro-to-method.md
> 觸發條件: 決定 C 的 int/short 欄位在 C# 中應為 int 或 bool

## 知識
C 沒有原生 bool 型別，常用 int 代替。移植時必須判斷真正語意。

### 判斷標準
**可以轉 bool 的情況**：
- 只賦值 0 或 1（TRUE/FALSE）
- 只用於 `if (field)` / `if (!field)` 判斷
- 語意為「是/否」（如 `is_npc`、`is_valid`）

**必須保留 int 的情況**：
- 賦值 >1 的數字（如計數器）
- 用 `%d` 格式印出
- 參與數學運算（加減乘除）
- 用作索引或陣列下標

### 常見陷阱
```c
// C: looks like bool but is actually a counter
ch->daze = 2;         // daze rounds remaining
if (ch->daze > 0)     // 倒數計時，不是 bool
ch->daze--;

// C: truly a flag
ch->is_valid = TRUE;  // 只有 TRUE/FALSE → bool ok
```

### 安全做法
```csharp
// 不確定時，先保留 int
public int Daze { get; set; }

// 確認只有 0/1 後再改 bool
public bool IsValid { get; set; }
```

### 搜尋策略
```
1. grep 所有對該欄位的賦值：找出所有可能的值
2. grep 所有對該欄位的使用：確認是否參與運算
3. 若有 %d 印出 → 保留 int
4. 若有 > 1 的值 → 保留 int
```

## 行動
- 對每個疑似 bool 欄位，搜尋全部賦值與使用
- 只在確認只用 0/1 且無數學運算時才轉 bool
- 不確定時保留 int（安全第一）

## 驗證
- 轉 bool 後編譯通過
- 無 `int → bool` 隱式轉換錯誤
- 原始邏輯行為完全保留

## 失敗時
→ 回退為 int，加 TODO 註解標記待確認
