# GSN/Table Mixup (技能查找表混用)

> 來源: CODEX_VERIFY_GUIDE.md#陷阱-Q
> 信心度: VERIFIED
> 前置知識: skill_table 與 archery_table 索引系統
> 相關原子: patterns/skill-lookup, patterns/archery-system
> 觸發條件: ArcheryLearned[] 使用了 SkillLookup 而非 ArcheryLookup 索引

## 知識

本 MUD 有兩套獨立的技能查找系統，各有不同的索引範圍。
混用會導致陣列越界或存取到錯誤的資料。

**兩套系統：**

```
skill_table (技能表):
  索引範圍: 0 ~ 188 (MAX_SKILL - 1)
  查找函式: SkillLookupByGsn(gsn)
  儲存陣列: ch.Learned[0..188]

archery_table (射術表):
  索引範圍: 0 ~ 6
  查找函式: ArcheryLookupByGsn(gsn)
  儲存陣列: ch.ArcheryLearned[0..6]
```

**錯誤案例：**

```csharp
// 錯誤：用 SkillLookupByGsn 去索引 ArcheryLearned
// SkillLookupByGsn 回傳 0~188，但 ArcheryLearned 只有 7 個元素！
int idx = SkillLookupByGsn(gsn);
int level = ch.ArcheryLearned[idx];  // IndexOutOfRangeException!
```

**正確寫法：**
```csharp
// 正確：用 ArcheryLookupByGsn 去索引 ArcheryLearned
int idx = ArcheryLookupByGsn(gsn);
int level = ch.ArcheryLearned[idx];  // idx 在 0~6 範圍內，安全
```

**反向錯誤也可能發生：**
```csharp
// 錯誤：用 ArcheryLookupByGsn 去索引 Learned
int idx = ArcheryLookupByGsn(gsn);
int level = ch.Learned[idx];  // 永遠只取到前 7 個技能
```

**C 原始碼中的對應關係：**
```c
// C 中使用 gsn 直接索引
ch->learned[gsn]           // gsn 是全域技能編號
ch->pcdata->archery[sn]    // sn 是射術專用編號
```

**偵測方法：**
- 搜尋所有 `ArcheryLearned[` 的存取
- 確認索引值來源是 ArcheryLookup 而非 SkillLookup
- 反之亦然：`Learned[` 應用 SkillLookup

## 行動

1. 列出所有 `ArcheryLearned[` 的存取位置
2. 追蹤每個索引值的來源函式
3. 確認使用了正確的 Lookup 函式
4. 同樣檢查 `Learned[` 的索引來源

## 驗證

- 所有 `ArcheryLearned[x]` 的 x 來自 `ArcheryLookupByGsn`
- 所有 `Learned[x]` 的 x 來自 `SkillLookupByGsn` 或合法的 gsn
- 無陣列越界風險

## 失敗時

→ patterns/skill-lookup, patterns/archery-system
