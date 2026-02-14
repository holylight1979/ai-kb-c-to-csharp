# Function Call vs. Direct Assignment

> 來源: audit-findings.md, 移植陷阱分析
> 信心度: VERIFIED
> 前置知識: stub-simplified
> 相關原子: stub-simplified, stub-empty, dispatch-table
> 觸發條件: 將 C 函式呼叫簡化為直接賦值時

## 知識
**這是最危險的移植陷阱之一。**

C 函式呼叫往往不只是簡單的欄位設定，而是包含全域副作用。
直接用賦值替換會導致資料不一致。

危險範例 — `stop_fighting`：
```c
// C 原始碼：遍歷 char_list 清除所有引用
void stop_fighting(CHAR_DATA *ch, bool fBoth)
{
    CHAR_DATA *fch;
    for (fch = char_list; fch; fch = fch->next)
    {
        if (fch == ch || (fBoth && fch->fighting == ch))
        {
            fch->fighting = NULL;
            fch->position = POS_STANDING;
            update_pos(fch);
        }
    }
}
```

錯誤的 C# 簡化：
```csharp
// 只清除自己的 Fighting 欄位，其他角色仍指向 ch！
ch.Fighting = null;
ch.Position = PosStanding;
```

正確的 C# 移植：
```csharp
public static void StopFighting(CharData ch, bool fBoth)
{
    foreach (var fch in DbModule.CharList)
    {
        if (fch == ch || (fBoth && fch.Fighting == ch))
        {
            fch.Fighting = null;
            fch.Position = PosStanding;
            UpdatePos(fch);
        }
    }
}
```

高風險函式清單（常被錯誤簡化）：
- `stop_fighting` → 需遍歷 char_list
- `char_from_room` → 需更新 room 的 people 鏈結
- `extract_char` → 需清理所有全域引用
- `obj_from_char` → 需更新重量鏈
- `affect_remove` → 需還原屬性修正

## 行動
1. 遇到 C 函式呼叫時，先用 `decode-big5` 閱讀完整函式
2. 若函式有 for/while 迴圈遍歷全域列表 → 不可簡化
3. 完整移植函式邏輯，保留所有副作用

## 驗證
比較 C 函式行數與 C# 實作行數。
函式內有 `char_list`/`object_list` 遍歷 → 絕不可簡化為賦值。

## 失敗時
→ decode-big5 (閱讀 C 原始碼)
→ line-count-check (比較行數)
→ stub-simplified (可能是簡化 stub)
