# Function Pointer Dispatch Pattern

> 來源: MERC.H 審計, spec_fun/spell_fun/attack_fun 架構
> 信心度: VERIFIED
> 前置知識: partial-class
> 相關原子: function-call-vs-assign, stub-simplified
> 觸發條件: 移植含有函式指標的 C 結構時

## 知識
C 使用函式指標儲存回呼，C# 改用字串名稱 + 執行時期分派。

C 原始碼：
```c
struct mob_index_data {
    SPEC_FUN *spec_fun;    // 函式指標
};
// 設定方式
pMob->spec_fun = spec_cast_mage;
// 呼叫方式
if (ch->spec_fun && (*ch->spec_fun)(ch))
    continue;
```

C# 移植：
```csharp
public class MobIndexData {
    public string SpecFun;  // 儲存函式名稱字串
}

// 分派表（Dictionary）
private static readonly Dictionary<string, Func<CharData, bool>> SpecTable
    = new()
{
    ["spec_cast_mage"] = SpecCastMage,
    ["spec_cast_cleric"] = SpecCastCleric,
    ["spec_breath_any"] = SpecBreathAny,
    // 必須註冊所有 entry
};

// 呼叫方式
if (ch.MobIndex.SpecFun != null
    && SpecTable.TryGetValue(ch.MobIndex.SpecFun, out var fn))
{
    if (fn(ch)) continue;
}
```

關鍵：必須在表中註冊每一個函式。遺漏 = silent failure。
三種主要分派表：spec_fun、spell_fun、attack_fun。

## 行動
1. 列出 C 中所有用到的 spec/spell/attack 函式
2. 確認 C# 分派表已註冊全部項目
3. 確認每個註冊的方法都有實作（非 stub）

## 驗證
比對 C 的函式指標賦值處與 C# 分派表條目數量。
缺少的 entry 會導致 runtime 時 `TryGetValue` 失敗。

## 失敗時
→ stub-scan (確認對應方法已實作)
→ grep-existing (搜尋已有的分派表)
