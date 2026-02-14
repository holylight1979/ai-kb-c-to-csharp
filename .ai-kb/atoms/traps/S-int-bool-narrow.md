# Int Narrowed to Bool (int 被窄化為 bool 遺失旗標資訊)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-S
> 信心度: VERIFIED
> 前置知識: C 的 int-as-bool 慣用法
> 相關原子: syntax/c-int-bool, patterns/flag-fields
> 觸發條件: C 中以 int 儲存但用作布林判斷的欄位，被改為 C# bool

## 知識

C 語言沒有原生 bool 型別（C99 之前），很多欄位用 `int` 宣告
但在某些地方當 bool 使用。然而這些 int 欄位實際上可能儲存
大於 1 的值，包含額外的旗標資訊。

**典型案例：**

C 原始碼：
```c
// 宣告為 int
struct char_data {
    int  deaf;        // 看似布林，但值可以是 CHANNEL_* 旗標
    int  comm;        // 通訊旗標，每個位元代表一個頻道
    int  wiznet;      // 巫師網路旗標
};

// 有時當 bool 用
if (ch->deaf)
    send_to_char("你聽不到。\n", ch);

// 但也用 %d 格式顯示數值
sprintf(buf, "deaf 值: %d\n", ch->deaf);  // 可能輸出 5, 12 等
```

**錯誤移植（窄化為 bool）：**
```csharp
public class CharData
{
    public bool Deaf { get; set; }     // 遺失旗標資訊！
    public bool Comm { get; set; }     // 嚴重錯誤
    public bool Wiznet { get; set; }   // 嚴重錯誤
}
```

**正確移植：**
```csharp
public class CharData
{
    public int Deaf { get; set; }      // 保持 int，保留旗標
    public int Comm { get; set; }      // 可以做位元運算
    public int Wiznet { get; set; }    // 可以做位元運算
}
```

**如何判斷是否安全窄化：**

可以安全改 bool 的條件（全部滿足才行）：
1. C 中只賦值 0 或 1（TRUE/FALSE）
2. 從不用 `%d` 格式印出
3. 從不做位元運算（`&`, `|`, `^`）
4. 從不與其他數值比較（`== 2`, `> 1` 等）

**偵測線索：**
```c
// 線索 1: 用 %d 格式 → 值可以 > 1
sprintf(buf, "%d", ch->deaf);

// 線索 2: 位元運算 → 是旗標欄位
if (ch->comm & COMM_NOSHOUT)

// 線索 3: 賦值非 0/1 → 不是純 bool
ch->deaf = CHANNEL_GOSSIP | CHANNEL_AUCTION;
```

## 行動

1. 列出所有 C 中宣告為 int 但 C# 改為 bool 的欄位
2. 在 C 原始碼中搜尋每個欄位的所有使用位置
3. 檢查是否有 `%d` 格式、位元運算、或非 0/1 賦值
4. 將不安全的窄化還原為 int

## 驗證

- 比對 C 與 C# 的欄位型別
- 確認所有 `%d` 格式對應的欄位保持 int
- 確認所有位元運算的欄位保持 int
- 比對值的範圍是否一致

## 失敗時

→ syntax/c-int-bool, patterns/flag-fields
